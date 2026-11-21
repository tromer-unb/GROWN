# Data, provenance and reproducibility

This public GitHub repository contains the **minimal portable software,
source CIF structures, source input JSON configurations and archived
selected run scripts**. It deliberately does **not** commit all large
simulation trajectories, tens of thousands of intermediate geometries
or HPC logs. This keeps the version-controlled source accessible
without misleading users about the completeness of public data.

## Full research archive

The internally prepared project archive `files_reproduced.zip`
contains **2,542 original scientific source files** and research
documentation, figure rebuild scripts, plots, logs and integrity
manifests. It is distinct from this curated Git repository and **is
not yet linked to a public data DOI**. Until a verified deposit is
available, the full study cannot be claimed to be freely reproducible
solely from this GitHub checkout.

## Source fidelity

- Core code (`grown_input.py`, `mc_flux_corrigido_multiaxis_v4.py` and
  `growth_parameter_advisor_corrected_multiaxis_v4.py`) was copied
  from the original scientific archive.
- The five baseline JSON/CIF builder examples are archived original
  inputs. The bundling script `build_examples.py` was deliberately not
  published because it hard-coded the original lab's private filesystem
  and is unnecessary for users.
- Actual graphite AB 100-event MACE JSONs preserve physics-related
  fields; only local paths, PBS queue and environment activation were
  sanitized for portability. An accompanying `PORTABILITY_CHANGES.md`
  documents these edits.
- The two archived heterostructure command sets are original
  `run.sh` files and matching CIFs, not recreated or claimed to have
  been run from this GitHub snapshot.
- The original 72-case matrix is included as a small CSV; it is a
  **historical snapshot**, not current scheduler state.

## Reproducing a calculation responsibly

Record at least: seed/template SHA256, scientific JSON, PBC mask,
energy calculator name/version/checkpoint SHA, random seed, event
count, force stopping tolerance, accepted event logs, growth
candidate-screening counts, created structures, trajectory geometry,
the exact experimental comparison definition and the machine
environment. Different pretrained potential versions can yield
different energetics. A completed growth trajectory does not
guarantee a chemically accurate final structure.

## Test status and compute scope

A small 12-test Input Builder regression suite existed in the source
archive and passed with its full scientific fixtures. Public tests
are retained with **temporary output directories** to avoid
versioning five duplicate 180-KB growth engines inside generated
example folders. The tests validate the interface/PBC, not the
physics of new growth trajectories.

**No GitHub Actions simulation or automated HPC job is configured.**
Any local user execution of the engine is an explicit separate step.
