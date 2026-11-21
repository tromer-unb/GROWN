# Scientific input examples from the manuscript

**Provenance is explicit.** The repository carries curated CIF seeds,
original builder presets and selected source `run.sh` commands taken
from the research archive, not its ~134-MB full reproducibility bundle.
The underlying simulation engine and adviser sources are preserved.
These examples **will not execute** when viewed or cloned; the user
must explicitly run or submit generated scripts.

## Categories and source folders

| Example | Where | Nature of the supplied input |
|---|---|---|
| Graphite AB independent X, Y, Z (MACE) | [`examples/paper/graphite_ab/`](../examples/paper/graphite_ab/) | **100-event archived input_config.json**, with private paths/queue rewritten for portability; matching original C256 seeds |
| Graphene X and Si(100) X | [`software/.../examples/`](../software/GROWN_INPUT_BUILDER/examples/) | Original Input Builder `8-event` generation demonstrations |
| MoS₂ X | [`software/.../examples/`](../software/GROWN_INPUT_BUILDER/examples/) | Original Input Builder `8-event` demonstration |
| Graphite XZ, stochastic boron | [`software/.../examples/graphite_XZ_B.json`](../software/GROWN_INPUT_BUILDER/examples/graphite_XZ_B.json) and [archived runs](../examples/paper/graphite_boron/) | Builder demonstration plus original 500-event run commands |
| Graphene supported on MoS₂ | [`examples/paper/graphene_on_MoS2/`](../examples/paper/graphene_on_MoS2/) | Source heterostructure and film template, archived MACE/CHGNet X-run shell commands |
| Graphene supported on SiC | [`examples/paper/graphene_on_SiC/`](../examples/paper/graphene_on_SiC/) | Source film/substrate structure and film template, archived model X-run shell commands |
| Graphene vacancies and N substitution | [`examples/paper/graphene_defects/`](../examples/paper/graphene_defects/) | Original rectangular graphene structure, 10/20% vacancy and 10% N run commands, MACE/CHGNet |
| Historical 72-case material survey | [`historical_72_case_matrix.csv`](../examples/paper/historical_72_case_matrix.csv) | Archived original state/metadata matrix; not 72 full trajectories |
| Graphite AB builder X/Y/Z controls | [`experiments/AB_geometry_validation/builder_examples/`](../experiments/AB_geometry_validation/builder_examples/) | Original 30-event builder preflight cases with portable PBS settings |

## Graphite AB: exact 100-event parameter cases

The **actual scientific 100-event configurations** were copied from
`experiments/graphite_AB100/runs/MACE/{X,Y,Z}/input_config.json` in
the complete source archive. We changed only the **input CIF path** to
the bundled filename, the **output run directory** to a local relative
path, and the **PBS queue/environment activation** to portable values.
Physical settings remain from the archived records, including MACE-small,
500 K, 100 accepted events, seed 490596, 12 local relaxation steps,
32 additional columns, and the orientation-specific PBC/column period.

```bash
grown-input validate examples/paper/graphite_ab/graphite_AB100_MACE_X.json
grown-input validate examples/paper/graphite_ab/graphite_AB100_MACE_Y.json
grown-input validate examples/paper/graphite_ab/graphite_AB100_MACE_Z.json
```

This **does not** recompute the paper simulations; version/model matching
and exact wrapper instrumentation are additional conditions for
bitwise reproduction. The original 100-event MACE X/Y/Z trajectories
in the research archive completed their maximum accepted event count.

## Graphene over substrates: actual archived scripts

The heterostructure examples are **original paper input command
snapshots**, not silently reconstructed builder configurations.
Both models completed 160/160 carbon additions on MoS₂, but independent
fixed-substrate relaxation retained 17 short C–C contact flags. Over SiC,
MACE terminated after 20/96 and CHGNet after 40/96 with no available
**geometrically eligible site**; final energy-tested site count was
zero. These are normal finite-template stops, not verified
energetically forbidden growth.

## Graphite defects and boron

For the 500-event graphene defect examples, `vac10p` and `vac20p`
denote vacancy probabilities at future growth events; `N10p` denotes
a nitrogen substitutional event probability. The final composition
is stochastic. For boron on the XZ graphite front, the model used
`--impurity B 0.09090909090909091`, meaning a random mean ~1 B for
10 C events, not deterministic positioning. The archived B production
trajectories were only partially complete at the frozen snapshot.

## Multi-axis computational scaling

The archived graphite XY/XZ/YZ MACE demonstrations reached 100/100
accepted events, but the XZ case required 33,114 screened candidates
for 100 events versus 1,173 for independent X growth. We recommend
combined-direction growth primarily for **small research cells**
unless the front-competition question justifies substantially more
computation.

## Important distinction: files here vs complete reproduction

Some provided paper-case shell commands are **source snapshots** rather
than new CLI-generated runs. They are kept to show *what was actually
configured*; do not infer they are platform independent. The full
scientific archive also contains the original logs, trajectories,
energy tables, potential records, failures and partially saved runs,
and remains separate from GitHub until an approved DOI-backed data
release exists. See [Reproducibility](REPRODUCIBILITY.md).
