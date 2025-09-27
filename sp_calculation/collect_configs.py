from ase.io import read, write
import pandas as pd
import os, sys
import glob
import numpy as np
os.system('mkdir cp')
subfolders = list(range(0, 152))

for folder in subfolders:
    folder_name = str(folder+1)
    os.chdir(folder_name)   # move to the subfolder directory
    configs = sorted([d for d in glob.glob('config_*') if not d.endswith('.xyz')], key=lambda x: int(x.split('_')[1]))
    for dir in configs:
        os.chdir(dir)

        conf = os.path.basename(os.getcwd())  # obtain the name of the config
        with open('tmp-log-FCP.txt', 'r') as file:
            lines = file.readlines()
        if len(lines)!=1:
            df = pd.read_csv('tmp-log-FCP.txt', delimiter='\t')
            
            if not os.path.exists('OUTCAR') and np.abs(df['conv(V)'].iloc[0])<0.01 :
                os.system('cp OUTCAR_pzc OUTCAR')    
                os.system(f'echo {conf} CP converged at initial ne setting!')
            if  np.abs(df['conv(V)'].iloc[-1])>=0.01 :
                os.chdir("..")   # return back to the subfolder
                os.system(f'echo {conf} does not CP converged')
                continue
            atoms_cp=read('OUTCAR', format='vasp-out')
            write(f'{conf}_cp.result.extxyz', atoms_cp, format='extxyz')
            free_energy_grand_cp = df['Etoten_grand(eV)'].iloc[-1]

            with open(f'{conf}_cp.result.extxyz', 'r') as file:
                lines = file.readlines()

            # change energy_no_entropy to grand_energy_no_entropy
            index_to_replace = 1  # the index of energy line

            lines[index_to_replace] = lines[index_to_replace].replace(
                ' free_energy=' + lines[index_to_replace].split('free_energy=')[-1].split()[0], 
                ""
                )        
            lines[index_to_replace] = lines[index_to_replace].replace(
                'energy=' + lines[index_to_replace].split(' energy=')[-1].split()[0],
                'energy=' + str(free_energy_grand_cp)
            )

            # save the modified file
            with open(f'{conf}_cp.result.extxyz', 'w') as file:
                file.writelines(lines)

#            os.system(f'mv {conf}_pzc.result.extxyz ../../pzc')
            os.system(f'mv {conf}_cp.result.extxyz ../../cp')
        else:
            print(f'{dir} does not successfully calculated!')
        os.chdir("..")   # return back to the subfolder
    os.chdir("..")   # return back to the subfolder
