# Iron Leaf Creative Automation Pipeline

A proof-of-concept creative automation tool that generates consistent social ad creatives across multiple aspect ratios using GenAI-generated backgrounds and product compositing.

Built for the Adobe Forward Deployed AI Engineer take-home exercise.

## Features

- **Campaign Brief Input**: Accept structured campaign briefs with products, target region, audience, and messaging
- **Regional Background Generation**: Uses DALL-E 3 to generate contextual backgrounds based on target region (10+ regions including US regions and global destinations)
- **Product Compositing**: Overlays consistent product images onto generated backgrounds (shadows baked into product PNGs)
- **Multi-Format Output**: Generates creatives in 3 aspect ratios:
  - 1:1 (1080×1080) - Instagram Feed
  - 9:16 (1080×1920) - Stories/Reels
  - 16:9 (1920×1080) - YouTube/Web
- **Brand Consistency**: Applies campaign message and logo overlay according to brand guidelines
- **Streamlit UI**: Simple web interface for uploading briefs, previewing results, and downloading outputs

## Architecture

```
Campaign Brief → Parse → For Each Product:
    │
    ├── Generate Regional Background (DALL-E)
    │
    ├── Composite Product onto Background
    │
    ├── Resize to 3 Aspect Ratios
    │
    ├── Apply Brand Overlay (text + logo)
    │
    └── Save to Output Folder
```

### Key Design Decisions

1. **Product Compositing vs. Pure GenAI**: DALL-E cannot guarantee consistent product appearance across generations. By using product PNGs and compositing them onto generated backgrounds, we ensure the same product appears identically across all regional variations.

2. **Background-Only Generation**: Prompts are crafted to generate scenic backdrops suitable for product photography. Products are overlaid directly onto the backgrounds.

3. **Badge-Style Logo**: The logo includes its own background to ensure visibility regardless of the generated background colors/brightness.

4. **Separation of Concerns**: Brand configuration is separate from campaign briefs, mirroring real-world workflows where brand guidelines are fixed across campaigns.

## Project Structure

```
├── app.py                      # Streamlit web interface
├── requirements.txt            # Python dependencies
├── brand_config.json           # Iron Leaf brand configuration
├── pipeline/
│   ├── models.py               # Pydantic models for validation
│   ├── background_generator.py # DALL-E integration
│   ├── compositor.py           # Product + shadow compositing
│   ├── aspect_ratios.py        # Multi-format resizing
│   ├── brand_overlay.py        # Text + logo overlay
│   └── generator.py            # Main orchestrator
├── assets/                     # Brand images and product assets
│   ├── products/               # Product images (PNGs with baked shadows)
│   │   ├── boots.png
│   │   └── shoes.png
│   ├── cta-button.png          # Call-to-action button
│   └── iron-leaf-logo.png      # Brand logo
├── examples/
│   └── campaign_brief.json     # Example campaign brief
└── output/                     # Generated creatives
```

## Setup

### Prerequisites

- Python 3.10+
- OpenAI API key with DALL-E access

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd adobe
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenAI API key:
   ```bash
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## Usage

1. **Load Campaign Brief**: Use the example brief, upload your own JSON, or create one in the UI
2. **Review Products**: Verify the product images are loaded correctly
3. **Generate**: Click "Generate Campaign Creatives" to start the pipeline
4. **Preview**: Review generated creatives in all aspect ratios
5. **Download**: Download all creatives as a ZIP file

## Example Campaign Brief

```json
{
  "campaign_name": "Trail Season 2026",
  "products": [
    {
      "id": "trailblazer-boot",
      "name": "Trailblazer Hiking Boot",
      "description": "Waterproof leather hiking boot with Vibram sole",
      "product_image": "assets/products/boots.png"
    },
    {
      "id": "summit-jacket",
      "name": "Summit Weatherproof Jacket",
      "description": "3-layer breathable shell with sealed seams",
      "product_image": "assets/products/shoes.png"
    }
  ],
  "target_region": "us_pacific_northwest",
  "target_audience": "Outdoor enthusiasts aged 25-45",
  "campaign_message": "Conquer Every Trail"
}
```

## Available Regions

### United States

- `us_pacific_northwest` - Misty forests with moss and ferns
- `us_southwest` - Desert landscapes with red rocks and sandstone cliffs
- `us_northeast` - Autumn forests with fall foliage
- `us_rockies` - Alpine meadows with dramatic mountain peaks
- `us_midwest` - Rolling prairie grasslands and woodlands

### Global

- `alps_europe` - European Alps with dramatic alpine peaks and valleys
- `scandinavia` - Scandinavian wilderness with pine forests and fjords
- `patagonia` - Windswept plains with jagged mountain peaks
- `new_zealand` - Lush green mountains and rolling hills
- `japan_alps` - Forested mountain slopes with misty atmosphere

## Limitations & Future Enhancements

### Current Limitations

- **Compositing Realism**: Products are overlaid onto backgrounds and may not perfectly integrate with background lighting
- **Font Availability**: Uses system fonts; custom fonts require additional setup
- **Single Region per Campaign**: Current implementation generates one region per run
- **Product Shadows**: Shadows must be baked into product PNGs; no dynamic shadow generation

### Future Enhancements

- **Adobe Firefly Integration**: Swap to Firefly API when enterprise access is available for better product-scene integration
- **Multi-Region Generation**: Generate all regional variations in a single run
- **Localization**: Translate campaign messages for different markets
- **Brand Compliance Checks**: Validate logo presence, color usage, and text contrast
- **A/B Variant Generation**: Generate multiple creative variations for testing

## Technology Stack

- **Python 3.10+**: Core language
- **Streamlit**: Web UI framework
- **OpenAI DALL-E 3**: Background image generation
- **Pillow**: Image processing and compositing
- **Pydantic**: Data validation

## License

This project was created as part of a job interview exercise.

---

_Iron Leaf is a fictional outdoor gear brand created for demonstration purposes._
