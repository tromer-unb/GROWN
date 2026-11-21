# Troubleshooting

## `grown-input: command not found`
Activate the correct `venv`/Conda environment, then run
`python -m pip install -e .` from repository root. As a fallback:
`python software/GROWN_INPUT_BUILDER/grown_input.py --help`.

## `Missing input structure`
The builder resolves the `structure`/`template` paths relative to
the JSON file. Check that the referenced CIF is really present.

## `Output directory exists and is nonempty`
The builder refuses to overwrite scientific jobs. Use a unique
`run_directory` or deliberately archive/rename previous results.

## `Periodic axis z has no covalent neighbor`
You may be treating a vacuum-separated 2D slab as 3D bulk.
Use `dimension: 2d` or `layered` with open Z as appropriate. For
compact Bernal graphite with real periodic van der Waals contacts,
use `layered_bulk` with a physically correct Z seam.

## `Advisor rejects detached nucleation`
Check cell termination and connectivity. Detached basal-sheet
nucleation should only be enabled with a physically motivated
layered-bulk or layered-Z model, its own front cutoffs and a careful
follow-up geometry inspection.

## `No valid deposition candidate`
This is a **normal stopping rule** when the configured finite template
has no eligible site. It does not prove a barrier to physical growth.
Check `post_shell`, `tested_energy`, `template_extend_ncols`,
template alignment, front maximum distance and other constraints.
Do not simply loosen filters without physical justification.

## My run stopped at 24 although input said 100
`events: 100` means a *maximum* of 100 accepted events. Some source
monitoring wrappers separately expected exactly 100 and may raise
an exception on an otherwise normal candidate-exhaustion stop.
Read the engine log and wrapper exit cause separately.

## Model import errors / missing GLIBCXX / missing GPU
Model backends are external dependencies; set up a compatible PyTorch,
CUDA or compiler/`libstdc++` environment on the compute node. Confirm
the PBS job sees the environment. A generator-only test does not
exercise these libraries.

## `run.sh` runs locally but PBS fails
Review queue, environment activation, memory, file paths, `job.err`,
`simulation.log`, node-specific package visibility and compute-node
allocation. Do not run large MACE/CHGNet/GPAW workloads on login nodes.

## Reproduced energies differ from the manuscript
Compare checkpoint hashes, dispersion options, PBC, geometry and
relaxation, atomic energy reference, model versions and precision.
GROWN does not calibrate all potential models to a common reference.
