# Corrected graphite AB: Input Builder geometry checks

These three preserved example CIF seeds and JSON configurations were
originally used to inspect geometry in the graphite AB validation campaign.
They specify 30 accepted-event maximum **builder demonstrations**, not
the paper's separate 100-event production runs.

The CIFs contain a corrected 256-atom Bernal graphite cell. Compact periodic
Z is essential for prismatic X/Y growth (PBC 011 or 101); Z is nonperiodic
for basal growth (PBC 110).

After installing GROWN from the repository root:

~~~bash
grown-input validate experiments/AB_geometry_validation/builder_examples/graphite_AB_MACE_X.json
grown-input validate experiments/AB_geometry_validation/builder_examples/graphite_AB_MACE_Y.json
grown-input validate experiments/AB_geometry_validation/builder_examples/graphite_AB_MACE_Z.json
~~~

The examples have been sanitized only for public scheduler portability:
the original cluster queue and personal Conda activation were replaced by
null/empty values. No scientific data or model calculation was performed
by this documentation revision. For the **actual** 100-event case configs,
see ../../../examples/paper/graphite_ab/.
