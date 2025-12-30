"""
Iron Leaf Creative Automation Pipeline - Streamlit UI

A proof-of-concept tool for generating social ad creatives
with consistent branding across multiple aspect ratios.
"""

import streamlit as st
import json
import os
import zipfile
from io import BytesIO
from pathlib import Path
from PIL import Image

from pipeline.models import CampaignBrief, BrandConfig
from pipeline.generator import generate_campaign_creatives, load_brand_config
from pipeline.background_generator import get_available_regions
from pipeline.aspect_ratios import get_aspect_ratio_info

# Page config
st.set_page_config(
    page_title="Iron Leaf Creative Automation", page_icon="🍃", layout="wide"
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .stApp {
        background-color: #1a1a1a;
    }
    .main-header {
        color: #5C4033;
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 0;
    }
    .sub-header {
        color: #5C4033;
        font-size: 2.1rem;
        margin-top: 0;
        opacity: 0.8;
    }
    .product-card {
        background-color: #2d2d2d;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stMainBlockContainer {
        background-color: #fff;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown(
    '<p class="main-header">🍃 Iron Leaf Creative Automation</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Generate consistent social ad creatives across multiple formats</p>',
    unsafe_allow_html=True,
)
st.divider()

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Brand config
    brand_config_path = st.text_input(
        "Brand Config Path",
        value="brand_config.json",
        help="Path to brand configuration JSON file",
    )

    # Load brand config
    try:
        brand_config = load_brand_config(brand_config_path)
        st.success(f"✓ Loaded {brand_config.brand_name} brand config")
    except Exception as e:
        st.error(f"Error loading brand config: {e}")
        brand_config = None

    st.divider()

    # Available regions
    st.subheader("Available Regions")
    regions = get_available_regions()
    for region in regions:
        st.text(f"• {region.replace('_', ' ').title()}")

    st.divider()

    # Aspect ratio info
    st.subheader("Output Formats")
    for name, config in get_aspect_ratio_info().items():
        st.text(f"• {name}: {config.width}x{config.height}")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Campaign Brief")

    # Option to upload or use example
    brief_source = st.radio(
        "Brief Source", ["Use Example", "Upload JSON", "Create New"], horizontal=True
    )

    if brief_source == "Use Example":
        example_path = "examples/campaign_brief.json"
        if os.path.exists(example_path):
            with open(example_path, "r") as f:
                brief_data = json.load(f)
            st.json(brief_data)
        else:
            st.warning("Example brief not found. Please upload a brief.")
            brief_data = None

    elif brief_source == "Upload JSON":
        uploaded_file = st.file_uploader("Upload Campaign Brief", type=["json"])
        if uploaded_file:
            brief_data = json.load(uploaded_file)
            st.json(brief_data)
        else:
            brief_data = None

    else:  # Create New
        st.subheader("Create Campaign Brief")

        campaign_name = st.text_input("Campaign Name", value="Trail Season 2026")
        target_region = st.selectbox("Target Region", get_available_regions())
        target_audience = st.text_input(
            "Target Audience", value="Outdoor enthusiasts aged 25-45"
        )
        campaign_message = st.text_input(
            "Campaign Message", value="Conquer Every Trail"
        )

        # Products
        st.subheader("Products")

        # Find available product images
        products_dir = Path("assets/products")
        product_images = (
            list(products_dir.glob("*.png")) if products_dir.exists() else []
        )

        products = []
        for i, img_path in enumerate(product_images):
            # Try to find matching product name from example brief if it exists
            default_name = img_path.stem.replace("-", " ").title()
            default_desc = f"Premium {img_path.stem}"

            # Check if example brief exists and has matching product
            example_path = "examples/campaign_brief.json"
            if os.path.exists(example_path):
                try:
                    with open(example_path, "r") as f:
                        example_brief = json.load(f)
                        # Try to match by image filename
                        for prod in example_brief.get("products", []):
                            if prod.get("product_image", "").endswith(img_path.name):
                                default_name = prod.get("name", default_name)
                                default_desc = prod.get("description", default_desc)
                                break
                except:
                    pass  # If example brief can't be loaded, use defaults

            # Use product name for expander title if it's not just the filename
            display_name = (
                default_name
                if default_name != img_path.stem.replace("-", " ").title()
                else img_path.stem
            )
            with st.expander(f"Product {i+1}: {display_name}"):
                name = st.text_input(
                    f"Name",
                    value=default_name,
                    key=f"name_{i}",
                )
                desc = st.text_input(
                    f"Description",
                    value=default_desc,
                    key=f"desc_{i}",
                )
                products.append(
                    {
                        "id": img_path.stem,
                        "name": name,
                        "description": desc,
                        "product_image": str(img_path),
                    }
                )

        if products:
            brief_data = {
                "campaign_name": campaign_name,
                "products": products,
                "target_region": target_region,
                "target_audience": target_audience,
                "campaign_message": campaign_message,
            }
        else:
            st.warning("No product images found in assets/products/ folder")
            brief_data = None

with col2:
    st.header("Product Preview")

    if brief_data and "products" in brief_data:
        preview_cols = st.columns(len(brief_data["products"]))
        for i, product in enumerate(brief_data["products"]):
            with preview_cols[i]:
                if os.path.exists(product["product_image"]):
                    img = Image.open(product["product_image"])
                    st.image(img, caption=product["name"], width="stretch")
                else:
                    st.warning(f"Image not found: {product['product_image']}")

st.divider()

# Generation section
st.header("Generate Creatives")

if brief_data and brand_config:
    if st.button("Generate Campaign Creatives", type="primary", width="stretch"):
        try:
            # Validate brief
            brief = CampaignBrief(**brief_data)

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(message, percent):
                progress_bar.progress(percent)
                status_text.text(message)

            # Generate!
            with st.spinner("Generating creatives..."):
                results = generate_campaign_creatives(
                    brief=brief,
                    brand_config=brand_config,
                    output_dir="output",
                    progress_callback=update_progress,
                )

            progress_bar.progress(1.0)
            status_text.text("✅ Generation complete!")

            st.success(f"Generated {sum(len(v) for v in results.values())} creatives!")

            # Display results
            st.header("📸 Generated Creatives")

            # Create a mapping from product_id to product name
            product_name_map = {p.id: p.name for p in brief.products}

            for product_id, file_paths in results.items():
                # Use product name from the products array, fallback to formatted product_id
                product_name = product_name_map.get(
                    product_id, product_id.replace("-", " ").title()
                )
                st.subheader(product_name)

                cols = st.columns(3)
                for i, path in enumerate(file_paths):
                    with cols[i % 3]:
                        if os.path.exists(path):
                            img = Image.open(path)
                            ratio_name = Path(path).stem
                            st.image(img, caption=ratio_name, width="stretch")

            # Download ZIP
            st.divider()
            st.subheader("📦 Download All")

            # Create ZIP in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for product_id, file_paths in results.items():
                    for path in file_paths:
                        if os.path.exists(path):
                            arcname = f"{product_id}/{Path(path).name}"
                            zip_file.write(path, arcname)

            zip_buffer.seek(0)

            st.download_button(
                label="⬇️ Download All Creatives (ZIP)",
                data=zip_buffer,
                file_name=f"{brief.campaign_name.lower().replace(' ', '_')}_creatives.zip",
                mime="application/zip",
                width="stretch",
            )

        except Exception as e:
            st.error(f"Error generating creatives: {e}")
            st.exception(e)
else:
    if not brief_data:
        st.warning("Please provide a campaign brief above.")
    if not brand_config:
        st.warning("Please configure brand settings in the sidebar.")

# Footer
st.divider()
st.caption(
    "Iron Leaf Creative Automation Pipeline • Built for Adobe FDE Take-Home Exercise"
)
