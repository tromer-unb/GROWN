# Installation: pip, Conda and optional backends

This repository provides source-based packaging for the **Input Builder**.
There is currently **no verified GROWN package on PyPI or Anaconda**.
Installing this project requires no ML potential and runs no scientific jobs.

## Prerequisites

- Python 3.10 or newer; Python 3.11 recommended.
- Git and `pip` or Conda/Miniforge.
- Linux/macOS (usual) or Windows with a suitable shell. PBS scripts are
  intended for a Linux cluster with a configured scheduler.

## A. Virtual environment + pip

```bash
git clone https://github.com/tromer-unb/GROWN.git
cd GROWN
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
grown-input --help
```

Windows PowerShell activation: `.\.venv\Scripts\Activate.ps1`.
For noneditable installation directly from the Git URL:

```bash
python -m pip install "git+https://github.com/tromer-unb/GROWN.git"
```

A git URL installation does **not** leave a local checkout of the paper
CIF/JSON examples. Clone to access the example files and contribute changes.

## B. Conda / Miniforge

```bash
git clone https://github.com/tromer-unb/GROWN.git
cd GROWN
conda env create -f environment.yml
conda activate grown
python -m pip install -e . --no-deps
grown-input --help
```

The Conda file installs ASE, NumPy and SciPy from conda-forge, and the
last command installs the editable source without redownloading these
dependencies. Alternative:

```bash
conda create -n grown -c conda-forge python=3.11 ase numpy scipy pip
conda activate grown
python -m pip install -e . --no-deps
```

## C. Optional scientific calculator environments

Preparing CIF/JSON inputs uses only ASE, NumPy, SciPy. **Actual deposition
runs** additionally require the selected calculator's versions and model
checkpoints. Install only what your study needs:

```bash
# MACE: select a compatible PyTorch/CUDA build first
python -m pip install mace-torch

# CHGNet:
python -m pip install chgnet

# GPAW: a conda-forge option (compilation / PAW data may be platform-specific)
conda install -c conda-forge gpaw gpaw-data
```

Upstream references:
[ASE](https://ase.gitlab.io/ase/install.html),
[MACE](https://mace-docs.readthedocs.io/en/latest/guide/installation.html),
[GPAW](https://gpaw.readthedocs.io/install.html).
A library installation alone does not guarantee reproducing the exact
checkpoint/dispersion/version from the paper; check [Backends](BACKENDS.md).

## Lightweight verification (no growth)

```bash
grown-input --help
grown-input validate software/GROWN_INPUT_BUILDER/examples/graphene_X.json
```

These commands check the interface and preflight geometry. No jobs run.
Generating a new `run.sh` also does not execute it.

## Cluster considerations

Configure `pbs_queue`, `pbs_memory`, `pbs_cores` and `env_activation` for
your system; the archived examples may use the original cluster queue
`workq`. Do not run expensive calculations on a login node. Never assume
that MACE/CHGNet/GPAW or needed model weights are automatically available
on an HPC node.
