from ase.calculators.FCPelectrochem import FCP
from ase.calculators.vasp import Vasp
from ase.io import read, write
from ase.optimize import LBFGS
import numpy as np 
import sys, os
import glob

# set the r2SCAN dict
Vasp.xc_defaults['r2scan'] = {'metagga': 'R2SCAN', 'luse_vdw': True, 'bparam': 11.95, 'cparam': 0.0093, 'lasph': True}
# set the hybrid solution parameter
hysol = {'lsolhybrid': True, 'method_sh': 1, 'sigma_sh': 0.02857, 'alpha_sh': 0.10}
# set the calculator
cal_sol=Vasp(pp='PBE',
             xc='r2scan',
             lwave=True,
             istart=1,
             lcharg=False,  # write the charge density file
             laechg=False,  # necessary for bader charge analysis
             lvtot=False, lvhar=False, lelf=False,
             encut=500,
             ismear=1, sigma=0.2, isym=0, ediff=1E-6,
             nelm=200,                      
             lsol=True, eb_k=78.4, lambda_d_k=3.04, tau=0, lrhoion=False,
             lreal='Auto', algo='All', addgrid=True,           
             ncore = 4,         # for gpu, comment this keywards        
             kpts=(3, 3, 1)
             )
# cal_sol.set(directory='sol')
cal_sol.set(**hysol)



configs = sorted(glob.glob('config_*.xyz'), key=lambda x: int(x.split('_')[1].split('.')[0]))

for conf in configs:     
      atoms=read(conf)
      atoms.pbc = [True, True, True]
      atoms.cell = [8.688, 8.688, 38.458, 90, 90, 120]
      dir = conf.split('.xyz')[0]
      cal_sol.set(directory=dir)
      ne = 743
      U_set = -1.5
      cal_FP=FCP(innercalc=cal_sol,
                  fcptxt='log-fcp.txt',
                  U=U_set,
                  NELECT = ne,
                  C = 1/80,    #1/k  capacitance per A^2
                  FCPmethod = 'Newton-fitting',
                  FCPconv=0.01,
                  NELECT0=ne, 
                  adaptive_lr=True,
                  work_ref=4.21,
                  max_FCP_iter=10000
                  )
      atoms.calc=cal_FP
      energy = atoms.get_potential_energy()
      print(conf, " Single point energy: ", energy, " eV")
      del atoms










