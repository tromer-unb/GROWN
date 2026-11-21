# Energy calculators: what to install, what to validate

The Input Builder's own dependencies are **ASE, NumPy and SciPy**. It can
prepare cases with `backend` names `chgnet`, `mace`, `gpaw`, `emt`, `lj`,
`sevennet` and `mattersim`. Not every backend/material combination has
been benchmarked in the paper or tested on every platform.

| Backend | Typical installation | Scientific considerations |
|---|---|---|
| MACE | `python -m pip install mace-torch` | PyTorch version/device, checkpoint, dispersion handling and chemical domain |
| CHGNet | `python -m pip install chgnet` | Potential transferability, especially van der Waals graphite |
| GPAW | `conda install -c conda-forge gpaw gpaw-data` | PAW datasets, basis, k-points, XC and memory convergence |
| EMT / LJ | ASE built-ins | Lightweight diagnostic calculators; generally unsuitable for quantitative materials predictions |
| SevenNet / MatterSim | Upstream model instructions | Optional research interfaces; install and verify API/checkpoint compatibility independently |

These are **optional** model packages. Do not install all ML/DFT stacks
just to create inputs. GROWN's generated scripts are model-agnostic
front-end commands; the physical result remains a function of the
selected calculator, chemical environment and relaxation settings.

## MACE in the graphite AB manuscript

The archived corrected graphite AB benchmark used MACE-MP (small) with
dispersion enabled for a fixed-geometry interlayer comparison. The
basal cleavage estimate was **0.271 J/m²**, compared with the derived
ideal-Bernal benchmark **0.39 ± 0.02 J/m²**. A 30.5% difference remains,
although sign/scale and interlayer separation are physically plausible.
A new installation of `mace-torch` is not proof of a bitwise-identical
scientific environment; pin package versions and record model checksums.

## CHGNet transferability caveat

In the same graphite geometry the archived CHGNet reference gave a
negative basal cleavage estimate and an excessively large preferred
interlayer spacing. This does not necessarily indict CHGNet on all
materials, but means the chosen potential must be **validated on a
specific interatomic interaction** before conclusions are drawn.

## GPAW first-principles pilot

The archived C32→C34 graphite pilot contains two depositions; this
demonstrates an engine connection, not converged density-functional
binding or kinetic barriers. Production GPAW work requires careful
convergence tests and platform-specific PAW/basis setup.

## Computational hygiene

- Never run heavy jobs on a cluster login node or automatically on
  GitHub.
- Record backend/library version, checkpoint hash, CPU/GPU and
  precision, atomic reference energies, dispersion flags and all
  convergence settings.
- Model potential energies are **not automatically comparable** across
  different backends or reservoir references.
- Geometric candidate exhaustion is **not** an energy-based physical
  growth-stop prediction.
- The flux-clock parameter in the engine is **not** a calibrated
  experimental growth-rate prediction.

Upstream: [MACE](https://mace-docs.readthedocs.io/en/latest/guide/installation.html),
[ASE](https://ase.gitlab.io/ase/install.html),
[GPAW](https://gpaw.readthedocs.io/install.html).
