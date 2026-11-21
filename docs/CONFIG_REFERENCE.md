# Input JSON configuration reference

The Input Builder reads a **JSON object** and rejects unknown keys. CIF
and `run_directory` paths are interpreted relative to the JSON file.
The following parameter groups reflect the archived `grown_input.py`
v0.1 source. Fields not explicitly supplied use the code defaults.

## Required scientific specification

| Key | Kind | Meaning / typical value |
|---|---|---|
| `name` | string | Short run label; e.g. `Gr_X_demo` |
| `structure` | CIF path | Initial structure (ASE readable) |
| `template` | CIF path or null | Distinct growth template; null uses structure |
| `dimension` | string | `2d`, `3d`, `layered` or `layered_bulk` |
| `growth_axis` | string | `x`, `y`, `z`, `xy`, `xz`, `yz` or `xyz` |
| `backend` | string | `chgnet`, `mace`, `gpaw`, `emt`, `lj`, `sevennet` or `mattersim` |
| `deposition_species` | list of elements | E.g. `["C"]` or `["Mo","S"]` |
| `events` | positive integer | Maximum **accepted** events (default 20) |
| `run_directory` | path | New, nonempty output folder is **refused** |

## Physical and stochastic controls

| Key | Default | Meaning |
|---|---|---|
| `temperature_K` | 500 | Algorithmic temperature, K |
| `flux_ML_s` | 0.001 | Imposed deposition flux in ML/s; **not a calibrated growth rate** |
| `seed` | 490596 | Pseudorandom seed for candidate sampling |
| `relax_steps` | 6 | Local relaxation steps per event |
| `fmax_eV_A` | 0.05 | Local force-tolerance target, eV/Å |
| `mobile_radius_A` | 4.5 | Mobile-relaxation neighborhood, Å |
| `impurities` | `{}` | Probability per new event: e.g. `{"N":0.1}`, `{"vac":0.2}` |
| `mace_model` | `small` | Model size/alias for MACE backend |
| `gpaw_mode` | `lcao` | `lcao`, `pw` or `fd` |
| `gpaw_basis` | `dzp` | Basis for GPAW LCAO mode |
| `gpaw_kpts` | `[1,1,1]` | GPAW k-point mesh (converge for research) |
| `gpaw_xc` | `PBE` | GPAW XC functional |

## Template and geometry settings

| Key | Default | Meaning |
|---|---|---|
| `template_build_mode` | `extend-columns` | `repeat` / `extend-columns` |
| `template_extend_ncols` | 12 | Number of future template columns |
| `template_column_period` | 2 | Crystallographic column period |
| `template_column_tol_A` | 0.2 | Column tolerance in Å |
| `template_front_max_A` | 3.5 | Front-search cutoff in Å |
| `template_connect_cutoff_A` | 1.9 | Local connectivity cutoff in Å |
| `min_dist_A` | 1.0 | Absolute minimum distance in Å |
| `template_occupancy_tol_A` | 0.65 | Template-site occupation tolerance |
| `template_min_neighbors` | 1 | Connectivity requirement (often 0 for new basal sheets) |
| `template_front_mode` | `shell` | `shell`, `global`, `all_connected` |
| `growth_direction` | `plus` | `plus`, `minus`, `both` |
| `template_species_mode` | `template` | `template` or `command` |
| `growth_origin_species` | null | Source species identifying the growing region |
| `restrict_Z_fraction` | null | Vertical fraction defining film region (0–1) |
| `pbc_override` | null | Explicit [X,Y,Z] PBC mask; growing axes cannot be periodic |
| `advanced_args` | `[]` | Additional engine CLI tokens; restricted core flags rejected |
| `enable_advisor_report` | true | Write geometric advisor report |

## Scheduler and environmental settings

| Key | Default | Meaning |
|---|---|---|
| `pbs_queue` | null | Queue name; **`workq` in archived samples is site-specific** |
| `pbs_memory` | `16gb` | Job memory request |
| `pbs_cores` | 1 | PBS CPU core request |
| `env_activation` | empty | Trusted one-line shell activation in generated PBS file |

## Important constraints

- A growth axis cannot be periodic. The builder selects PBC automatically
  and checks physically plausible seams, with special rules for compact
  `layered_bulk` graphite.
- `2d` forbids Z growth. `layered` is a slab (nonperiodic Z), whereas
  `layered_bulk` requires a compact van der Waals periodic seam in Z for
  prismatic growth.
- JSON `advanced_args` is a list of string tokens, not a single shell
  command. Reserved flags such as `--cif`, `--growth-axis` and
  `--site-mode` cannot be overridden there.
- The energy cutoff `--max-adsorption-energy-eV` is an **engine advanced
  option** rather than a first-class builder field in v0.1. It is not
  turned on by default. Use the `advanced_args` token list only after
  reading the engine help/source and reviewing scientific meaning.
- `impurities` probabilities are **stochastic per new event**; they do
  not guarantee an exact final atom fraction.
- Basal Z continuation can require zero covalent neighbors at the
  prospective first new sheet, which is an explicit approximation to be
  analyzed rather than a proof of spontaneous layer nucleation.
- `env_activation` is executed by the generated PBS shell script.
  Never copy untrusted commands into it.

For complete source defaults and validation logic, inspect
[`grown_input.py`](../software/GROWN_INPUT_BUILDER/grown_input.py).
