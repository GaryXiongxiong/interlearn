#!/usr/bin/env python3
"""
notebook_builder.py - Reusable template for generating interactive learning notebooks.

Usage in generate_notebook.py:
    from notebook_builder import NotebookBuilder, TODO_CELL_TEMPLATE
    
    builder = NotebookBuilder(project_dir=".")
    
    # Add cells
    builder.add_title("My Topic")
    builder.add_env_check()
    
    builder.add_chapter(
        title="Chapter 1: Introduction",
        markdown="# What is X?\n\nExplanation here...",
        skeleton_code=skeleton,      # Code with TODOs (for learner)
        verification=verification,   # Test code that validates implementation
    )
    
    builder.add_summary(summary_md)
    
    # Two-pass generation:
    # Pass 1: With full implementations → execute to verify
    nb = builder.build(implementation_mode=True)
    builder.execute_and_save(nb, "notebook.ipynb")
    
    # Pass 2: With TODO placeholders → deliver to learner
    nb_todo = builder.build(implementation_mode=False)
    builder.save(nb_todo, "notebook.ipynb")

"""

import os
import sys
from typing import Optional

# ─── JUPYTER_PATH setup (MUST be before jupyter imports) ──────────
# The kernel is registered via --sys-prefix into .venv-interactive/share/jupyter/.
# We need to tell jupyter_client where to find it. Set paths relative to CWD
# and relative to this file's directory (handles both project-dir and skill-dir usage).
_jupyter_paths = []

# Relative to current working directory
_cwd_venv = os.path.join(os.getcwd(), ".venv-interactive", "share", "jupyter")
if os.path.isdir(_cwd_venv):
    _jupyter_paths.append(_cwd_venv)

# Relative to this file's location (skill scripts directory)
_skill_dir = os.path.dirname(os.path.abspath(__file__))
_skill_parent = os.path.dirname(_skill_dir)  # .opencode/skills/<name>/
_skill_venv = os.path.join(_skill_parent, ".venv-interactive", "share", "jupyter")
if os.path.isdir(_skill_venv):
    _jupyter_paths.append(_skill_venv)

# Also add to any existing JUPYTER_PATH
_existing = os.environ.get("JUPYTER_PATH", "")
_all_paths = [p for p in (_existing + ":" + ":".join(_jupyter_paths)).split(":") if p]
os.environ["JUPYTER_PATH"] = ":".join(_all_paths)


import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor


# ─── TODO Comment Template ────────────────────────────────────────
TODO_CELL_TEMPLATE = """\
# TODO: [{knowledge_point}]
#
# 💡 Hint: {hint}
#
# 📐 Input shape: {input_shape}
# 📐 Output shape: {output_shape}
#
# ✅ Acceptance: The tests in Cell C will pass once completed.
"""


