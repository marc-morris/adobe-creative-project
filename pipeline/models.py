"""
Pydantic models for campaign briefs and brand configuration.
"""
from pydantic import BaseModel


class Product(BaseModel):
    """A product to feature in the campaign."""
    id: str
    name: str
    description: str
    product_image: str  # Path to transparent PNG


class CampaignBrief(BaseModel):
    """Campaign brief containing all inputs for creative generation."""
    campaign_name: str
    products: list[Product]
    target_region: str
    target_audience: str
    campaign_message: str


class LayoutRules(BaseModel):
    """Rules for positioning brand elements."""
    logo_position: str = "bottom-right"
    logo_max_width_percent: float = 15.0
    text_position: str = "top-left"
    safe_margin_percent: float = 5.0
    text_background_opacity: float = 0.75


class BrandConfig(BaseModel):
    """Brand configuration for consistent styling."""
    brand_name: str
    colors: dict[str, str]
    typography: dict[str, str]
    logos: dict[str, str]
    layout_rules: LayoutRules

