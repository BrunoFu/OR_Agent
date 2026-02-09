# TextArena Benchmark Website Rules (Phase 1)

This document distills reusable website rules from `examples/_reference/brightbenchmark.github.io` for building the TextArena benchmark site. It captures patterns, not content. Do not copy text, tables, records, or assets from the reference repository.

## 1. Overall Layout Structure

### Observed in reference
- Shared shell around page content: head, header, footer, and content container.
- Multiple layout templates for different page families (generic pages and challenge/landing pages).
- Content pages are mostly markdown with front matter; some challenge pages are heavily custom HTML.

### Reusable rules
- Keep one stable shell for global consistency:
  - shared `<head>`
  - shared top navigation
  - shared footer
  - single content wrapper
- Allow page-specific sections inside the shell (hero, cards, tables, callouts) without redefining the global frame.

## 2. Navigation Pattern

### Observed in reference
- Header-driven navigation with top-level links.
- Some pages are generated from page metadata; some use custom links.

### Reusable rules
- Use explicit navigation data (not automatic page-title sorting) to avoid unstable ordering.
- Define nav items in one data file and render from template.
- Current IA for v1:
  - Home
  - Dataset
  - Leaderboard

## 3. Page Types and Roles

### Observed in reference
- Landing/challenge pages combine narrative, quick links, and performance tables.
- Generic pages present structured lists/tables from data files.

### Reusable rules
- Separate responsibilities:
  - Home: benchmark identity, high-level counts, method families, quick actions.
  - Dataset: scope, structure, lead-time setup, file schema, data access.
  - Leaderboard: standardized ranking table, result fields, submission format.
- Keep descriptive content and benchmark-result rendering logically separated.

## 4. CSS / Typography Conventions

### Observed in reference
- Mixed style systems coexist (legacy Bootstrap/Jekyll style + newer research-site style).
- Inconsistent typography and component styles across pages.

### Reusable rules
- Use one design system for the new site:
  - CSS variables for colors, spacing, and typography.
  - One responsive grid/card/table system.
  - No mixed UI frameworks in v1.
- Visual direction: **Clean Data-Lab**
  - professional, data-first
  - moderate contrast and restrained accents
  - clean hierarchy for benchmark information

## 5. Component Patterns

### Observed in reference
- Heavy use of tables for rankings and structured metadata.
- Repeated section cards and grouped content blocks.

### Reusable rules
- Define canonical components and reuse everywhere:
  - card block (summary + grouped content)
  - table block (leaderboard + dataset structure)
  - small metadata badge/tag
  - callout box (pending links, caveats, update notes)
- Keep table headers stable so result files can be injected without template rewrites.

## 6. Build System (Jekyll Structure)

### Observed in reference
- Standard Jekyll primitives are used:
  - `_config.yml`
  - `_layouts`
  - `_includes`
  - `_data`
  - markdown pages with front matter

### Reusable rules
- Keep content rendering data-driven:
  - put navigation and benchmark metadata under `_data/*.yml`
  - keep markdown pages template-oriented
- Keep templates minimal and composable for GitHub Pages compatibility.

## 7. Do / Don’t Constraints

### Do
- Reuse architecture patterns and component logic.
- Recreate layout behavior with original wording and original styles.
- Keep benchmark-specific content aligned with local TextArena source data.

### Don’t
- Do not copy reference prose, names, rows, leaderboard results, or assets.
- Do not mirror reference CSS class names as a direct clone.
- Do not import reference site media unless explicitly licensed and required.

## 8. Mapping to TextArena Content

### Included source scope (v1 public benchmark scope)
- `examples/benchmark/real_trajectory` (600 instances)
- `examples/benchmark/synthetic_trajectory` (720 instances)
- Total benchmark scope: 1320 instances

### Explicitly excluded from benchmark scope pages
- `examples/benchmark/200_articles`
- benchmark logs and batch summaries
- `benchmark_results.json`
- strategy output text files (`or_*.txt`, `llm_*.txt`, etc.)

## Implementation Notes for Phase 1

