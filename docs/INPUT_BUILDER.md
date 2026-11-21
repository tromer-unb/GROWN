# Step-by-step Input Builder tutorial

GROWN separates **scientific input preparation** from **production growth**.
The user-facing Python application takes a CIF seed, an optional separate
growth template and a JSON configuration.

```text
CIF seed (+ optional template) → JSON → geometric preflight/adviser
                                      ↓
                   validated input, engine copy, run.sh, job.pbs
                                      ↓
                   researcher decides whether to run externally
```

## 1. Start from an existing scientific CIF

Use an atomistic structure readable by ASE, with the intended growth
front exposed, sensible vacuum/cell lengths and correct in-plane
lattice periodicity. For film/substrate heterostructures, select a
**film-only template** with cell coordinates matching the complete
heterostructure seed.

## 2. Make a configuration

Interactive wizard:

```bash
grown-input init my_case.json
```

Or copy and edit a real source example. For reference, the archived
graphene X preset contains:

```json
{
  "name": "Gr_X_demo",
  "structure": "graphene_C128_periodicY.cif",
  "dimension": "2d",
  "backend": "chgnet",
  "growth_axis": "x",
  "deposition_species": ["C"],
  "events": 8,
  "template_extend_ncols": 12,
  "template_column_period": 2,
  "template_front_max_A": 3.5,
  "template_connect_cutoff_A": 1.8,
  "min_dist_A": 1.0,
  "mobile_radius_A": 4.0,
  "run_directory": "generated/graphene_X",
  "pbs_queue": "workq",
  "env_activation": ""
}
```

The original queue `workq` is cluster-specific. Change to your queue or
set `pbs_queue` to `null` for a scheduler-default queue. CIF and output
paths are resolved **relative to the location of the JSON file**.

## 3. Validate without running growth

```bash
grown-input validate software/GROWN_INPUT_BUILDER/examples/graphene_X.json
```

Inspect resolved PBC mask, element composition, minimum atom separation,
boundary seams, directional front connectivity, layer/vacuum correctness,
the adviser messages and accepted input parameters. For graphite AB,
`dimension: layered_bulk` permits a genuinely compact van der Waals
seam in Z during lateral growth, unlike a vacuum-separated layer/slab.

## 4. Generate — no model execution

```bash
grown-input generate software/GROWN_INPUT_BUILDER/examples/graphene_X.json
```

This prepares:

```text
examples/generated/graphene_X/
  seed.cif (with the original scientific filename)
  mc_flux_corrigido_multiaxis_v4.py
  growth_parameter_advisor_corrected_multiaxis_v4.py
  input_config.json
  validated_input.json
  advisor_checked_axes.json
  advisor_report.txt
  README.txt
  run.sh
  job.pbs
```

The builder copies the source engine into each generated case, computes
source hashes and protects existing **nonempty** output folders.
Generating inputs **never submits a PBS job** and **never executes ML/DFT**.

## 5. Review and run separately (optional)

Check `validated_input.json` and `advisor_report.txt`, available memory,
model checkpoint, fitted calculator domain and intended growth species.

Only **after deciding to actually run** on an allocated compute node,
the generated directory can be used with `bash run.sh` or, on a configured
PBS cluster, `qsub job.pbs`. These manual steps **do execute heavy scientific
calculations**; they are **not part of GitHub publication**.

## 6. Read progress without modifying the simulation

```bash
grown-input status software/GROWN_INPUT_BUILDER/examples/generated/graphene_X
```

When a `growth_log.csv` exists, status reports the accepted event count,
new deposited species and whether a final CIF is present. It does not
independently verify energetic reliability or force convergence.

## 7. Understand the stop condition

The `events` field is the **maximum number of accepted growth events**,
not the number of candidates evaluated. The engine can stop earlier
when the permitted finite template/front has no remaining eligible site.
For SiC-supported graphene the final diagnostic had `tested_energy=0`:
geometric screening exhausted the pool before energy evaluation. It is
incorrect to claim this demonstrates experimentally forbidden growth.

## 8. Dimensions, PBC and candidate templates

| Material class | Axis | PBC X,Y,Z |
|---|---|---|
| Monolayer graphene / MoS₂ (`2d`) | x | `010` |
| Si(100) or diamond (`3d`) | x | `011` |
| Layered slab (`layered`) | xz | `010` |
| Compact graphite AB (`layered_bulk`) | x | `011` |
| Compact graphite AB (`layered_bulk`) | y | `101` |
| Basal graphite AB growth (`layered_bulk`) | z | `110` |

PBC must be zero along every active growth axis. Monolayers may not grow
in Z in the `2d` category; changing the model to layered structures
requires physical redesign of the cell and template. Simultaneous growth
in XZ can be much more expensive than a single front and is recommended
for smaller cells.

## 9. Vacancies and dopants

```json
"impurities": {"vac": 0.10}
```

is a **per-event** vacancy probability; a skipped deposition site can
remain permanently vacant. Similarly `"impurities": {"N": 0.10}` gives a
stochastic substitutional N event probability, not exactly 10% N
concentration in the final full structure. The archived boron test used
`{"B": 0.09090909090909091}` (mean B:C approximately 1:10 for new events).

See [complete JSON reference](CONFIG_REFERENCE.md),
[paper examples](PAPER_EXAMPLES.md) and
[troubleshooting](TROUBLESHOOTING.md).
