"""
Brand overlay - adds campaign text and logo to images.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
from .models import BrandConfig


def get_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    """
    Load a font, falling back to default if not found.

    Args:
        font_name: Name of the font (e.g., "Oswald-Bold")
        size: Font size in pixels

    Returns:
        PIL ImageFont object
    """
    # Common font paths to check
    font_paths = [
        f"/System/Library/Fonts/{font_name}.ttf",
        f"/System/Library/Fonts/Supplemental/{font_name}.ttf",
        f"/Library/Fonts/{font_name}.ttf",
        f"/Library/Fonts/{font_name}.otf",
        f"~/.fonts/{font_name}.ttf",
        f"fonts/{font_name}.ttf",
        f"{font_name}.ttf",
    ]

    # Try bold system fonts for impact
    font_variations = [
        font_name,
        font_name.replace("-", " "),
        "Impact",  # Great for headlines
        "Arial Bold",
        "Helvetica Bold",
        "Arial Black",
        "Futura Bold",
        "Futura-Bold",
        "Helvetica Neue Bold",
        "Oswald-Bold",
        "Oswald",
    ]

    for font_var in font_variations:
        for path_template in font_paths:
            path = os.path.expanduser(path_template.replace(font_name, font_var))
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue

    # Try system font collection files (Mac)
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", size)
    except:
        pass

    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except:
        pass

    return ImageFont.load_default()


def wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw
) -> list[str]:
    """
    Wrap text to fit within a maximum width.

    Args:
        text: Text to wrap
        font: Font to use for measuring
        max_width: Maximum width in pixels
        draw: ImageDraw object for measuring text

    Returns:
        List of lines
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Try adding this word to the current line
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]

        if test_width <= max_width:
            current_line.append(word)
        else:
            # Current line is full, start a new line
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    # Don't forget the last line
    if current_line:
        lines.append(" ".join(current_line))

    return lines if lines else [text]


