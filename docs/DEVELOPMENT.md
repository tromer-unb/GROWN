# Developer notes

The public project intentionally retains the archive's **flat Python
module layout** to minimize scientific source changes:

```text
software/GROWN_INPUT_BUILDER/
  grown_input.py                              # CLI and geometry preflight
  mc_flux_corrigido_multiaxis_v4.py          # atomistic event engine
  growth_parameter_advisor_corrected_multiaxis_v4.py
  examples/                                   # 5 source JSONs + CIFs
  tests/                                      # unit/regression tests
experiments/AB_geometry_validation/builder_examples/
examples/paper/                               # curated actual manuscript cases
docs/
pyproject.toml
environment.yml
```

`pyproject.toml` installs these three Python modules and the
`grown-input` console entry point. New abstraction layers should
be introduced with test coverage rather than making silent
physics-altering refactors of the preserved research engine.

Running `python -m unittest discover -s
software/GROWN_INPUT_BUILDER/tests -v` is a **local,
input-preparation-only** check and does not compute growth with
MACE/CHGNet/GPAW. There are **no GitHub Actions workflows**.

For any scientific change, document whether it changes a numerical
result, calculator defaults, candidate geometry, force model,
termination logic or files needed to reproduce the manuscript.