class NotebookBuilder:
    """Builds structured interactive learning notebooks with nbformat."""

    def __init__(self, project_dir: str = ".", kernel_name: str = "interlearn", language: str = "en"):
        self.project_dir = os.path.abspath(project_dir)
        self.kernel_name = kernel_name
        self.language = language

    def _new_notebook(self) -> nbf.NotebookNode:
        """Create an empty notebook with proper kernelspec metadata."""
        nb = nbf.v4.new_notebook()
        nb.metadata["kernelspec"] = {
            "display_name": f"Python 3 ({self.kernel_name})",
            "language": "python",
            "name": self.kernel_name,
        }
        # Store content language for reference (markdown/TODO hints use this)
        nb.metadata["interlearn_language"] = self.language
        return nb

    # ─── Header Cells ──────────────────────────────────────────────

    def add_title(self, title: str, subtitle: Optional[str] = None) -> None:
        """Add the notebook title cell."""
        source = f"# {title}\n"
        if subtitle:
            source += f"\n{subtitle}"
        self._nb.cells.append(nbf.v4.new_markdown_cell(source))

    def add_env_check(self, extra_checks: Optional[str] = None) -> None:
        """Add environment verification cell."""
        code = (
            "import sys\n"
            'print(f"Python: {sys.version}")\n'
            "\n"
            "# Verify core dependencies\n"
            "try:\n"
            "    import numpy as np\n"
            '    print(f"numpy: {np.__version__}")\n'
            "except ImportError:\n"
            '    print("WARNING: numpy not installed")\n'
            "\n"
            "try:\n"
            "    import matplotlib\n"
            '    print(f"matplotlib: {matplotlib.__version__}")\n'
            "except ImportError:\n"
            '    print("WARNING: matplotlib not installed")\n'
        )
        if extra_checks:
            code += "\n# Additional checks\n" + extra_checks
        self._nb.cells.append(nbf.v4.new_code_cell(code))

    # ─── Chapter Cells ─────────────────────────────────────────────

    def add_chapter(
        self,
        title: str,
        markdown: str,
        skeleton_code: str,
        verification: str,
    ) -> None:
        """Add a full chapter with 3 cells: theory (A), skeleton (B), tests (C).

        Args:
            title: Chapter heading (e.g. "Chapter 1: Introduction")
            markdown: Theory/explanation content (markdown)
            skeleton_code: Code cell with TODOs for the learner
            verification: Test code that validates the implementation
        """
        self._nb.cells.append(nbf.v4.new_markdown_cell(f"## {title}\n\n{markdown}"))
        self._nb.cells.append(nbf.v4.new_code_cell(skeleton_code))
        self._nb.cells.append(nbf.v4.new_code_cell(verification))

    def add_summary(self, content: str) -> None:
        """Add a final summary/conclusion cell."""
        self._nb.cells.append(nbf.v4.new_markdown_cell(f"---\n\n{content}"))

    # ─── Build & Execute ───────────────────────────────────────────

    def build(self, implementation_mode: bool = False) -> nbf.NotebookNode:
        """Build the notebook. Subclasses override _build_impl() for content."""
        self._nb = self._new_notebook()
        if implementation_mode:
            self._build_impl(True)
        else:
            self._build_impl(False)
        return self._nb

    def execute_and_save(self, nb: nbf.NotebookNode, filename: str = "notebook.ipynb") -> None:
        """Execute all cells and save the notebook."""
        filepath = os.path.join(self.project_dir, filename)
        ep = ExecutePreprocessor(timeout=600, kernel_name=self.kernel_name)
        ep.preprocess(nb, {"metadata": {"path": self.project_dir}})

        with open(filepath, "w") as f:
            nbf.write(nb, f)

    def save(self, nb: nbf.NotebookNode, filename: str = "notebook.ipynb") -> None:
        """Save notebook without executing."""
        filepath = os.path.join(self.project_dir, filename)
        with open(filepath, "w") as f:
            nbf.write(nb, f)

    # ─── Override This Method ──────────────────────────────────────

    def _build_impl(self, implementation_mode: bool) -> None:
        """Override in subclass to define chapter content.

        Args:
            implementation_mode: True = working code, False = TODO placeholders
        """
        raise NotImplementedError(
            "Subclass must implement _build_impl(implementation_mode)"
        )


def run_generator(builder_cls, project_dir: str = ".", language: str = "en", verbose: bool = True) -> None:
    """Run the two-pass generation workflow.

    Args:
        builder_cls: A NotebookBuilder subclass (instantiated with no args)
        project_dir: Directory to write notebook.ipynb into
        language: Content language code for markdown/TODO hints (e.g. 'en', 'zh', 'ja')
        verbose: Print progress messages
    """
    import time

    if verbose:
        print("📝 Step 1: Generating notebook with full implementations...")

    # Pass 1: Build + execute to verify all tests pass
    builder = builder_cls()
    nb = builder.build(implementation_mode=True)

    if verbose:
        print("⚡ Executing all cells to verify correctness...")

    ep = ExecutePreprocessor(timeout=600, kernel_name="interlearn")
    try:
        ep.preprocess(nb, {"metadata": {"path": project_dir}})
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        sys.exit(1)

    # Save executed version for reference
    with open(os.path.join(project_dir, "notebook.ipynb"), "w") as f:
        nbf.write(nb, f)

    if verbose:
        print("✅ Notebook generated and verified successfully!")

    # Pass 2: Rebuild with TODO placeholders (no execution needed)
    if verbose:
        print("\n📝 Step 2: Regenerating notebook with TODO placeholders...")

    builder_todo = builder_cls()
    nb_todo = builder_todo.build(implementation_mode=False)
    with open(os.path.join(project_dir, "notebook.ipynb"), "w") as f:
        nbf.write(nb_todo, f)

    if verbose:
        print("✅ Final notebook saved as notebook.ipynb")


# ─── Convenience: Main Entry Point ────────────────────────────────

if __name__ == "__main__":
    # Usage from command line: python3 notebook_builder.py <project_dir>
    project = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Usage: Create a builder subclass, then call run_generator(MyBuilder, '{project}')")
