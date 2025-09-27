#!/usr/bin/env python
# coding: utf-8

# In[23]:


import ase
from ase.io import read,write
from ase import Atoms
import numpy as np
#import matplotlib.pyplot as plt
import MDAnalysis as mda

# In[3]:


def extract_positions(frame):
    Ocoordinates = [atom.position for atom in frame if atom.symbol == 'O']
    Hcoordinates = [atom.position for atom in frame if atom.symbol == 'H']
    Ccoordinates = [atom.position for atom in frame if atom.symbol == 'C']
    # not sure if it works with C atom (to check)
    # if len(Ccoordinates) != 0:
    #     dCO = ase.geometry.get_distances(Ccoordinates,Ocoordinates,cell=frame.cell,pbc=True)[1]
    #     Ocoordinates = Ocoordinates[dCO<2.0]
    return Ocoordinates, Hcoordinates, Ccoordinates


# In[4]:


def pairwise_distances(oatoms,hatoms,cell):
    distances = ase.geometry.get_distances(oatoms,hatoms,cell=cell,pbc=True)[1]
    return distances


# In[58]:


def denominator(distances,lambda_=50):
    sums = np.zeros([np.shape(distances)[1]])
    for i in range(np.shape(sums)[0]):
        sums[i] = np.sum(np.exp(-lambda_ * distances.T[i]))
    return sums


# In[59]:


def create_matrix(distances,sums,lambda_=50,threshold=1e-3):
    OHmatrix = np.zeros([np.shape(distances)[0],np.shape(distances)[1]])
    for j in range(np.shape(distances)[1]):
        for i in range(np.shape(distances)[0]):
            OHmatrix[i][j] = np.exp(-lambda_ * distances[i][j])/sums[j]
        OHmatrix = np.where(np.abs(OHmatrix) < threshold, 0, OHmatrix)

    return OHmatrix


# In[124]:


def find_oh(frame,OHmatrix):
    z_oh = 0
    idx=-1
    surf = 9.458
    for x in range(len(Ocoordinates)-2):   # discard the last of O atoms of CO2
        if np.sum(OHmatrix[x]) == 1:
            z_oh = Ocoordinates[x][2] - surf
            idx = x
    return z_oh, idx


# In[ ]:



u = mda.Universe('traj.xyz')
cell = [[14.479, 0.0, 0.0], [-7.239499999999995, 12.538813999999999, 0.0], [0.0, 0.0, 44.458]]
types =  u.atoms.types
types[types=='A'] = 'Ag'

Z_oh = open('z_oh.txt', 'w')
for x in range(len(u.trajectory)):
    positions = np.array(u.trajectory[x].positions)
    positions = positions.reshape((-1,3))
    frame = Atoms(types,positions=positions)
    frame.set_cell(cell)
    frame.set_pbc(True)
    #print('extracting coordinates')
    Ocoordinates, Hcoordinates, Ccoordinates = extract_positions(frame)
    oxygen_indices = [i for i, atom in enumerate(frame) if atom.symbol == 'O']
    #print('starting voronoi stuff')
    distances = pairwise_distances(Ocoordinates, Hcoordinates, frame.cell)
    den = denominator(distances,500)
    OHmatrix = create_matrix(distances,den,500)
    #print('computing LSI')
    z_oh, idx = find_oh(frame,OHmatrix)
    if idx != -1 :
        oh_idx = oxygen_indices[idx]
    else:
        oh_idx  = idx
    Z_oh.write(f"{z_oh},{oh_idx}\n")
    Z_oh.flush()
    #print(f'end frame {x}')

Z_oh.close()