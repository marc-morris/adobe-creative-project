"""
DALL-E background generation with regional prompts.
"""

import os
import requests
from io import BytesIO
from pathlib import Path
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")


def get_openai_client() -> OpenAI:
    """Get OpenAI client, with helpful error if API key is missing."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please create a .env file in the project root with:\n"
            "OPENAI_API_KEY=your_key_here"
        )
    return OpenAI(api_key=api_key)


# Regional background prompts - scenic backdrops for product overlay
REGION_PROMPTS = {
    # United States
    "us_pacific_northwest": (
        "Wide landscape photograph of United States Pacific Northwest forest hiking trail, misty atmosphere, "
        "moss-covered trees and ferns, soft diffused natural lighting, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    "us_southwest": (
        "Wide landscape photograph of United States Southwest desert hiking trail, "
        "red rock formations and sandstone cliffs, warm golden hour lighting with soft shadows, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    "us_northeast": (
        "Wide landscape photograph of United States Northeast forest hiking trail in autumn, "
        "dense hardwood forest with red and orange fall foliage, warm afternoon sunlight filtering through trees, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    "us_rockies": (
        "Wide landscape photograph of United States Rocky Mountains hiking trail, "
        "alpine meadow with wildflowers, dramatic mountain peaks, crisp clear mountain light, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    "us_midwest": (
        "Wide landscape photograph of United States Midwest hiking trail, "
        "rolling prairie grasslands with tall grasses, oak and maple woodlands, gentle hills, "
        "soft natural light beneath a wide open sky, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    # Global regions
    "alps_europe": (
        "Wide landscape photograph of European Alps hiking trail, "
        "dramatic alpine peaks, green valleys, rocky paths, crisp high-altitude light, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    "scandinavia": (
        "Wide landscape photograph of Scandinavian wilderness hiking trail, "
        "pine forests, rocky terrain, fjord landscape, cool soft daylight, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    "patagonia": (
        "Wide landscape photograph of Patagonia hiking trail, "
        "windswept plains, jagged mountain peaks, glacial valleys, dramatic moody natural light, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    "new_zealand": (
        "Wide landscape photograph of New Zealand hiking trail, "
        "lush green mountains, rolling hills, distant peaks, clean natural daylight, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
    "japan_alps": (
        "Wide landscape photograph of Japanese Alps hiking trail, "
        "forested mountain slopes, rocky paths, misty atmosphere, soft morning light, photorealistic, "
        "image fills entire canvas with no black bars or borders, no letterboxing, "
        "no people, no text, no products, no logos, no vignette, no frame"
    ),
}


def generate_background(region: str, size: str = "1792x1024") -> Image.Image:
    """
    Generate a regional background image using DALL-E 3.

    Args:
        region: Region key (pacific_northwest, southwest, northeast, rockies)
        size: Image size (1792x1024 for landscape, 1024x1792 for portrait)

    Returns:
        PIL Image of the generated background
    """
    # Get prompt for region, fallback to first available region if not found
    prompt = REGION_PROMPTS.get(region)
    if prompt is None:
        # Use first available region as fallback
        fallback_region = list(REGION_PROMPTS.keys())[0]
        print(
            f"Warning: Region '{region}' not found. Using '{fallback_region}' as fallback."
        )
        prompt = REGION_PROMPTS[fallback_region]

    print(f"Generating {region} background...")

    client = get_openai_client()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
    )

    # Download the image
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))

    print(f"Background generated successfully!")
    return image


def get_available_regions() -> list[str]:
    """Return list of available region keys."""
    return list(REGION_PROMPTS.keys())
