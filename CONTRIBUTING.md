# Contributing to GROWN

We welcome well-documented improvements to geometric validation,
input preparation, numerical consistency, portability and scientific
examples. This is research software: changes to the event engine can
alter published energetic or structural outcomes.

## Branch and review practice

1. Fork or create a topic branch (`feature/...`, `docs/...`, `fix/...`).
2. Keep source modifications isolated from new result trajectories.
3. Open a pull request describing motivation, scope, source files
   affected, expected scientific effect and changes to numerical output.
4. Require a human scientific review before changing defaults, PBC,
   candidate eligibility or calculator parameters.
5. For pure documentation, provide exact corresponding source examples
   and avoid invented paper data or DOIs.

## Lightweight checks (local only)

```bash
python -m compileall -q software/GROWN_INPUT_BUILDER
python -m unittest discover -s software/GROWN_INPUT_BUILDER/tests -v
```

The tests validate Input Builder behavior using real archived CIFs and
temporary generated files. They **do not execute energy-based crystal
growth** or submit PBS jobs. Do not enable any automatically scheduled
ML/DFT workflows on GitHub.

## Data and provenance

If you contribute a new material example, include an original ASE
readable CIF, JSON config, model/reference provenance and an explanation
of the accepted-event target versus any geometric/energy stop. Do not
commit multi-gigabyte trajectories, private cluster paths, tokens,
weights with noncompatible licenses or third-party scientific data
without permission. Store raw numerical results in an approved
external DOI-backed data repository when available.

## Coding and science

Use Python 3.10+ and documented dependencies. Preserve semantic input
validation; make a regression test for each geometry/CLI correction.
A valid CIF or completed event target is not itself physical validation.
Our design goal is **transparent scientific limits** rather than
guaranteed agreement with experiments.
