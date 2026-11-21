#!/usr/bin/env python3
"""GROWN Input Builder v0.1: interactive, JSON-driven, portable ASE/MLIP growth inputs.

Examples:
  python grown_input.py init
  python grown_input.py validate examples/graphene_X.json
  python grown_input.py generate examples/graphene_X.json
  python grown_input.py status examples/output_graphene_X

Generates only job.pbs/run.sh/inputs; NEVER runs ML/DFT or submits jobs.
Interface designed for scientists unfamiliar with the 110 flags of engine v4.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,shlex,shutil,subprocess,sys,tempfile
from pathlib import Path
from collections import Counter
from dataclasses import dataclass
from typing import Any
from math import isfinite
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.data import atomic_numbers,covalent_radii
import numpy as np

ROOT=Path(__file__).resolve().parent
ENGINE=ROOT/"mc_flux_corrigido_multiaxis_v4.py"
ADVISOR=ROOT/"growth_parameter_advisor_corrected_multiaxis_v4.py"
BACKENDS=("chgnet","mace","gpaw","emt","lj","sevennet","mattersim")
DIMENSIONS=("2d","3d","layered","layered_bulk")
AXES=("x","y","z","xy","xz","yz","xyz")
SUPPORTED_KEYS={
 "name","structure","template","dimension","growth_axis","backend","deposition_species",
 "temperature_K","flux_ML_s","events","seed","relax_steps","fmax_eV_A","mobile_radius_A",
 "template_build_mode","template_extend_ncols","template_column_period","template_column_tol_A",
 "template_front_max_A","template_connect_cutoff_A","min_dist_A","template_occupancy_tol_A",
 "template_min_neighbors","template_front_mode","growth_direction","template_species_mode",
 "growth_origin_species","restrict_Z_fraction","impurities","pbc_override","run_directory",
 "pbs_queue","pbs_memory","pbs_cores","env_activation","mace_model","gpaw_mode","gpaw_basis",
 "gpaw_kpts","gpaw_xc","advanced_args","enable_advisor_report"
}
DEFAULT={
 "name":"example","structure":"SEED.cif","template":None,
 "dimension":"2d","growth_axis":"x","backend":"chgnet","deposition_species":["C"],
 "temperature_K":500,"flux_ML_s":0.001,"events":20,"seed":490596,
 "relax_steps":6,"fmax_eV_A":0.05,"mobile_radius_A":4.5,
 "template_build_mode":"extend-columns","template_extend_ncols":12,
 "template_column_period":2,"template_column_tol_A":0.2,
 "template_front_max_A":3.5,"template_connect_cutoff_A":1.9,
 "min_dist_A":1.0,"template_occupancy_tol_A":0.65,
 "template_min_neighbors":1,"template_front_mode":"shell","growth_direction":"plus",
 "template_species_mode":"template","growth_origin_species":None,"restrict_Z_fraction":None,
 "impurities":{},"pbc_override":None,"run_directory":"run_example",
 "pbs_queue":None,"pbs_memory":"16gb","pbs_cores":1,"env_activation":"",
 "mace_model":"small","gpaw_mode":"lcao","gpaw_basis":"dzp","gpaw_kpts":[1,1,1],
 "gpaw_xc":"PBE","advanced_args":[],"enable_advisor_report":True
}
RESERVED_ARGS={x for x in (
 "--cif","--template-cif","--pbc","--growth-axis","--steps","--backend",
 "--species","--out","--log","--site-mode","--build-mode","--impurity",
 "--template-site-species","--growth-origin-species"
)}

def canonical_path(base:Path, raw:str|Path)->Path:
 p=Path(raw).expanduser()
 return (p if p.is_absolute() else base/p).resolve()

def hashfile(path:Path)->str:
 return hashlib.sha256(path.read_bytes()).hexdigest()

def choose_pbc(dimension:str,axis:str)->list[int]:
 if dimension=="2d":
  if "z" in axis:raise ValueError("Monocamada 2D: crescimento em Z é proibido. Se deseja várias camadas, selecione 'layered'.")
  return [0 if "x" in axis else 1,0 if "y" in axis else 1,0]
 if dimension=="layered":
  return [0 if "x" in axis else 1,0 if "y" in axis else 1,0]
 # For 3D a non-growing axis is periodic; this may DIFFER from old PAPER_2 XY=000 presets.
 return [int(ax not in axis) for ax in "xyz"]

def check_config(cfg:dict, config_path:Path)->tuple[dict,list[str]]:
 if not isinstance(cfg,dict):raise ValueError("JSON config must contain one object.")
 unknown=set(cfg)-SUPPORTED_KEYS
 if unknown:raise ValueError("Unrecognized settings: "+", ".join(sorted(unknown)))
 c={**DEFAULT,**cfg}
 for k in ("name","structure","dimension","growth_axis","backend","run_directory"):
  if not isinstance(c[k],str) or not c[k].strip():raise ValueError(f"{k} is required.")
 c["growth_axis"]=c["growth_axis"].lower().strip()
 c["backend"]=c["backend"].lower().strip()
 c["dimension"]=c["dimension"].lower().strip()
 if c["dimension"] not in DIMENSIONS:raise ValueError("dimension must be 2d, 3d, layered or layered_bulk")
 if c["growth_axis"] not in AXES:raise ValueError("growth_axis must be x, y, z, xy, xz, yz or xyz")
 if c["backend"] not in BACKENDS:raise ValueError("backend not supported: "+c["backend"])
 if c["dimension"]=="2d" and "z" in c["growth_axis"]:raise ValueError("Cannot grow in Z for a monolayer.")
 if not isinstance(c["deposition_species"],list) or not c["deposition_species"]:
  raise ValueError("deposition_species must be nonempty list, e.g. ['Mo','S']")
 for el in c["deposition_species"]:
  if el not in atomic_numbers:raise ValueError("Unknown chemical symbol: "+str(el))
 for k in ("events","seed","relax_steps","template_extend_ncols","template_column_period",
           "template_min_neighbors","pbs_cores"):
  if isinstance(c[k],bool) or not isinstance(c[k],int) or c[k]<0:
   raise ValueError(k+" must be non-negative integer")
 if c["events"]==0 or c["pbs_cores"]==0 or c["template_column_period"]==0:raise ValueError("events, pbs_cores and template_column_period must be positive")
 for k in ("temperature_K","flux_ML_s","mobile_radius_A","fmax_eV_A",
           "template_column_tol_A","template_front_max_A","template_connect_cutoff_A",
           "min_dist_A","template_occupancy_tol_A"):
  if not isinstance(c[k],(int,float)) or not isfinite(c[k]) or c[k]<=0:raise ValueError(k+" must be a finite positive number")
 if c["temperature_K"]>8000:raise ValueError("Temperature appears invalid (>8000 K).")
 if c["template_build_mode"] not in ("repeat","extend-columns"):raise ValueError("template_build_mode must be repeat or extend-columns")
 if c["template_species_mode"] not in ("template","command"):raise ValueError("template_species_mode must be template or command")
 if c["template_front_mode"] not in ("shell","global","all_connected"):raise ValueError("Invalid template_front_mode")
 if c["growth_direction"] not in ("plus","minus","both"):raise ValueError("growth_direction must be plus, minus, both")
 if c["restrict_Z_fraction"] is not None:
  if not isinstance(c["restrict_Z_fraction"],(int,float)) or not 0<c["restrict_Z_fraction"]<1:raise ValueError("restrict_Z_fraction is a cell fraction between 0 and 1")
 if c["growth_origin_species"] is not None:
  if not isinstance(c["growth_origin_species"],list) or not all(el in atomic_numbers for el in c["growth_origin_species"]):raise ValueError("growth_origin_species must be list of valid chemical symbols")
 if not isinstance(c["impurities"],dict):raise ValueError("impurities must be a dict: {'B':0.09,'vac':0.1}")
 if any(not isinstance(v,(float,int)) or not 0<=v<=1 for v in c["impurities"].values()):raise ValueError("Impurity probabilities must be in [0,1]")
 if sum(c["impurities"].values())>1.000000001:raise ValueError("Sum of impurity probabilities > 1")
 for el in c["impurities"]:
  if el!="vac" and el not in atomic_numbers:raise ValueError("Unknown impurity: "+str(el))
 if not isinstance(c["advanced_args"],list) or not all(isinstance(x,str) for x in c["advanced_args"]):raise ValueError("advanced_args must be list of strings")
 if any(x in RESERVED_ARGS for x in c["advanced_args"]):raise ValueError("advanced_args cannot override essential input/safety flags")
 if c["pbc_override"] is not None:
  if not isinstance(c["pbc_override"],list) or len(c["pbc_override"])!=3 or any(x not in (0,1) for x in c["pbc_override"]):raise ValueError("pbc_override must be [0,1,0] or equivalent three 0/1 entries")
  pbc=list(map(int,c["pbc_override"]))
 else:pbc=choose_pbc(c["dimension"],c["growth_axis"])
 for idx,ax in enumerate("xyz"):
  if ax in c["growth_axis"] and pbc[idx]==1:
   raise ValueError(f"Growth along {ax} cannot be periodic; pbc[{idx}]=1 conflicts.")
 if c["dimension"]=="2d" and pbc[2]:raise ValueError("2D monolayer must have vacuum/nonperiodic Z")
 if c["dimension"]=="layered" and "z" not in c["growth_axis"] and pbc[2]:
  raise ValueError("Layered slab with growth only lateral should not repeat vacuum Z")
 if c["dimension"]=="layered_bulk" and not pbc[2] and "z" not in c["growth_axis"]:
  raise ValueError("layered_bulk lateral growth requires periodic Z and compact interlayer cell. For Z-vacuum slab use dimension layered.")
 c["resolved_pbc"]=pbc
 dirname=Path(c["run_directory"])
 if len(dirname.parts)==0 or dirname==Path("."):raise ValueError("run_directory cannot be current directory")
 c["resolved_structure"]=str(canonical_path(config_path.parent,c["structure"]))
 c["resolved_template"]=str(canonical_path(config_path.parent,c["template"] or c["structure"]))
 c["resolved_run_directory"]=str(canonical_path(config_path.parent,c["run_directory"]))
 for item in ("resolved_structure","resolved_template"):
  if not Path(c[item]).is_file():raise ValueError(f"Missing input structure {c[item]}")
 if c["backend"]=="gpaw":
  if c["gpaw_mode"] not in ("lcao","pw","fd"):raise ValueError("GPAW mode invalid")
  if not isinstance(c["gpaw_kpts"],list) or len(c["gpaw_kpts"])!=3 or any(not isinstance(x,int) or x<=0 for x in c["gpaw_kpts"]):raise ValueError("gpaw_kpts must be [1,1,1] etc.")
 warnings=[]
 if c["template_build_mode"]=="extend-columns":
  warnings.append("Column extension is heuristic; inspect the advisor report and the first proposed bonds before long runs.")
 if c["dimension"]=="3d" and len(c["growth_axis"])>1:
  warnings.append("For bulk 3D, auto PBC keeps non-growing axes periodic (e.g. XY => 001). Historical PAPER_2 multidirectional runs may have PBC=000; use explicit pbc_override to reproduce them.")
 if c["impurities"]:
  warnings.append("Impurity ratio is stochastic per future deposition site; it is not exact final stoichiometry.")
 if c["backend"]=="gpaw":
  warnings.append("GPAW can be far slower than MLIPs. LCAO basis and k-points require convergence checks; available basis data must be installed.")
 if c["env_activation"] and ("\n" in c["env_activation"] or "\r" in c["env_activation"]):
  raise ValueError("env_activation must be a single trusted shell line")
 return c,warnings

def structure_validation(c:dict)->dict:
 import warnings as warnings_module
 with warnings_module.catch_warnings():
  warnings_module.simplefilter("ignore",FutureWarning)
  atoms=read(c["resolved_structure"])
  template=read(c["resolved_template"])
 if len(atoms)==0 or len(template)==0:raise ValueError("Empty input structure/template")
 pbc=np.array(c["resolved_pbc"],dtype=bool)
 atoms.pbc=pbc;template.pbc=pbc
 if not np.allclose(np.array(atoms.cell.lengths())[pbc],
                     np.array(template.cell.lengths())[pbc],atol=.03,rtol=0):
  raise ValueError("Seed/template mismatch in periodic transverse cell lengths (strain/commensurability).")
 if c["dimension"]=="2d" and atoms.cell.lengths()[2]<8.:
  raise ValueError("2D Z cell <8 A: seems insufficient vacuum.")
 initial_elements=Counter(atoms.get_chemical_symbols())
 templ_elements=Counter(template.get_chemical_symbols())
 for s in c["deposition_species"]:
  if s not in templ_elements:
   raise ValueError("Growing species "+s+" has NO sites in template CIF.")
 sym=atoms.get_chemical_symbols()
 # Element-dependent no-unphysical-collision gate: safely below a typical bond length.
 radius=np.array([covalent_radii[atomic_numbers[s]] for s in sym])
 maxr=float(np.max(radius))
 cutoff=max(3.6,2.65*maxr,5.0 if c["dimension"]=="layered_bulk" and pbc[2] else 0.0)
 i,j,d,vec=neighbor_list("ijdD",atoms,cutoff)
 if len(d)==0:raise ValueError("No atomic pairs found; check CIF and supercell.")
 excl0=(i<j)
 ij=np.flatnonzero(excl0)
 # For self-images (same atom periodic), ASE neighbor_list includes i==j;
 # check those as well (short cell self-overlap).
 short_ids=np.flatnonzero(d < (radius[i]+radius[j])*0.58)
 if len(short_ids):
  k=int(short_ids[0]);raise ValueError(f"Unphysical short contact: {sym[int(i[k])]}-{sym[int(j[k])]} {d[k]:.3f} A (atoms {i[k]},{j[k]}); fix cell/seams.")
 seams={}
 vdw_seam_contacts={}
 for dim,v in enumerate(pbc):
  if not v:continue
  direct=atoms.positions[j]-atoms.positions[i]
  wrap=np.abs(vec[:,dim]-direct[:,dim])>.25
  # Use a bonded-neighbor threshold; avoid counting far periodic images:
  bonded=d<1.40*(radius[i]+radius[j])
  n=int(np.sum(wrap&bonded))//2
  seams["xyz"[dim]]=n
  if n==0:
   # EXPLICIT checked exception for van der Waals periodic layered BULK
   # along Z (graphite AB d=3.35 A, no covalent C-C bonds between layers).
   # Do not allow empty seams without real interlayer neighbor contacts.
   if c["dimension"]=="layered_bulk" and dim==2:
    vdw=wrap & (d>=2.5) & (d<=5.0)
    n_vdw=int(np.sum(vdw))//2
    if n_vdw<1:
     raise ValueError("layered_bulk z periodicity has no interlayer neighbors across seam within 2.5-5.0 A; this appears to be vacuum.")
    vdw_seam_contacts["z"]=n_vdw
   else:
    raise ValueError(f"Periodic axis {'xyz'[dim]} has no covalent neighbor crossing seam. This is likely an open/incorrect cell. Make periodic supercell, or explicitly choose nonperiodic PBC.")
 volume=float(atoms.get_volume())
 if volume<=0:raise ValueError("Invalid cell volume.")
 if c["restrict_Z_fraction"] is not None:
  threshold=c["restrict_Z_fraction"]*atoms.cell.lengths()[2]
  selected=[s for s,x in zip(sym,atoms.positions[:,2]) if x>=threshold]
  if not selected:raise ValueError("restrict_Z_fraction excludes ALL growth-front atoms.")
  if not any(s in c["deposition_species"] for s in selected):raise ValueError("No eligible growth element above restrict_Z cutoff.")
 # When substrate and growth template differ, validate growth-layer atoms
 # against the actual candidate-site lattice, including transverse PBC copies.
 growth_indices=[i for i,s in enumerate(sym) if s in c["deposition_species"]]
 if c["restrict_Z_fraction"] is not None:
  threshold=c["restrict_Z_fraction"]*atoms.cell.lengths()[2]
  growth_indices=[i for i in growth_indices if atoms.positions[i,2]>=threshold]
 if c["resolved_template"]!=c["resolved_structure"]:
  if not growth_indices:raise ValueError("No growth-front atoms found in seed.")
  from scipy.spatial import cKDTree
  tpositions=np.array(template.positions)
  tsymbols=np.array(template.get_chemical_symbols())
  for sp in c["deposition_species"]:
   selected=[i for i in growth_indices if sym[i]==sp]
   if not selected:continue
   temp=tpositions[tsymbols==sp]
   if not len(temp):raise ValueError("No template sites for "+sp)
   images=[temp]
   for ax,v in enumerate(pbc):
    if v:
     vector=np.array(template.cell.array[ax])
     images+=[temp+vector,temp-vector]
   matchdist,_=cKDTree(np.vstack(images)).query(atoms.positions[selected],k=1)
   if float(np.max(matchdist))>.08:
    raise ValueError(f"Seed/template mismatch for growing element {sp}: max distance {np.max(matchdist):.3f} A. Correct the interface/strain/template.")
 # Do not pretend top-front geometry is validated solely from seam checks.
 return {"atoms":len(atoms),"template_atoms":len(template),
  "composition":dict(initial_elements),"template_composition":dict(templ_elements),
  "pbc":list(map(int,pbc)),"periodic_bond_seams":seams,
  "periodic_vdw_seam_contacts":vdw_seam_contacts,
  "minimum_pair_distance_A":round(float(np.min(d)),5),
  "cell_lengths_A":[round(float(x),5) for x in atoms.cell.lengths()],
  "cell_angles_deg":[round(float(x),3) for x in atoms.cell.angles()],
  "source_sha256":hashfile(Path(c["resolved_structure"])),
  "template_sha256":hashfile(Path(c["resolved_template"]))}

def advisor_validate(c:dict)->tuple[list[dict],list[str]]:
 """Reject extrapolation of genuinely detached layers except explicit layered-Z nucleation."""
 if not ADVISOR.is_file() or not c["enable_advisor_report"]:
  return [],["Advisor not run. Future template connectivity is UNVERIFIED."]
 with tempfile.TemporaryDirectory() as tmp:
  result=Path(tmp)/"advisor.json"
  # For a heterostructure, the advisor should examine the GROWING lattice,
  # not substrate elements that do not participate in the graphene front.
  # The seed/template overlap is independently checked below.
  adv_structure=(c["resolved_template"] if
      c["resolved_structure"]!=c["resolved_template"] else c["resolved_structure"])
  command=[sys.executable,str(ADVISOR),"--structure",adv_structure,
   "--template",c["resolved_template"],"--axis",c["growth_axis"],
   "--growth-direction",c["growth_direction"],"--species",*c["deposition_species"],
   "--json",str(result),"--quiet-command"]
  completed=subprocess.run(command,capture_output=True,text=True,timeout=90)
  if completed.returncode or not result.is_file():
   raise ValueError("Advisor failed; inspect your CIF/template. "+completed.stderr[-600:])
  rep=json.loads(result.read_text())
  axes=rep.get("axes",[])
 if not axes:raise ValueError("Advisor returned zero growth axes")
 warnings=[]
 for entry in axes:
  axis=entry["axis"]
  mode=entry.get("interface_mode","unknown")
  med=entry.get("first_future_dmin_median_A")
  periodic=entry.get("structural_period")
  print(f"  Advisor axis {axis}: mode={mode}, next-bond={med} A, suggested-column-period={periodic}")
  if mode=="detached-layer-nucleation":
   if c["dimension"] in ("layered","layered_bulk") and axis=="z":
    warnings.append("Layered-Z growth may start as detached-layer nucleation. Auto-set minimum neighbors in Z=0; isolated atom/slow nucleation risk, monitor physically.")
   else:
    raise ValueError(f"Advisor rejects {axis} as detached nucleation; correct cell termination/template or choose a physically meaningful layered-Z system.")
  elif mode not in ("covalent-continuation","bonded-continuation"):
   warnings.append(f"Advisor growth mode for {axis} is {mode}; examine the report before scientific conclusions.")
  if c["template_column_period"]!=periodic and len(axes)==1 and c["template_build_mode"]=="extend-columns":
   warnings.append(f"Column period {c['template_column_period']} differs from advisor recommendation {periodic}; verify before long jobs.")
 return axes,warnings

def validate_config(path:Path):
 raw=json.loads(path.read_text(encoding="utf-8"))
 c,warnings=check_config(raw,path)
 geometry=structure_validation(c)
 axes,adv_warnings=advisor_validate(c)
 c["advisor_axes"]=axes
 warnings.extend(adv_warnings)
 print("PREFLIGHT geometry: OK (bond seam and short-contact checks; advisor checked if enabled)")
 print("  seed atoms:",geometry["atoms"],"composition:",geometry["composition"])
 print("  template sites:",geometry["template_atoms"],"composition:",geometry["template_composition"])
 print("  growth axis:",c["growth_axis"],"PBC:",geometry["pbc"],"seam bonds:",geometry["periodic_bond_seams"])
 print("  min pair distance:",geometry["minimum_pair_distance_A"],"A; cell:",geometry["cell_lengths_A"])
 print("  backend:",c["backend"],"steps:",c["events"],"temperature:",c["temperature_K"])
 for warn in warnings:print("WARNING:",warn)
 return c,geometry,warnings

def generated_command(c:dict, seed_name:str, template_name:str, engine_name:str)->list[str]:
 args=["python3","-u",engine_name,
   "--cif",seed_name,"--species",*c["deposition_species"],
   "--backend",c["backend"],"--backend-device","cpu",
   "--build-mode","direct","--growth-axis",c["growth_axis"],
   "--pbc",*map(str,c["resolved_pbc"]),
   "--replicate","1","1","1","--vacuum","0",
   "--site-mode","template","--template-cif",template_name,
   "--template-species-mode",c["template_species_mode"],
   "--template-site-species",*c["deposition_species"],
   "--growth-origin-species",*(c["growth_origin_species"] or c["deposition_species"]),
   "--template-build-mode",c["template_build_mode"],
   "--template-repeat","1","1","1",
   "--template-extend-ncols",str(c["template_extend_ncols"]),
   "--template-column-period",str(c["template_column_period"]),
   "--template-column-tol",str(c["template_column_tol_A"]),
   "--template-debug",
   "--template-growth-direction",c["growth_direction"],
   "--template-front-mode",c["template_front_mode"],
   "--template-layer-tol","0.35",
   "--template-front-min","0.05",
   "--template-front-max",str(c["template_front_max_A"]),
   "--template-occupancy-tol",str(c["template_occupancy_tol_A"]),
   "--template-connect-cutoff",str(c["template_connect_cutoff_A"]),
   "--template-min-neighbors",str(c["template_min_neighbors"]),
   "--min-dist",str(c["min_dist_A"]),
   "--cn-cutoff",str(c["template_connect_cutoff_A"]),
   "--match-cell-to-template","--cell-growth-margin","6",
   "--skip-bulk-reference",
   "--relax-steps",str(c["relax_steps"]),
   "--fmax",str(c["fmax_eV_A"]),
   "--mobile-radius",str(c["mobile_radius_A"]),
   "--steps",str(c["events"]),
   "--temperature",str(c["temperature_K"]),
   "--flux-ML-s",str(c["flux_ML_s"]),
   "--seed",str(c["seed"]),
   "--out","growth.traj","--log","growth_log.csv"]
 if c["restrict_Z_fraction"] is not None:args+=["--restrict-Z",str(c["restrict_Z_fraction"])]
 if c["backend"]=="mace":args+=["--mace-model",c["mace_model"]]
 if c["backend"]=="gpaw":
  args+=["--gpaw-mode",c["gpaw_mode"],"--gpaw-xc",c["gpaw_xc"],
    "--gpaw-kpts",*map(str,c["gpaw_kpts"])]
  if c["gpaw_mode"]=="lcao":args+=["--gpaw-basis",c["gpaw_basis"]]
 # Per-axis front cutoffs and neighbor constraints derived from the geometry advisor.
 # This is essential for graphite XZ, whose next Z layer is detached from the seed.
 for entry in c.get("advisor_axes",[]):
  axis=entry["axis"]
  if axis not in c["growth_axis"]:continue
  front=entry.get("recommended_front_max_A")
  if isinstance(front,(float,int)) and front>0:
   args+=["--template-front-max-"+axis,str(front)]
  mode=entry.get("interface_mode","")
  neighbors=(0 if mode=="detached-layer-nucleation" and c["dimension"] in ("layered","layered_bulk") and axis=="z" else entry.get("recommended_min_neighbors",c["template_min_neighbors"]))
  args+=["--template-min-neighbors-"+axis,str(int(neighbors))]
 if c["impurities"]:
  args+=["--impurity"]
  for el,v in c["impurities"].items():args+=[str(el),str(v)]
 args+=c["advanced_args"]
 return args

def generate(path:Path)->None:
 c,geometry,warnings=validate_config(path)
 target=Path(c["resolved_run_directory"])
 if target.exists():
  if any(target.iterdir()):
   raise ValueError(f"Output directory exists and is nonempty: {target}. Use a NEW run_directory; no overwrites.")
 if not ENGINE.is_file():raise ValueError("Motor não encontrado: "+str(ENGINE))
 target.mkdir(parents=True,exist_ok=True)
 seed=Path(c["resolved_structure"])
 templ=Path(c["resolved_template"])
 files=[seed,templ,ENGINE]
 if ADVISOR.exists():files.append(ADVISOR)
 names={}
 for file in files:
  name=file.name
  if name in names and names[name]!=str(file):
   raise ValueError("Seed and template have same filename but different source; rename one.")
  names[name]=str(file)
  shutil.copy2(file,target/name)
 args=generated_command(c,seed.name,templ.name,ENGINE.name)
 run=target/"run.sh"
 run.write_text("#!/usr/bin/env bash\nset -euo pipefail\n"+shlex.join(args)+"\n")
 run.chmod(0o755)
 pbs=target/"job.pbs"
 queue_line=f"#PBS -q {c['pbs_queue']}\n" if c["pbs_queue"] else ""
 # Only user-provided env activation, no hard-coded tromer/con­da path.
 env_line=c["env_activation"]+"\n" if c["env_activation"] else ""
 pbs.write_text("#!/usr/bin/env bash\n"
  f"#PBS -N Grown_{c['name'][:8]}\n"
  +queue_line+
  f"#PBS -l nodes=1:ppn={c['pbs_cores']}\n"
  f"#PBS -l mem={c['pbs_memory']}\n"
  "#PBS -o job.o\n#PBS -e job.err\n"
  "set -euo pipefail\n"
  "cd \"$PBS_O_WORKDIR\"\n"
  +env_line+
  "export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONUNBUFFERED=1\n"
  "echo \"BEGIN $(date -Is) $(hostname) $PBS_JOBID\"\n"
  "bash run.sh > simulation.log 2>&1\n"
  "echo \"END $(date -Is)\"\n")
 # Copy original JSON and a normalized resolved configuration and scientific preflight.
 (target/"input_config.json").write_text(path.read_text(encoding="utf-8"))
 (target/"validated_input.json").write_text(json.dumps({
  "config":c,"geometry":geometry,"warnings":warnings,
  "engine_sha256":hashfile(ENGINE),"command":args,
  "created_by":"GROWN Input Builder v0.1",
  "limitations":"PBC/seam/collision validation is not full physical geometry, force or thermal correctness. No DFT convergence.",
 },indent=2,ensure_ascii=False))
 if c.get("advisor_axes"):
  (target/"advisor_checked_axes.json").write_text(json.dumps(c["advisor_axes"],indent=2,ensure_ascii=False))
 if ADVISOR.exists() and c["enable_advisor_report"]:
  adv_structure=templ if c["resolved_template"]!=c["resolved_structure"] else seed
  advisor=subprocess.run([sys.executable,str(ADVISOR),
   "--structure",str(adv_structure),"--template",str(templ),
   "--axis",c["growth_axis"],"--growth-direction",c["growth_direction"],
   "--species",*c["deposition_species"]],
   capture_output=True,text=True)
  (target/"advisor_report.txt").write_text(advisor.stdout+"\nERR:\n"+advisor.stderr)
  if advisor.returncode:print("WARNING: advisor returned code",advisor.returncode,"; see advisor_report.txt")
 for script in (run,pbs):subprocess.run(["bash","-n",str(script)],check=True)
 (target/"README.txt").write_text(
  "GROWN Input Builder v0.1\n"
  "Inputs were validated for periodic bonds and short collisions, NOT all future growth sites.\n"
  "Inspect validated_input.json and advisor_report.txt BEFORE submitting!\n"
  "User is responsible for installing the selected backend and choosing PBS environment.\n"
  "How to run locally: bash run.sh (DO NOT run heavy calculations on cluster login nodes).\n"
  "How to submit to PBS from this folder: qsub job.pbs\n"
  "Check qstat, job.err, simulation.log and growth_log.csv; final CIF alone is not success.\n")
 print("GENERATED",target)
 print("Files: input_config.json validated_input.json",seed.name,templ.name,"run.sh job.pbs advisor_report.txt")
 print("Preview:",shlex.join(args))
 print("NOT SUBMITTED. If geometry and environment are appropriate, from output dir: qsub job.pbs")

def ask(msg:str,default:str)->str:
 v=input(f"{msg} [{default}]: ").strip()
 return v or default

def init(path:Path):
 print("\nGROWN: guided input setup. You can edit the generated JSON later.")
 print("Required: an ASE-readable CIF seed; validated 2D/3D template; backend installation.")
 c=DEFAULT.copy()
 c["structure"]=ask("Path to seed CIF","seed.cif")
 c["template"]=ask("Path to growth template CIF (blank = same as seed)",c["structure"])
 c["dimension"]=ask("Kind: 2d, 3d, layered, layered_bulk","2d")
 c["growth_axis"]=ask("Growth axis x/y/z/xy/xz/yz","x")
 c["backend"]=ask("Energy calculator chgnet/mace/gpaw/emt","chgnet")
 sp=ask("Deposited chemical elements, space-delimited","C")
 c["deposition_species"]=sp.split()
 c["events"]=int(ask("Maximum deposition events","50"))
 c["temperature_K"]=float(ask("Temperature [K]","500"))
 c["template_connect_cutoff_A"]=float(ask("Bond connectivity cutoff [A]","1.90"))
 c["template_column_period"]=int(ask("Template column periodicity (must be checked using advisor)","2"))
 c["template_extend_ncols"]=int(ask("Extra template columns","30"))
 doping=ask("Impurity/vacancies e.g. 'N:0.1,B:0.09,vac:0.1' (blank = none)","")
 c["impurities"]={k:float(v) for k,v in (part.split(":") for part in doping.split(",") if part)}
 c["run_directory"]=ask("New output folder","my_first_growth")
 c["pbs_queue"]=ask("PBS queue (empty = default queue)","") or None
 c["env_activation"]=ask("Optional backend activation command in PBS (blank = none)","")
 c["name"]=ask("Short job name",Path(c["run_directory"]).name)
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():raise ValueError("Refuse to overwrite an existing config: "+str(path))
 path.write_text(json.dumps(c,indent=2,ensure_ascii=False)+"\n")
 print("WROTE",path)
 print("NEXT: python3 grown_input.py validate",path)
 print("THEN: python3 grown_input.py generate",path)

def status(dir:Path):
 p=dir/"growth_log.csv"
 if not dir.is_dir():raise ValueError("Missing run folder: "+str(dir))
 if not p.exists():print("No growth_log.csv yet; perhaps not submitted or model still initializing");return
 with p.open(newline="",errors="replace") as f:events=list(csv.DictReader(f))
 chem=Counter(x.get("deposited_species") for x in events)
 print("Folder:",dir,"events:",len(events),"composition of events:",dict(chem),
       "has final CIF:",(dir/"growth_final.cif").exists())
 if (dir/"job.err").exists():print("PBS STDERR:",(dir/"job.err").read_text(errors="replace")[-900:])

def main():
 parser=argparse.ArgumentParser(description="Prepare validated crystal-growth inputs (no calculation and no qsub)")
 p=parser.add_subparsers(dest="command",required=True)
 for mode in ("init","validate","generate"):
  q=p.add_parser(mode)
  q.add_argument("config",help="JSON input config")
 q=p.add_parser("status")
 q.add_argument("run_directory")
 args=parser.parse_args()
 try:
  if args.command=="init":init(Path(args.config).expanduser().resolve())
  elif args.command=="validate":validate_config(Path(args.config).expanduser().resolve())
  elif args.command=="generate":generate(Path(args.config).expanduser().resolve())
  elif args.command=="status":status(Path(args.run_directory).expanduser().resolve())
 except (ValueError,FileNotFoundError,KeyError,json.JSONDecodeError) as e:
  print("GROWN INPUT ERROR:",str(e),file=sys.stderr)
  sys.exit(2)
if __name__=="__main__":main()
