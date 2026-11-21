#!/usr/bin/env python3
"""Input builder smoke/regression tests (no ML, no PBS, never submit)."""
from pathlib import Path
import json,shlex,sys,unittest,tempfile
B=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(B))
import grown_input as m
class Tests(unittest.TestCase):
 def test_automatic_pbc(self):
  self.assertEqual(m.choose_pbc("2d","x"),[0,1,0])
  self.assertEqual(m.choose_pbc("2d","y"),[1,0,0])
  self.assertEqual(m.choose_pbc("2d","xy"),[0,0,0])
  self.assertEqual(m.choose_pbc("3d","x"),[0,1,1])
  self.assertEqual(m.choose_pbc("3d","xy"),[0,0,1])
  self.assertEqual(m.choose_pbc("layered","xz"),[0,1,0])
 def test_2d_z_rejected(self):
  with self.assertRaises(ValueError):
   m.choose_pbc("2d","xz")
 def test_bad_periodic_vacuum_rejected(self):
  cfgpath=B/"examples/graphene_X.json"
  raw=json.loads(cfgpath.read_text())
  raw["dimension"]="3d"
  raw["pbc_override"]=[0,1,1]
  c,_=m.check_config(raw,cfgpath)
  with self.assertRaisesRegex(ValueError,"Periodic axis z has no covalent neighbor"):
   m.structure_validation(c)
 def test_no_output_overwrite(self):
  with tempfile.TemporaryDirectory(prefix="grown_test_") as td:
   out=Path(td)/"occupied"
   out.mkdir()
   (out/"keep.txt").write_text("do not overwrite")
   cfg=B/"examples/graphene_X.json"
   raw=json.loads(cfg.read_text())
   raw["structure"]=str(B/"examples/graphene_C128_periodicY.cif")
   raw["run_directory"]=str(out)
   config_path=Path(td)/"case.json"
   config_path.write_text(json.dumps(raw))
   with self.assertRaisesRegex(ValueError,"nonempty"):
    m.generate(config_path)
 def test_graphite_layered_B_flags(self):
  p=B/"examples/graphite_XZ_B.json"
  cfg,_=m.check_config(json.loads(p.read_text()),p)
  cmd=m.generated_command(cfg,"graphite_442_rectangular.cif","graphite_442_rectangular.cif",m.ENGINE.name)
  for flag,value in (("--growth-axis","xz"),("--impurity","B")):
   self.assertEqual(cmd[cmd.index(flag)+1],value)
  idx=cmd.index("--pbc")
  self.assertEqual(cmd[idx+1:idx+4],["0","1","0"])
  self.assertEqual(cmd[cmd.index("--impurity")+2],"0.09090909090909091")
 def test_hetero_growing_species_site_matching(self):
  c,_=m.check_config(json.loads((B/"examples/graphene_on_MoS2_X.json").read_text()),
                           B/"examples/graphene_on_MoS2_X.json")
  report=m.structure_validation(c)
  self.assertEqual(report["composition"],{"Mo":112,"S":224,"C":108})
  self.assertEqual(report["pbc"],[0,1,0])
  self.assertGreater(report["periodic_bond_seams"]["y"],0)
 def test_generated_pbs_and_input_files(self):
  cfg0=B/"examples/graphene_X.json"
  raw=json.loads(cfg0.read_text())
  with tempfile.TemporaryDirectory(prefix="grown_test_") as td:
   raw["structure"]=str(B/"examples/graphene_C128_periodicY.cif")
   raw["run_directory"]=str(Path(td)/"generated_case")
   cfg=Path(td)/"graphene_case.json"
   cfg.write_text(json.dumps(raw))
   m.generate(cfg)  # creates scripts and preflight only; NO model run or scheduler submission
   out=Path(raw["run_directory"])
   for name in ("job.pbs","advisor_report.txt","validated_input.json","run.sh",
                "mc_flux_corrigido_multiaxis_v4.py"):
    self.assertTrue((out/name).is_file(),name)
   d=json.loads((out/"validated_input.json").read_text())
   self.assertEqual(d["geometry"]["pbc"],d["config"]["resolved_pbc"])
if __name__=="__main__":unittest.main(verbosity=2)