- Site root: `examples/benchmark_website`
- Language: English only (v1)
- Initial pages:
  - `index.md`
  - `dataset.md`
  - `leaderboard.md`
- Leaderboard starts as a full-schema placeholder with empty entries.

## 9. External Resources

- **Dataset (primary host)**: [Hugging Face – inventory_control_benchmark_instances](https://huggingface.co/datasets/Yaopeng12138/inventory_control_benchmark_instances)
- **Codebase**: [GitHub – OR_Agent](https://github.com/BrunoFu/OR_Agent)

These URLs are the canonical references used by the benchmark website for the **Dataset** and **Code** buttons and for download links on the dataset page.

## 10. Page Inventory and Roles

### 10.1 Home (`index.md`)

- **Purpose**: Introduce the benchmark, highlight the 1,320 instances, and provide direct access to dataset, code, and leaderboard.
- **Main components**:
  - hero block (title, subtitle, action buttons)
  - two-column section: left narrative (“Why this benchmark?”, “Benchmark design”), right leaderboard preview card (top‑k methods, link to full leaderboard)
  - “Benchmark at a glance” cards with key numbers
  - short “Dataset overview” teaser with link to dataset page

### 10.2 Dataset (`dataset.md`)

- **Purpose**: Document the construction, structure, and file formats of the 1,320 benchmark instances and point users to the Hugging Face dataset.
- **Main components**:
  - intro paragraph and Hugging Face download button
  - summary of synthetic vs real instances (using numbers from `examples/benchmark/BENCHMARK_SPECIFICATION.md`)
  - directory layout and naming conventions
  - `train.csv` and `test.csv` schema tables
  - brief explanation of lead time and profit/holding-cost settings

### 10.3 Leaderboard (`leaderboard.md`)

- **Purpose**: Present benchmark results for OR baselines, LLM agents, and OR–LLM hybrids.
- **Main components**:
  - intro text explaining the metric (cumulative reward and normalized reward)
  - overall leaderboard table with stable column headers
  - optional subtables for synthetic-only and real-only subsets
  - notes on evaluation protocol and how to submit new results

## 11. Homepage Hero and Components

### 11.1 Hero block

- **Title**: `AI Agents for Inventory Control Benchmark`
- **Subtitle**: `A 1,320‑instance benchmark for stress‑testing OR and LLM‑based agents under non‑stationary demand and uncertain lead times.`
- **Primary buttons**:
  - **Dataset** → Hugging Face dataset URL
  - **Code** → GitHub codebase URL
  - **Leaderboard** → internal leaderboard page or anchor
  - **Paper** → placeholder (can be filled later with an arXiv link)
- **Meta line** (no author list on the website):  
  `Benchmark for OR‑ and LLM‑based inventory agents on synthetic and real trajectories.`

### 11.2 Two‑column main section

- **Left column**:
  - section heading: “Why this benchmark?”
  - 2–3 short paragraphs describing limitations of classical OR under regime shifts and the motivation for combining OR and LLM agents
  - section heading: “Benchmark design”
  - bullets for:
    - synthetic trajectories (10 patterns × 4 variants, 720 instances)
    - real trajectories (H&M weekly sales, 600 instances)
    - lead time regimes and lost orders

- **Right column**:
  - card heading: “Leaderboard (preview)”
  - short description: the table shows top‑k methods; link to full leaderboard page
  - table header: `Rank | Method | LLM | Setting | Score`
  - initial state: placeholder rows until real results are available
  - button: “View full leaderboard”

### 11.3 Benchmark at a glance

- section heading: “Benchmark at a glance”
- four cards:
  1. **1,320 instances** – synthetic and real inventory trajectories
  2. **2 benchmark families** – synthetic stress tests and real‑data demand
  3. **Lead‑time regimes** – immediate, fixed, and stochastic with lost orders
  4. **Methods and agents** – OR baselines, LLM agents, and OR–LLM hybrids

### 11.4 Dataset teaser on home

- section heading: “Dataset overview”
- 1–2 sentences explaining each instance as a directory with `train.csv` and `test.csv`
- button: “Explore the dataset” → dataset page

