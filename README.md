# PopMart Stock Checker

A web scraper tool to monitor stock availability of products on PopMart Japan store. Uses Playwright to detect "Add to Cart" and "Sold Out" buttons in Japanese and English.

## Features

- Monitors PopMart Japan product pages for stock availability
- Detects Japanese and English stock status indicators
- Handles cookie banners automatically
- Extracts price information when available
- Returns structured JSON output with timestamp
- Configurable retry logic with environment variables
- Docker support for containerized execution

## Installation

### Local Setup

1. Install dependencies:
```bash
make setup
```

Or manually:
```bash
uv sync
uv run playwright install chromium
```

### Docker Setup

Build the Docker image:
```bash
make docker-build
```

## Usage

### Command Line

Default product check:
```bash
make run
```

Check specific product:
```bash
make run URL=https://www.popmart.com/jp/products/YOUR_PRODUCT_ID
```

Direct Python execution:
```bash
uv run python main.py https://www.popmart.com/jp/products/3884
```

### Docker

Run with default URL:
```bash
make docker-run
```

Run with custom URL:
```bash
make docker-run-url URL=https://www.popmart.com/jp/products/YOUR_PRODUCT_ID
```

## Configuration

Environment variables for customization:

- `RETRIES` - Number of retry attempts (default: 3)
- `RETRY_WAIT_MS` - Wait time between retries in milliseconds (default: 1200)
- `USER_AGENT` - Custom user agent string

Example:
```bash
RETRIES=5 RETRY_WAIT_MS=2000 uv run python main.py https://www.popmart.com/jp/products/3884
```

## Output Format

Returns JSON with the following structure:

```json
{
  "url": "https://www.popmart.com/jp/products/3884",
  "in_stock": true,
  "status": "IN_STOCK",
  "detected_texts_sample": ["«üÈký ", "üeY‹"],
  "price": "¥1,320",
  "checked_at": "2024-01-01T15:30:45+09:00"
}
```

### Status Values

- `IN_STOCK` - Product is available for purchase
- `OUT_OF_STOCK` - Product is sold out or unavailable
- `UNKNOWN` - Unable to determine stock status
- `ERROR` - An error occurred during checking

## Detection Logic

The tool searches for specific text patterns to determine stock status:

**In Stock Indicators (Japanese/English):**
- «üÈký  (Add to Cart)
- «üÈx (To Cart)  
- Add to Cart
- «üÈ (Cart)
- üe (Purchase)

**Sold Out Indicators:**
- («Œ (Out of Stock)
- SOLD OUT
- òŠŒ (Sold Out)
- Œò (Completely Sold)

## Development

### Available Make Commands

```bash
make help           # Show all available commands
make setup          # Install dependencies
make run            # Run with default URL
make run-python     # Show explicit command being run
make docker-build   # Build Docker image
make docker-run     # Run in Docker
make clean          # Clean up build artifacts
```

## Requirements

- Python 3.10+
- uv package manager
- Playwright with Chromium browser