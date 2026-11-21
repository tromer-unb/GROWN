#!/usr/bin/env python3
"""Regression tests for layered_bulk graphite van der Waals periodic seam."""
from pathlib import Path
import sys,unittest,json,tempfile
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import grown_input as m
EX=ROOT.parents[1]/'experiments/AB_geometry_validation/builder_examples'
class LayeredBulk(unittest.TestCase):
 def test_pbc_modes(self):
  self.assertEqual(m.choose_pbc('layered_bulk','x'),[0,1,1])
  self.assertEqual(m.choose_pbc('layered_bulk','y'),[1,0,1])
  self.assertEqual(m.choose_pbc('layered_bulk','z'),[1,1,0])
  self.assertEqual(m.choose_pbc('layered','x'),[0,1,0])
 def test_real_AB_XY_interlayer_PBC(self):
  for ax in 'XY':
   conf=EX/f'graphite_AB_MACE_{ax}.json'
   raw=json.loads(conf.read_text());raw['dimension']='layered_bulk'
   c,_=m.check_config(raw,conf)
   out=m.structure_validation(c)
   self.assertEqual(out['atoms'],256)
   self.assertGreater(out['periodic_vdw_seam_contacts']['z'],0)
   self.assertEqual(out['pbc'],[0,1,1] if ax=='X' else [1,0,1])
 def test_refuse_large_Z_vacuum(self):
  conf=ROOT/'examples/graphene_X.json'
  raw=json.loads(conf.read_text());raw['dimension']='layered_bulk'
  c,_=m.check_config(raw,conf)
  with self.assertRaisesRegex(ValueError,'interlayer neighbors across seam'):
   m.structure_validation(c)
 def test_Z_nucleation_PBC(self):
  conf=EX/'graphite_AB_MACE_Z.json'
  raw=json.loads(conf.read_text());raw['dimension']='layered_bulk'
  c,_=m.check_config(raw,conf)
  out=m.structure_validation(c)
  self.assertEqual(out['pbc'],[1,1,0])
 def test_real_vdw_contact_at_4p5_angstrom(self):
  # This must work beyond the previous global neighbor cutoff 3.6 A.
  from ase.io import read,write
  conf=EX/'graphite_AB_MACE_X.json'
  raw=json.loads(conf.read_text());raw['dimension']='layered_bulk'
  with tempfile.TemporaryDirectory() as tmp:
   atoms=read(EX/'AB_compact_X_seed_256.cif')
   atoms.positions[:,2]*=(4.5/3.35)
   cell=atoms.cell.array.copy()
   cell[2,2]=18.0
   atoms.set_cell(cell,scale_atoms=False)
   path=Path(tmp)/'AB_d4p5.cif'
   write(path,atoms,format='cif')
   raw['structure']=str(path)
   c,_=m.check_config(raw,conf)
   out=m.structure_validation(c)
   self.assertGreater(out['periodic_vdw_seam_contacts']['z'],0)
if __name__=='__main__':unittest.main(verbosity=2)
