<div align="center">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="/docs/ta_black.svg">
  <img alt="TextArena logo" src="/docs/ta_white.svg" width="25%" height="25%">
</picture>
  
A suite of 100+ {single,two,multi}-Player text-based games for benchmarking and training of LLMs.

<h3>

[Play](https://textarena.ai) | [Leaderboard](https://textarena.ai/leaderboard) | [Games](https://github.com/LeonGuertler/TextArena/blob/main/textarena/envs/README.md) | [Examples](https://github.com/LeonGuertler/TextArena/tree/main/examples) | [VM Benchmark](#benchmark-test-environment)

</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/LeonGuertler/TextArena)](https://github.com/LeonGuertler/TextArena/stargazers)
[![PyPI Downloads](https://static.pepy.tech/badge/textarena)](https://pepy.tech/projects/textarena)
[![Discord](https://img.shields.io/discord/1257951838322561075?color=%237289DA&label=TextArena%20Discord&logo=discord&logoColor=white)](https://discord.gg/KPacHzK23e)
[![PyPI version](https://img.shields.io/pypi/v/textarena.svg)](https://pypi.org/project/textarena)

</div>

## Updates
* **02/10/2025** Enhanced **VendingMachine** environment with multi-item inventory management, lead times, holding costs, and dynamic news events for complex economic simulations.
* **31/07/2025** We added **SettlersOfCatan** to TextArena!
* **14/07/2025** Announcing **MindGames** a NeurIPS2025 competition for training LLMs on various TextArena games that require theory of mind.
* **01/07/2025** Release of v0.6.9 with **100** games and simplified states, new observation wrappers for training and default wrappers for environments. 
* **01/07/2025** Release of __SPIRAL: Self-Play on Zero-Sum Games Incentivizes Reasoning via Multi-Agent Multi-Turn Reinforcement Learning__ introducing RL via self-play on TextArena games as a potential new training paradigm.
* **22/06/2025** Release of [UnstableBaselines](https://github.com/LeonGuertler/UnstableBaselines) a light weight async online RL library for training LLMs on TextArena games. 
* **16/04/2025** Release of the TextArena paper 
* **14/02/2025** Release of the new, stable version for both pip and the website
* **31/01/2025** Initial demo release highlighted by Andrej Karpathy (crashing all our servers)


## Introduction
**TextArena** is a flexible and extensible framework for training, evaluating, and benchmarking models in text-based games. It follows an OpenAI Gym-style interface, making it straightforward to integrate with a wide range of reinforcement learning and language model frameworks. The repository also includes a **benchmark test environment** for Vending Machine (VM) inventory control (OR baseline, LLM-only, and LLM↔OR hybrid strategies); see [Benchmark Test Environment](#benchmark-test-environment).


## Getting Started

### Installation
Install TextArena directly from PyPI:
```bash
pip install textarena
```

### Offline Play
The only requirement __Agents__ need to fulfill is having a __call__ function that accepts string observations and returns string action. We have implemented a number of basic agents that you can find [here](https://github.com/LeonGuertler/TextArena/blob/main/textarena/agents/basic_agents.py). 

#### Example 1: TicTacToe
In this example, we show how you can let **GPT-4o-mini** play against **anthropic/claude-3.5-haiku** in a game of __TicTacToe__.

We will be using the OpenRouterAgent, so first you need to set you OpenRouter API key:
```bash
export OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"
```

Now we can build the models and let them play:

```python
import textarena as ta

# Initialize agents
agents = {
    0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
    1: ta.agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
}

# Initialize the environment
env = ta.make(env_id="TicTacToe-v0")

# wrap it for additional visualizations
env = ta.wrappers.SimpleRenderWrapper(env=env) 

env.reset(num_players=len(agents))

done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, step_info = env.step(action=action)

rewards, game_info = env.close()
```

#### Example 2: Multi-Item Vending Machine
TextArena also includes complex economic simulation games. Here's an example of the **VendingMachine** environment with multiple items, lead times, and dynamic news events:

```python
import textarena as ta
import os

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-key-here"

# Initialize agents
agents = {
    0: ta.agents.OpenAIAgent(model_name="gpt-4o-mini", system_prompt="You are a VM controller..."),
    1: ta.agents.OpenAIAgent(model_name="gpt-4o-mini", system_prompt="You are a customer..."),
}

# Initialize the multi-item vending machine
env = ta.make(env_id="VendingMachine-v0")

# Configure multiple items with different economics
env.add_item(item_id="cola", description="Cola", lead_time=1, price=7, cost=4, holding_cost=0.5)
env.add_item(item_id="chips", description="Chips", lead_time=2, price=5, cost=3, holding_cost=0.3)
env.add_item(item_id="water", description="Water", lead_time=0, price=3, cost=2, holding_cost=0.2)

# Add dynamic news events that affect demand
env.add_news(day=2, news="Weekend Sale: Expect 30% higher demand for all items")
env.add_news(day=6, news="Baseball game: Expect 50% higher demand for popcorn")

env.reset(num_players=2)

# Game loop with custom observation wrapper for context management
done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, _ = env.step(action=action)

rewards, game_info = env.close()
print(f"VM Total Reward: ${rewards[0]:.2f}")
```

**Key Features of VendingMachine:**
- **Multi-item inventory management** with different lead times and costs
- **Dynamic news events** that agents can anticipate and plan for
- **Economic complexity** with holding costs, profit margins, and procurement planning
- **Custom observation wrapper** providing complete context history and role-specific visibility
- **Realistic supply chain mechanics** with order pipelines and delivery delays


## Benchmark Test Environment

This repository includes a **benchmark test environment** for evaluating VM (Vending Machine) control strategies: OR baseline, LLM-only, and hybrid (LLM↔OR). The test data, scripts, and leaderboard/website live under `examples/`.

### Test Dataset (`examples/benchmark_for_test`)

- **`real_trajectory/`** – Real demand trajectories (e.g. H&M-style article IDs). Subfolders:
  - `lead_time_0/`, `lead_time_4/`, `lead_time_stochastic/` (by lead-time scenario).
  - Each **instance** is a directory with `train.csv` (historical demand) and `test.csv` (evaluation periods).
- **`synthetic_trajectory/`** – Synthetic demand instances with similar structure.

Each instance directory must contain:

- **`train.csv`** – Historical demand: columns like `exact_dates_<item_id>`, `demand_<item_id>`.
- **`test.csv`** – Test horizon: same date/demand columns plus per-item `description_<item_id>`, `lead_time_<item_id>`, `profit_<item_id>`, `holding_cost_<item_id>` (lead time can be integer or `inf`).

Demand is given per 14-day period; the VM agent (player 0) orders each period, and demand (player 1) is read from the CSV.

### Strategies (Four Scripts + Baseline)

| Script | Description |
|--------|-------------|
| **`or_csv_demo.py`** | OR baseline: base-stock policy (μ̂, σ̂ from history); demand from CSV. |
| **`llm_csv_demo.py`** | LLM-only: one LLM makes ordering decisions from observations; demand from CSV. |
| **`llm_to_or_csv_demo.py`** | LLM→OR: LLM proposes (L, μ̂, σ̂); backend computes orders with the OR formula. |
| **`or_to_llm_csv_demo.py`** | OR→LLM: OR recommends orders; LLM sees recommendations and makes final decisions. |
| **`perfect_score.py`** | Baseline: theoretical max profit (sum of demand × profit), no lead time or holding cost. |

All run with CSV-driven demand; LLM scripts need `--real-instance-train` (path to `train.csv`) and an API key (`OPENAI_API_KEY` for `gpt*`, `OPENROUTER_API_KEY` for OpenRouter models).

### Running Benchmarks

**Single instance (one strategy):**

```bash
# OR baseline (no API key)
python examples/or_csv_demo.py --demand-file examples/benchmark_for_test/real_trajectory/lead_time_stochastic/253448001/test.csv --real-instance-train examples/benchmark_for_test/real_trajectory/lead_time_stochastic/253448001/train.csv --promised-lead-time 2

# LLM (set OPENAI_API_KEY or OPENROUTER_API_KEY)
python examples/llm_csv_demo.py --demand-file .../test.csv --real-instance-train .../train.csv --promised-lead-time 2 --model google/gemini-3-flash-preview
```

**All strategies on one instance** (writes `benchmark_results.json` in that instance dir):

```bash
python examples/benchmark_all_strategies.py --directory examples/benchmark_for_test/real_trajectory/lead_time_stochastic/253448001 --model x-ai/grok-4.1-fast
```

Promised lead time can be set with `--promised-lead-time` or auto-detected from the path (`lead_time_0` → 0, `lead_time_4` → 4, `lead_time_stochastic` → 2).

**Batch over many instances:**

```bash
python examples/run_batch_benchmark.py --base-dir examples/benchmark_for_test/real_trajectory/lead_time_stochastic --model x-ai/grok-4.1-fast --skip-completed
```

This discovers all subdirs that contain both `test.csv` and `train.csv`, runs `benchmark_all_strategies` on each (optionally skipping instances that already have full `benchmark_results.json`), and can run multiple instances in parallel.

### Leaderboard and Benchmark Website

- **Leaderboard data** is built by aggregating `benchmark_results.json` from `*_bench` directories (e.g. `grok-4.1-fast_bench`, `gpt-5-mini_bench`). Each such directory typically mirrors the instance tree of `benchmark_for_test` and adds per-instance `benchmark_results.json` (and logs) produced by the benchmark scripts.
- **Build stats** (mean ratio to perfect, optionally by family/lead time):

  ```bash
  python examples/benchmark_website/build_stats.py
  ```

  This writes `examples/benchmark_website/data/leaderboard.json` and `_data/leaderboard.yml`.

- **Detail pages** for the static site:

  ```bash
  cd examples/benchmark_website && python generate_detail_pages.py
  ```

- **Serve the site** (e.g. `python -m http.server 8000` in `examples/benchmark_website`) and open `index.html` or `leaderboard.html`.

See `examples/benchmark_website/README.md` and `examples/benchmark_leaderboard/README.md` for more detail.


## Citation [![arXiv](https://img.shields.io/badge/arXiv-2504.11442-b31b1b.svg)](https://arxiv.org/abs/2504.11442)

If you use **TextArena** in your research, please cite:

```bibtex
@misc{guertler2025textarena,
    title={TextArena}, 
    author={Leon Guertler and Bobby Cheng and Simon Yu and Bo Liu and Leshem Choshen and Cheston Tan},
    year={2025},
    eprint={2504.11442},
    archivePrefix={arXiv},
    primaryClass={cs.CL},
    url={https://arxiv.org/abs/2504.11442}, 
}
```


// End of Selection
```
