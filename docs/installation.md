# Installation

A-Profiles supports Python **3.11–3.13**. Install it into a virtual environment to keep its dependencies separate from system Python and other projects.

## Install from PyPI

Create and activate a virtual environment in your project directory:

```shell
python -m venv .venv
```

```shell
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the latest release:

```shell
python -m pip install --upgrade pip
python -m pip install aprofiles
```

Use `python -m pip` to make sure pip is associated with the active Python environment. If you use [uv](https://docs.astral.sh/uv/), create and activate a virtual environment first, then run `uv pip install aprofiles`.

## Install the command-line interface

The `apro` command is available through the optional `cli` extra:

```shell
python -m pip install "aprofiles[cli]"
```

To install the CLI in its own managed environment, use [pipx](https://pipx.pypa.io/):

```shell
pipx install "aprofiles[cli]"
```

## Install from source

```shell
git clone https://github.com/AugustinMortier/A-Profiles.git
cd A-Profiles
python -m venv .venv
```

Activate `.venv` using the command for your shell above, then install:

```shell
python -m pip install .
```

For development, install in editable mode with the development, documentation, and CLI dependencies:

```shell
python -m pip install -e ".[dev,docs,cli]"
```
