# Scientific method, stopping rules and limitations

GROWN is a **template-guided configuration generator and
energy-ranked event engine**. It does not constitute an independent,
universally valid description of adsorption kinetics or interlayer
cohesion. The front direction and template are explicit inputs;
a crystal structure grown in the desired orientation is **not**
a proof of spontaneous orientation selection.

## Event loop at a glance

1. Read seed CIF, optional film/crystal template, selected growth axes,
   species, PBC, temperature and calculator.
2. Construct candidate sites in the permitted forward crystallographic
   columns; reject collisions, already occupied sites, inconsistent
   species, PBC/front conflicts and disallowed geometry/connectivity.
3. Compute model energy for geometrically eligible candidates, subject
   to any explicitly configured upper adsorption-energy threshold.
4. Select an event, locally relax and archive the accepted structure
   and per-event diagnostics.
5. Repeat until the accepted-event target is reached **or** no
   eligible candidate remains in the configured finite search domain.

The requested `events: 100` sets **at most 100 accepted events**, not
100 energy evaluations. In the source code the empty candidate case
logs `[STOP] nenhum candidato de deposição válido.`. Candidate
exhaustion may arise before any energy evaluation and **cannot** be
identified as an energetic barrier without further analysis.

## Distinct state labels

| State | Valid inference |
|---|---|
| Target attained, e.g. 100/100 | All requested accepted events recorded; final geometry and forces still need validation |
| Candidate-exhaustion stop, e.g. 20/96 | The finite specified template/front has no admissible site; may be expected algorithmic termination |
| Partial archival snapshot, e.g. 81/100 | The saved log does not establish how the job ultimately ended |

The CHGNet graphite AB Y case stopped at 24/100 because of an empty
eligible site pool. An **external exact-target checker** subsequently
raised an exception because fewer than 100 events had been recorded;
this is not necessarily a force-field calculation error. The CHGNet
XZ case was recorded running at 81/100 in the last archived scheduler
snapshot, and its later state is unknown.

## Directional energetic comparisons

A comparison of **relative energy trends** on X, Y and Z fronts
under a common selected calculator is useful for evaluating preferred
growth pathways. It is not an experimentally calibrated rate model,
nor a direct prediction of laboratory velocities or an activation
barrier for attachment. Actual growth may involve diffusion,
reconstruction, desorption, chemical reservoirs and nonequilibrium
thermodynamics absent from the simplified event model.

For corrected Bernal graphite with MACE the basal new-layer spacing is
3.360 Å. The frozen-geometry basal cleavage test gives +0.271 J/m²,
compared with the experimentally constrained ideal-AB reference
0.39 ± 0.02 J/m². This is encouraging sign/scale agreement at modest
model complexity, **not** within the experimental uncertainty.
The AB stacking registry is **input-imposed**. The CHGNet basal
cleavage test produces a nonphysical negative energy, indicating
transferability problems for the selected potential.

The experimental ideal-AB cleavage estimate is inferred from the
incommensurate-interface measurement and a theoretical correction:
Wang et al., *Nature Communications* **6**, 7853 (2015),
https://doi.org/10.1038/ncomms8853.

## Do not conflate

- model-dependent site scores, total energy differences, cohesion and
  reaction barriers;
- simulator flux time and experimental deposition/growth speeds;
- 100-event maximum and number of candidate geometries screened;
- complete event count and thermodynamic or geometric stability;
- geometrical template exhaustion and physical growth arrest;
- completed trajectories and logs frozen during cluster execution.

For all conclusions, report the calculator/checkpoint, exact model
version, PBC, seed, template, screening parameters, force convergence
and structural-quality flags.
