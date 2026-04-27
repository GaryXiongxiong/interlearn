---
name: interlearn
description: Generate structured Jupyter notebooks for self-paced study of any topic with skeleton implementations and verification tests. Supports multi-language output based on user's input language.
license: MIT
compatibility: opencode
metadata:
  audience: learners
  workflow: education
---

# Interlearn

Generates structured Jupyter notebooks for self-paced learning with skeleton code (TODOs) and immediate verification at each step. Uses `nbformat` + `jupyter_client` Python API for reliable notebook creation and execution. Supports multi-language output — the notebook content (markdown explanations, TODO hints) is generated in the same language as the user's input.

## Trigger & Input

User provides a topic in one of these formats:
- **Keyword**: `"Teach me Transformer"` / `"学习动态规划"` / `"Ajude-me a aprender Django"`
- **URL**: A tutorial, documentation, paper, or blog post link

## Workflow

### Step 0: Detect Language & Create Project Directory

**Language Detection**: Analyze the user's input to detect the primary language. Use this language for all notebook content (markdown cells, TODO hints, summaries).

| Input Example | Detected Language | Lang Code |
|---------------|------------------|-----------|
| `"Learn dynamic programming"` | English | `en` |
| `"学习动态规划"` | Chinese | `zh` |
| `"Transformerを学ぼう"` | Japanese | `ja` |
| `"Aprende sobre Django"` | Spanish | `es` |
| `"Apprends le deep learning"` | French | `fr` |

If input contains mixed languages, prefer the language of the **main request** (e.g., Chinese keywords in an otherwise English sentence → `zh`). Default to `en` if undetectable.

**Project Directory**: Parse the user's learning topic and derive a clean directory name. Create it in the current working directory, then `cd` into it for all subsequent operations.

**Naming convention**: lowercase, hyphen-separated slug from the topic keyword.

| User Input | Derived Dir Name |
|------------|-----------------|
| `"Learn dynamic programming"` | `learn-dynamic-programming` |
| `"学习动态规划"` | `study-dynamic-programming` |
| `"Teach me Transformer"` | `teach-transformer` |
| URL → `"https://pytorch.org/tutorials/..."` | Extract last path segment or use protocol-based name, e.g. `learn-pytorch-tutorial` |

```bash
# Example for "学习动态规划" (Chinese)
export LANG=zh
mkdir -p study-dynamic-programming
cd study-dynamic-programming
```

All files below are created **inside this directory**.

### Step 1: Information Gathering

- Detect language from user input (if not already done in Step 0) → set `LANG` variable
- Parse input (keyword or URL)
- If URL → fetch content via `webfetch`
- If keyword → search for relevant knowledge
- Extract knowledge structure and plan chapter outline
- **All explanations, hints, and TODO comments must be generated in the detected language (`$LANG`)**

### Step 2: Environment Setup

Generate `setup.sh` from the bundled template at `scripts/setup.sh`. The script **forces uv** as the package manager (installs it if missing), creates a virtual environment at `.venv-interactive/`, installs dependencies, and registers the Jupyter kernel **locally inside that venv** (`--sys-prefix`). No global user directory pollution.

Set theme dependencies before running:
```bash
THEME_DEPS=(...)  # empty list for pure Python topics like "Dynamic programming"
```

**Base Dependencies** (always installed):
```
jupyterlab, nbformat>=5.0, jupyter_client, ipykernel, numpy, matplotlib, tqdm
```

**Theme Plugins** (auto-detected by topic):
```
"Transformer / deep learning" → torch, jieba
"Django"                      → django
"Dynamic programming"         → no extra deps needed
"Data analysis"               → pandas seaborn
"Computer vision"             → torchvision opencv-python
"NLP"                         → transformers spacy
"Website scraping"                → requests beautifulsoup4 selenium
```

Execute the setup script:
```bash
cd <project-dir> && bash setup.sh
```

### Step 3: Create Project Structure

The following files and directories are created inside the project directory:

```
<project>/                          # e.g. study-dynamic-programming/
├── setup.sh                        # Environment config (already executed)
├── pyproject.toml                  # uv dependency manifest
├── notebook.ipynb                  # Main learning file (created by generator)
├── generate_notebook.py            # Generator script (step 4 output)
├── notebook_builder.py             # Reusable builder helper (copied from skill)
├── data/                           # Data resources (if any)
└── assets/                         # Charts, images, etc.
```

