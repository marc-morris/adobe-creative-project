"""
Product compositing - places product PNGs onto backgrounds.
"""

from PIL import Image


def composite_product_on_background(
    background: Image.Image,
    product: Image.Image,
    position: str = "center",
    product_scale: float = 0.5,
    max_height_percent: float = 0.50,
) -> Image.Image:
    """
    Composite a product image onto a background.

    Args:
        background: Background image
        product: Product image with transparent background (shadows should be baked into the PNG)
        position: Where to place product ("center-bottom", "center", "left", "right")
        product_scale: Scale factor for product relative to background width
        max_height_percent: Maximum height as percentage of background (prevents tall products from dominating)

    Returns:
        Composited image
    """
    # Work on a copy
    result = background.copy().convert("RGBA")

    # Ensure product has alpha
    if product.mode != "RGBA":
        product = product.convert("RGBA")

    # Calculate scale based on width
    target_width = int(result.width * product_scale)
    scale_ratio = target_width / product.width
    target_height = int(product.height * scale_ratio)

    # Check if height exceeds maximum allowed
    max_height = int(result.height * max_height_percent)
    if target_height > max_height:
        # Scale down to fit within height constraint
        scale_ratio = max_height / product.height
        target_height = max_height
        target_width = int(product.width * scale_ratio)

    product_scaled = product.resize(
        (target_width, target_height), Image.Resampling.LANCZOS
    )

    # Calculate position
    if position == "center-bottom":
        x = (result.width - product_scaled.width) // 2
        y = (
            result.height - product_scaled.height - int(result.height * 0.08)
        )  # 8% from bottom
    elif position == "center":
        x = (result.width - product_scaled.width) // 2
        y = (result.height - product_scaled.height) // 2
    elif position == "left":
        x = int(result.width * 0.1)
        y = result.height - product_scaled.height - int(result.height * 0.08)
    elif position == "right":
        x = result.width - product_scaled.width - int(result.width * 0.1)
        y = result.height - product_scaled.height - int(result.height * 0.08)
    else:
        x = (result.width - product_scaled.width) // 2
        y = (result.height - product_scaled.height) // 2

    # Paste product (shadow is already baked into the PNG)
    result.paste(product_scaled, (x, y), product_scaled)

    return result
