import os,re
import random

def chg_seed(filename):
    # Generate random seeds
    seed1 = random.randint(10000, 99999)
    seed2 = random.randint(10000, 99999)
    
    # Read and modify input.lammps
    with open(filename, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if re.search(r"variable\s+SEED1", line):
            line = f"variable            SEED1           equal {seed1}\n"
        elif re.search(r"variable\s+SEED2", line):
            line = f"variable            SEED2           equal {seed2}\n"
        new_lines.append(line)
    # Write the modified input.lammps
    with open(filename, "w") as f:
        f.writelines(new_lines)

original_directory = os.getcwd()

for x in range(0, 5):
    i = x + 1
    print(f'data_{i}.lmp')
    os.system(f'mkdir {i}')
    os.system(f'cp -r input.lammps  plumed.dat cal_f_devi.py run_alwys.sh {i}/')
    os.system(f'mv data_{i}.lmp {i}/data.lmp')

    os.chdir(os.path.join(original_directory, f'{i}'))
    chg_seed('input.lammps')

    with open("run_alwys.sh", "r") as f:
        lines = f.readlines()
    new_lines = [line.replace(f"k_ion_360", f"{i}_k_ion_360") for line in lines]
    with open("run_alwys.sh", "w") as f:
        f.writelines(new_lines)
    print(os.getcwd())
    os.system("sbatch run_alwys.sh")

    # Change back to the original directory after processing each i
    os.chdir(original_directory)