# 📘 Interlearn — Turn Any Topic Into an Interactive Learning Experience

Transform a keyword or URL into a fully-structured, hands-on Jupyter notebook with skeleton code, automated tests, and instant feedback — so you learn by doing, not just reading.

[简体中文](./README_zh.md) | English

<p align="center">
  <img src="./doc/img/image.png" alt="Interlearn Demo" width="70%" />
</p>

## ✨ Features

- **🧩 Skeleton Code**: Every chapter includes TODO placeholders with hints so learners fill in the implementation themselves
- **✅ Instant Verification**: Each concept has automated tests that validate correctness immediately — works with both placeholder and completed implementations
- **🌍 Multi-Language Support**: All explanations, hints, and notebook content are generated in the same language as your input (English, Chinese, Japanese, Spanish, French, etc.)
- **📦 Zero Setup Friction**: Auto-installs `uv`, creates an isolated virtual environment, registers a Jupyter kernel — everything runs locally with no global pollution
- **♻️ Iterative Learning**: Continue questioning the agent based on the generated notebook — refine, dive deeper, or explore related topics without leaving your workflow
- **⚙️ Programmatic Generation**: Uses `nbformat` + `jupyter_client` to build notebooks reliably instead of hand-crafting JSON

## 🚀 Quick Start

```bash
npx skills add GaryXiongxiong/interlearn -g
```

## 📖 Usage

### Prerequisites

- **[uv](https://docs.astral.sh/uv/)** — the fast Python package installer and virtual environment manager. Install it before using Interlearn:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### Generate a Notebook

Provide a topic keyword or URL and let Interlearn do the rest:

```
/interlearn Transformer
```

### Examples

| Input Type | Example | Output |
|------------|---------|--------|
| **URL** | `/interlearn https://en.wikipedia.org/wiki/Depth-first_search` | [DFS Interactive Notebook](./examples/dfs.ipynb) |
| **Keyword** | `"教我快速排序"` | [Quick Sort Interactive Notebook in zh-CN](./examples/quicksort.ipynb) |

## 🏗️ How It Works

```
User Input (keyword or URL)
        │
        ▼
┌─────────────────────┐
│  Step 0: Detect     │◄── Language auto-detection
│      & Setup Dir    │    Creates <topic>/ directory
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Step 1: Gather     │◄── Fetch content / search knowledge
│      Info           │    Extract chapter outline
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Step 2: Env Setup  │◄── uv + venv + deps auto-install
│                   │    Registers Jupyter kernel locally
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Step 3: Structure  │◄── Creates project layout with assets/
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Step 4: Generate   │◄── Pass 1: impl=True, verify all pass
│      Notebook       │    Pass 2: impl=False, TODO placeholders
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Step 5: Deliver    │◄── Summary table + JupyterLab preview
└─────────────────────┘
```