# GROWN Input Builder — scientific source code (v0.1)

The three original Python modules in this folder implement the interactive
input builder, event engine and geometry adviser. The source modules have been
preserved from the research archive. The root `pyproject.toml` exposes the
`grown-input` command without requiring modification of the simulation engine.

The CLI has four commands: `init`, `validate`, `generate` and `status`.
**Only manual execution of generated job scripts launches growth.** The
`generate` command creates local files and an optional PBS script; it does not
execute ML/DFT, submit work or download checkpoints.

See [installation](../../docs/INSTALLATION.md),
[user guide](../../docs/INPUT_BUILDER.md),
[configuration schema](../../docs/CONFIG_REFERENCE.md) and
[scientific cases](../../docs/PAPER_EXAMPLES.md).
