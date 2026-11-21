# Graphite AB 100-event MACE inputs: source fidelity

Each `graphite_AB100_MACE_{X,Y,Z}.json` was copied from the **actual
100-event source** at
`experiments/graphite_AB100/runs/MACE/{X,Y,Z}/input_config.json`.
The corresponding archived crystal seeds were copied without modification
as `AB_C256_X.cif`, `AB_C256_Y.cif` and `AB_C256_Z.cif`.

Only these fields were changed relative to the original archived JSON:

| Field | Change in public example | Reason |
|---|---|---|
| `structure` | Absolute laboratory CIF path → local `AB_C256_AXIS.cif` | Portable relative seed |
| `run_directory` | Absolute laboratory output → `generated/graphite_AB100_MACE_AXIS` | No private folder/overwrite |
| `pbs_queue` | `workq` → `null` | Original LCCMat queue is not portable |
| `env_activation` | Lab-specific Conda activation → empty string | No hard-coded personal paths |

All physically relevant and stochastic settings (growth axis,
`events: 100`, 500 K, seed 490596, template periods and front,
model alias, local relax steps, PBC and reservoir/flux settings)
remain from the original input JSON. These inputs are **not**
promises of bitwise identical output without exact source
checkpoint/library/environment matching.