def add_text_with_background(
    image: Image.Image,
    text: str,
    position: str,
    font: ImageFont.FreeTypeFont,
    text_color: str,
    bg_color: str,
    bg_opacity: float,
    margin_percent: float,
    max_width_percent: float = 70.0,
) -> Image.Image:
    """
    Add text with a semi-transparent background pill, wrapping to multiple lines if needed.

    Args:
        image: Image to draw on
        text: Text to display
        position: Position ("top-left", "top-center", "bottom-left", etc.)
        font: PIL ImageFont object
        text_color: Hex color for text
        bg_color: Hex color for background
        bg_opacity: Background opacity (0-1)
        margin_percent: Margin from edges as percentage of image size
        max_width_percent: Maximum width of text box as percentage of image width

    Returns:
        Image with text overlay
    """
    result = image.copy().convert("RGBA")

    # Create overlay for semi-transparent background
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Calculate maximum allowed width for text
    margin_x = int(result.width * margin_percent / 100)
    margin_y = int(result.height * margin_percent / 100)
    max_text_width = int(result.width * max_width_percent / 100)

    # Wrap text to multiple lines if needed
    lines = wrap_text(text, font, max_text_width, draw)

    # Calculate dimensions for each line and find the widest
    line_heights = []
    line_widths = []
    for line in lines:
        # Get the actual rendered size using textlength for width
        line_width = draw.textlength(line, font=font)
        line_widths.append(int(line_width))
        # For height, use a sample character to get consistent line height
        bbox = draw.textbbox(
            (0, 0), "Ag", font=font
        )  # Use chars with ascender/descender
        line_heights.append(bbox[3] - bbox[1])

    max_line_width = max(line_widths)
    line_height = max(line_heights) if line_heights else 50
    line_spacing = int(line_height * 0.2)  # 20% spacing between lines
    total_text_height = (line_height * len(lines)) + (line_spacing * (len(lines) - 1))

    # Padding around text - equal top and bottom padding
    padding_x = int(line_height * 0.4)
    padding_y = int(line_height * 0.3)  # Equal padding for top and bottom

    # Calculate total box dimensions
    total_box_width = max_line_width + padding_x * 2
    total_box_height = total_text_height + padding_y * 2

    # Calculate position
    if "left" in position:
        x = margin_x
    elif "right" in position:
        x = result.width - total_box_width - margin_x
    else:  # center
        x = (result.width - total_box_width) // 2

    # Ensure x stays within bounds
    x = max(margin_x, min(x, result.width - total_box_width - margin_x))

    if "top" in position:
        y = margin_y
    elif "bottom" in position:
        y = result.height - total_box_height - margin_y
    else:  # center
        y = (result.height - total_box_height) // 2

    # Draw background pill
    bg_rgb = tuple(int(bg_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    bg_rgba = (*bg_rgb, int(255 * bg_opacity))

    pill_bbox = [x, y, x + total_box_width, y + total_box_height]

    # Draw rounded rectangle
    radius = int(line_height * 0.25)
    draw.rounded_rectangle(pill_bbox, radius=radius, fill=bg_rgba)

    # Composite overlay
    result = Image.alpha_composite(result, overlay)

    # Draw each line of text
    draw = ImageDraw.Draw(result)
    text_rgb = tuple(int(text_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))

    # Calculate starting y position - center text vertically in the pill
    # Get the bounding box of the first line to find where to start
    first_line_bbox = draw.textbbox((0, 0), lines[0], font=font)
    first_line_height = first_line_bbox[3] - first_line_bbox[1]

    # Start y position: top of box + padding + (line_height - first_line_height) / 2
    # This centers the first line's bounding box within its allocated space
    current_y = y + padding_y + (line_height - first_line_height) // 2

    for i, line in enumerate(lines):
        # Center each line within the box
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = x + padding_x + (max_line_width - line_width) // 2  # Center align

        draw.text((line_x, current_y), line, font=font, fill=(*text_rgb, 255))
        current_y += line_height + line_spacing

    return result


def add_logo(
    image: Image.Image,
    logo_path: str,
    position: str,
    max_width_percent: float,
    margin_percent: float,
) -> Image.Image:
    """
    Add logo to image at specified position.

    Args:
        image: Image to add logo to
        logo_path: Path to logo image
        position: Position ("bottom-right", "bottom-left", "top-right", "top-left")
        max_width_percent: Maximum logo width as percentage of image width
        margin_percent: Margin from edges as percentage

    Returns:
        Image with logo overlay
    """
    result = image.copy().convert("RGBA")

    # Load logo
    logo = Image.open(logo_path).convert("RGBA")

    # Scale logo
    max_width = int(result.width * max_width_percent / 100)
    if logo.width > max_width:
        scale = max_width / logo.width
        new_height = int(logo.height * scale)
        logo = logo.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Calculate position
    margin_x = int(result.width * margin_percent / 100)
    margin_y = int(result.height * margin_percent / 100)

    if "left" in position:
        x = margin_x
    else:  # right
        x = result.width - logo.width - margin_x

    if "top" in position:
        y = margin_y
    else:  # bottom
        y = result.height - logo.height - margin_y

    # Paste logo
    result.paste(logo, (x, y), logo)

    return result


def add_cta_button(
    image: Image.Image,
    button_image_path: str,
    max_width_percent: float = 45.0,
    spacing_below_product: float = 0.03,
) -> Image.Image:
    """
    Add a call-to-action button directly below the product (centered horizontally).

    Args:
        image: Image to add button to
        button_image_path: Path to button PNG image
        max_width_percent: Maximum button width as percentage of image width
        spacing_below_product: Spacing below product as percentage of image height

    Returns:
        Image with CTA button added
    """
    result = image.copy().convert("RGBA")

    # Load button image
    if not os.path.exists(button_image_path):
        print(
            f"Warning: Button image not found at {button_image_path}, skipping button"
        )
        return result

    button = Image.open(button_image_path).convert("RGBA")

    # Scale button to fit within max width while maintaining aspect ratio
    max_width = int(result.width * max_width_percent / 100)
    if button.width > max_width:
        scale = max_width / button.width
        new_height = int(button.height * scale)
        button = button.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Position - centered horizontally, directly below centered product
    # Products are centered vertically, so calculate where product bottom would be
    # For centered products with typical heights (40-65% of image), bottom is around 70-82% from top
    # Use 70% as a good estimate for most cases, then add spacing
    product_bottom_estimate = int(
        result.height * 0.70
    )  # Estimate where product bottom is
    spacing = int(result.height * spacing_below_product)
    y = product_bottom_estimate + spacing
    x = (result.width - button.width) // 2

    # Make sure button doesn't go off bottom of image (leave 5% margin)
    max_y = result.height - int(result.height * 0.05) - button.height
    if y > max_y:
        y = max_y

    # Paste button
    result.paste(button, (x, y), button)

    return result


# Logo size per aspect ratio (as percentage of image width)
LOGO_SIZES = {
    "1x1": 20.0,  # Square
    "9x16": 20.0,  # Portrait
    "16x9": 15.0,  # Landscape
}

# CTA button size per aspect ratio (as percentage of image width)
CTA_BUTTON_SIZES = {
    "1x1": 45.0,  # Square
    "9x16": 55.0,  # Portrait - larger for better visibility
    "16x9": 40.0,  # Landscape
}


def apply_brand_overlay(
    image: Image.Image,
    campaign_message: str,
    brand_config: BrandConfig,
    aspect_ratio: str = "1x1",
) -> Image.Image:
    """
    Apply complete brand overlay (text + logo + CTA button) to an image.

    Args:
        image: Base image
        campaign_message: Campaign message text
        brand_config: Brand configuration
        aspect_ratio: Aspect ratio name (1x1, 9x16, 16x9) for size-specific rules

    Returns:
        Image with brand overlay applied
    """
    layout = brand_config.layout_rules

    # Determine font size based on image dimensions - slightly smaller
    font_size = int(min(image.width, image.height) * 0.065)
    font = get_font(brand_config.typography.get("headline_font", "Arial"), font_size)

    # Add text
    result = add_text_with_background(
        image=image,
        text=campaign_message.upper(),  # Outdoor brands often use uppercase
        position=layout.text_position,
        font=font,
        text_color=brand_config.colors.get("text_light", "#FFFFFF"),
        bg_color=brand_config.colors.get("secondary", "#000000"),
        bg_opacity=layout.text_background_opacity,
        margin_percent=layout.safe_margin_percent,
    )

    # Add CTA button (below product) with aspect-ratio-specific size
    button_path = "assets/cta-button.png"  # Path to your button PNG
    button_size = CTA_BUTTON_SIZES.get(aspect_ratio, 45.0)
    result = add_cta_button(
        image=result,
        button_image_path=button_path,
        max_width_percent=button_size,
        spacing_below_product=0.03,
    )

    # Add logo with aspect-ratio-specific size
    logo_path = brand_config.logos.get("primary")
    if logo_path and os.path.exists(logo_path):
        logo_size = LOGO_SIZES.get(aspect_ratio, layout.logo_max_width_percent)
        result = add_logo(
            image=result,
            logo_path=logo_path,
            position=layout.logo_position,
            max_width_percent=logo_size,
            margin_percent=layout.safe_margin_percent,
        )

    return result
