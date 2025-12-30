"""
Main pipeline orchestrator - ties all components together.
"""

import os
import json
from pathlib import Path
from PIL import Image
from typing import Dict, List
from datetime import datetime

from .models import CampaignBrief, BrandConfig
from .background_generator import generate_background
from .compositor import composite_product_on_background
from .aspect_ratios import resize_and_crop, ASPECT_RATIOS
from .brand_overlay import apply_brand_overlay


# Product scale and position settings per aspect ratio
# scale = max width as % of image width
# max_height = max height as % of image height (prevents tall products from dominating)
PRODUCT_SETTINGS = {
    "1x1": {"scale": 0.55, "max_height": 0.50, "position": "center"},
    "9x16": {
        "scale": 0.75,
        "max_height": 0.40,
        "position": "center",
    },  # Tighter height for vertical
    "16x9": {"scale": 0.50, "max_height": 0.65, "position": "center"},
}


def load_campaign_brief(brief_path: str) -> CampaignBrief:
    """Load and validate a campaign brief from JSON."""
    with open(brief_path, "r") as f:
        data = json.load(f)
    return CampaignBrief(**data)


def load_brand_config(config_path: str) -> BrandConfig:
    """Load and validate brand configuration from JSON."""
    with open(config_path, "r") as f:
        data = json.load(f)
    return BrandConfig(**data)


def generate_campaign_creatives(
    brief: CampaignBrief,
    brand_config: BrandConfig,
    output_dir: str = "output",
    progress_callback=None,
) -> Dict[str, List[str]]:
    """
    Generate all campaign creatives for all products and aspect ratios.

    Args:
        brief: Campaign brief
        brand_config: Brand configuration
        output_dir: Output directory path
        progress_callback: Optional callback for progress updates (message, percent)

    Returns:
        Dictionary mapping product IDs to lists of generated file paths
    """
    results = {}

    # Create output directory structure
    campaign_slug = brief.campaign_name.lower().replace(" ", "-")
    region_slug = brief.target_region.lower().replace(" ", "_")
    campaign_dir = Path(output_dir) / f"{campaign_slug}_{region_slug}"
    campaign_dir.mkdir(parents=True, exist_ok=True)

    total_steps = len(brief.products) * (
        1 + len(ASPECT_RATIOS)
    )  # bg gen + ratios per product
    current_step = 0

    def update_progress(message: str):
        nonlocal current_step
        current_step += 1
        if progress_callback:
            progress_callback(message, current_step / total_steps)

    for product in brief.products:
        product_results = []
        product_dir = campaign_dir / product.id
        product_dir.mkdir(exist_ok=True)

        # Generate background for this product
        update_progress(
            f"Generating {brief.target_region} background for {product.name}..."
        )
        background = generate_background(brief.target_region)

        # Load product image
        product_image = Image.open(product.product_image)

        # Generate each aspect ratio with appropriate product scaling
        for ratio_name, ratio_config in ASPECT_RATIOS.items():
            update_progress(f"Creating {ratio_name} for {product.name}...")

            # First, crop background to target aspect ratio
            cropped_bg = resize_and_crop(
                background, ratio_config.width, ratio_config.height, focus="center"
            )

            # Get the appropriate product settings for this aspect ratio
            settings = PRODUCT_SETTINGS.get(
                ratio_name,
                {"scale": 0.40, "max_height": 0.50, "position": "center"},
            )

            # Composite product onto the cropped background
            composited = composite_product_on_background(
                background=cropped_bg,
                product=product_image,
                position=settings["position"],
                product_scale=settings["scale"],
                max_height_percent=settings["max_height"],
            )

            # Apply brand overlay
            final_image = apply_brand_overlay(
                image=composited,
                campaign_message=brief.campaign_message,
                brand_config=brand_config,
                aspect_ratio=ratio_name,
            )

            # Save
            output_path = product_dir / f"{ratio_name}.png"
            final_image.convert("RGB").save(output_path, "PNG")
            product_results.append(str(output_path))

        results[product.id] = product_results

    # Save generation log
    log_data = {
        "campaign_name": brief.campaign_name,
        "region": brief.target_region,
        "generated_at": datetime.now().isoformat(),
        "products": [p.id for p in brief.products],
        "aspect_ratios": list(ASPECT_RATIOS.keys()),
        "files": results,
    }

    log_path = campaign_dir / "generation_log.json"
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)

    return results
