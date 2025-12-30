"""
Aspect ratio resizing and cropping for different ad formats.
"""

from PIL import Image
from typing import Tuple, Dict
from dataclasses import dataclass


@dataclass
class AspectRatioConfig:
    """Configuration for an aspect ratio."""

    name: str
    width: int
    height: int
    use_case: str


# Standard social media aspect ratios
ASPECT_RATIOS: Dict[str, AspectRatioConfig] = {
    "1x1": AspectRatioConfig(
        name="1x1", width=1080, height=1080, use_case="Instagram Feed, Facebook"
    ),
    "9x16": AspectRatioConfig(
        name="9x16",
        width=1080,
        height=1920,
        use_case="Instagram Stories, TikTok, Reels",
    ),
    "16x9": AspectRatioConfig(
        name="16x9", width=1920, height=1080, use_case="YouTube, Web Banners"
    ),
}


def resize_and_crop(
    image: Image.Image, target_width: int, target_height: int, focus: str = "center"
) -> Image.Image:
    """
    Resize and crop image to target dimensions, maintaining aspect ratio.
    Uses "cover" strategy - scales to fill entire target area, then crops excess.

    Args:
        image: Source image
        target_width: Target width in pixels
        target_height: Target height in pixels
        focus: Where to focus the crop ("center", "top", "bottom")

    Returns:
        Resized and cropped image at exactly target_width x target_height
    """
    # Calculate scaling to COVER target dimensions (fill completely, crop excess)
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # Image is wider than target - scale by height to fill, will crop width
        new_height = target_height
        new_width = int(image.width * (target_height / image.height))
    else:
        # Image is taller/narrower than target - scale by width to fill, will crop height
        new_width = target_width
        new_height = int(image.height * (target_width / image.width))

    # Resize to cover dimensions
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate crop box to get exact target dimensions
    if new_width >= target_width:
        # Crop horizontally (center)
        left = (new_width - target_width) // 2
        right = left + target_width
    else:
        # This shouldn't happen with cover logic, but handle it
        left = 0
        right = new_width

    if new_height >= target_height:
        # Crop vertically based on focus
        if focus == "top":
            top = 0
            bottom = target_height
        elif focus == "bottom":
            top = new_height - target_height
            bottom = new_height
        else:  # center
            top = (new_height - target_height) // 2
            bottom = top + target_height
    else:
        # This shouldn't happen with cover logic, but handle it
        top = 0
        bottom = new_height

    cropped = resized.crop((left, top, right, bottom))
    return cropped


def generate_all_aspect_ratios(
    image: Image.Image, focus: str = "center"
) -> Dict[str, Image.Image]:
    """
    Generate all standard aspect ratio versions of an image.

    Args:
        image: Source image (should be high resolution)
        focus: Where to focus crops ("center", "top", "bottom")

    Returns:
        Dictionary mapping ratio names to cropped images
    """
    results = {}

    for ratio_name, config in ASPECT_RATIOS.items():
        results[ratio_name] = resize_and_crop(
            image, config.width, config.height, focus=focus
        )

    return results


def get_aspect_ratio_info() -> Dict[str, AspectRatioConfig]:
    """Return info about available aspect ratios."""
    return ASPECT_RATIOS