### Step 4: Generate Notebook Content via Python API

Use the bundled `scripts/notebook_builder.py` helper to construct notebooks programmatically. This is more reliable than writing ipynb JSON manually because nbformat validates structure automatically.

**Quick start — create a generator script:**

```python
#!/usr/bin/env python3
"""generate_notebook.py - Build notebook.ipynb for <Topic>."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".opencode", "skills", "interlearn", "scripts"))

from notebook_builder import NotebookBuilder, run_generator


class MyTopicBuilder(NotebookBuilder):
    """Custom builder for the specific learning topic."""

    def _build_impl(self, impl: bool) -> None:
        # Title + env check are added by base class methods in Step 5
        pass  # override to add chapters


def main():
    project = os.path.dirname(os.path.abspath(__file__))
    run_generator(MyTopicBuilder, project_dir=project)

if __name__ == "__main__":
    main()
```

**Chapter structure (each chapter has 3 cells):**

| Step | Cell Type | Content |
|------|-----------|---------|
| A | Markdown | Knowledge explanation: definitions, formulas/principles, design motivation — **in detected language** |
| B | Code | Skeleton implementation with TODOs (learner fills these in) — **hints in detected language** |
| C | Code | Verification tests: shape/type checks, edge cases, output comparison |

**Two-pass generation workflow:**
1. **Pass 1**: `implementation_mode=True` — full working code → execute all cells to verify they pass
2. **Pass 2**: `implementation_mode=False` — TODO placeholders → save as final deliverable (no execution)

If any cell fails during Pass 1, fix the implementation in the generator script and regenerate.

**⚠️ Critical: impl=True must have ZERO placeholders.** Never use `...`, `raise NotImplementedError()`, or `pass`-only function bodies in impl=True code. These cause silent execution failures that are hard to debug. Before running Pass 1, verify:
```bash
# Quick check: ensure no ... placeholders leak into impl=True templates
grep -n "^\s*\.\.\." generate_notebook.py | grep -v "# TODO" || echo "✅ No placeholder found"
```

**Recommended structure**: Define impl and non-impl templates as **separate top-level constants** (not inline in if/else blocks). This makes it visually obvious which is which:
```python
# ✅ Recommended: separate constants at module level
CH2_SKELETON_IMPL = '''\
def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
'''

CH2_SKELETON_TODO = '''\
def partition(arr, low, high):
    """Lomuto partition scheme
    
    TODO: [Implement Lomuto partition scheme]
    
    💡 Hint: 
      1. Select arr[high] as pivot
      2. Initialize i = low - 1
      ...
    """
    # TODO: Implement here
    pass
'''

class MyBuilder(NotebookBuilder):
    def _build_impl(self, impl: bool) -> None:
        self.add_chapter(
            title="Chapter 2",
            markdown=ch2_markdown,
            skeleton_code=CH2_SKELETON_IMPL if impl else CH2_SKELETON_TODO,
            verification=CH2_VERIFICATION,
        )
```

### Step 5: Delivery

- Output summary table with chapter structure + TODO locations + estimated learning time
- Invite user to begin learning; commit to answering questions — **in detected language**
- Start JupyterLab for interactive viewing (see Step 6)

## Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Minimally Runnable** | Every chapter's verification tests must pass with placeholder implementations. Tests still pass after learner fills in TODOs. |
| **Progressive Learning** | Chapters ordered by dependency — prerequisites always covered first. |
| **Immediate Feedback** | Each concept has corresponding code; each piece of code has verification via `ExecutePreprocessor`. |
| **Interactive** | TODO sections left blank but well-prompted; learners verify immediately after filling in. |
| **Multi-Language** | All notebook content (explanations, hints, summaries) is generated in the user's input language for accessibility. |

## nbformat API Reference

| Function | Purpose |
|----------|---------|
| `nbf.v4.new_notebook()` | Create empty notebook |
| `nbf.v4.new_markdown_cell(source)` | Add markdown cell |
| `nbf.v4.new_code_cell(source, execution_count=N)` | Add code cell with optional output |
| `nb.cells.append(cell)` | Add cell to notebook |
| `nbf.read(f, as_version=4)` | Read existing notebook |
| `nbf.write(nb, f)` | Save notebook (auto-validates) |
| `ExecutePreprocessor(timeout=N, kernel_name='...')` | Execute all cells via Jupyter kernel |

