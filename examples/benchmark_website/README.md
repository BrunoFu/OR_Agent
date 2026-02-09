# Benchmark Website

This directory contains the static HTML website for the AI Agents for Inventory Control Benchmark.

## Structure

```
benchmark_website/
├── index.html              # Homepage
├── leaderboard.html        # Full leaderboard page
├── dataset.html            # Dataset documentation
├── build_stats.py          # Script to generate leaderboard data
├── generate_detail_pages.py # Script to generate detail pages
├── assets/
│   └── css/
│       └── main.css       # Stylesheet
├── data/
│   └── leaderboard.json   # Leaderboard data (generated)
└── leaderboard/
    ├── gemini-3-flash/
    ├── gpt-5-mini/
    └── grok-4.1-fast/
        └── *.html          # Detail pages for each LLM+Method combination
```

## Usage

### 1. Generate Leaderboard Data

First, run the build script to aggregate benchmark results:

```bash
cd examples/benchmark_website
python build_stats.py
```

This will:
- Scan all `*_bench` directories in `examples/`
- Aggregate performance metrics from `benchmark_results.json` files
- Generate `data/leaderboard.json` for the website
- Also generate `_data/leaderboard.yml` at repo root (for backward compatibility)

### 2. Generate Detail Pages

After updating the leaderboard data, regenerate detail pages:

```bash
python generate_detail_pages.py
```

This creates HTML detail pages for each LLM+Method combination in the `leaderboard/` directory.

### 3. Serve the Website

Use any HTTP server to view the website locally:

```bash
# Using Python
python -m http.server 8000

# Using Node.js (if you have http-server installed)
npx http-server -p 8000
```

Then open `http://localhost:8000/index.html` in your browser.

## File Descriptions

- **index.html**: Homepage with benchmark overview and top 5 LLM rankings
- **leaderboard.html**: Full leaderboard showing all LLM+Method combinations
- **dataset.html**: Documentation about the benchmark dataset structure
- **build_stats.py**: Aggregates benchmark results into JSON/YAML data files
- **generate_detail_pages.py**: Generates HTML detail pages from leaderboard data

## Notes

- All paths in HTML files are relative, so the site works when served from this directory
- The website is pure HTML/CSS/JavaScript with no build step required
- Data is loaded dynamically via `fetch()` from `data/leaderboard.json`