## TODO Comment Template

```python
# TODO: [Knowledge Point Name]
# 
# 💡 Hint: {hint_text_in_detected_language}
#
# 📐 Input shape: (batch_size, seq_len, d_model)
# 📐 Output shape: (batch_size, seq_len, d_model)
#
# ✅ Acceptance: The tests in Cell C will pass once completed.
```

## Environment Configuration Rules

**Base Dependencies**:
- `jupyterlab` — for serving notebooks interactively
- `nbformat>=5.0` — notebook file read/write with validation
- `jupyter_client` — kernel management and execution
- `ipykernel` — Python kernel installation (registered inside `.venv-interactive/`)
- `numpy, matplotlib, tqdm`

**Package Manager**: `uv` is always used. If not installed, the setup script installs it automatically via pipx or pip. The virtual environment lives at `.venv-interactive/`.

## Bundled Scripts Reference

| Script | Purpose | Location |
|--------|---------|----------|
| `setup.sh` | Force-install uv, create venv, install deps, register kernel | `scripts/setup.sh` |
| `notebook_builder.py` | Reusable NotebookBuilder class + run_generator() workflow | `scripts/notebook_builder.py` |

## Common Pitfalls

### 1. Triple-quote nesting in template strings

When using `"""..."""` to wrap Python code templates (skeleton/verification), inner docstrings with `"""..."""` will prematurely close the outer string, causing `SyntaxError`.

```python
# ❌ Fails: inner """ terminates outer string
skeleton = """\
def foo():
    """docstring here."""   # ← breaks out of template!
    pass
"""
```

**Fix**: Use `'''...'''` (single-quote triple) for all template strings. Convert inner docstrings to comments (`# comment`).

### 2. Implementation mode confusion in two-pass workflow

Pass 1 (`implementation_mode=True`) must contain **full working code** with no `...` or placeholder values. Pass 2 (`implementation_mode=False`) gets the TODO version. Mixing them up causes execution failures during verification.

```python
def _build_impl(self, impl: bool) -> None:
    if impl:
        # ✅ Full working implementation — used for execution & verification
        skeleton = '''\
def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
'''
    else:
        # ✅ TODO placeholder — delivered to learner
        skeleton = '''\
def partition(arr, low, high):
    # TODO: Implement Lomuto partition scheme...
    pivot = ...
    i = ...
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            # TODO: swap arr[i] and arr[j]
            ...
'''
```

**Key rule**: `impl=True` code must pass all verification tests when executed. If any cell has `...`, `raise NotImplementedError()`, or similar — Pass 1 will fail.

### 3. JupyterLab port conflicts

Port 8889 is commonly already in use. Always check for available ports and be prepared to specify an alternative (e.g., `--port=8890`). Use `--no-browser` since the terminal may not have a display.

```bash
# Port 8889 is default; if busy, Jupyter auto-increments but logs change
jupyter lab --no-browser --port=8890   # explicit port avoids ambiguity
```

## Delivery Command (uv-aware)

When telling the user how to start JupyterLab:

```bash
# cd into project dir first, then activate venv
cd <project-dir> && source .venv-interactive/bin/activate && jupyter lab --no-browser
```

Never use bare `jupyter lab` without activating the venv or being in the correct directory, as it may not have the interlearn kernel or required packages.

## Debugging Checklist

When notebook execution fails, follow this order:

0. **Placeholder leak check** → Run `grep -n "^\s*\.\.\." generate_notebook.py | grep -v "# TODO"`. If impl=True templates contain `...`, Pass 1 will fail with cryptic errors. This is the #1 cause of execution failures — always verify before running.
1. **Kernel discoverable?** → Run `python -c "from jupyter_client.kernelspec import KernelSpecManager; print(list(KernelSpecManager().find_kernel_specs().keys()))"`. If `interlearn` is missing, check JUPYTER_PATH (see Pitfall #3).
2. **Cell syntax valid?** → Check for `...`, `raise NotImplementedError()`, or unclosed strings in impl=True code. These cause execution failures during Pass 1.
3. **Triple-quote nesting?** → Use `'''` for template strings, not `"""`. Inner docstrings with `"""` will break the outer string (see Pitfall #1).
4. **Port conflict?** → JupyterLab defaults to 8889; use `--port=8890` if busy (see Pitfall #4).