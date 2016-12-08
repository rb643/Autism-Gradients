# -*- coding: utf-8 -*-
"""
Created on Mon Dec 01 15:05:56 2016

@author: Richard
"""
## Required packages:
# pySTATIS
# numpy
# mapalign
# nibabel
# sklearn
# cluster_roi

## suggested file struture:
# main/
# main/cpac/filt_noglobal/rois_cc400/ > for data files
# main/Affn/ > for adjacency matrices
# main/Embs/ > for diffusion embedding files
# main/Regs/ > for registered gradient files

# download ABIDE data:
# http://preprocessed-connectomes-project.org/abide/download.html
# python download_abide_preproc.py -d rois_cc400 -p cpac -s filt_noglobal -o data/ -x 'M' -gt 18 -lt 55

## lets start with some actual script
# import useful things
import numpy as np
import os
import nibabel as nib
from sklearn.metrics import pairwise_distances

# get a list of inputs
from os import listdir
from os.path import isfile, join

# little helper function to return the proper filelist with the full path
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]
# and create a filelist
onlyfiles = listdir_fullpath("cpac/filt_noglobal/rois_cc400")

# check to see which files contains nodes with missing information
missingarray = []
for i in onlyfiles:
# load timeseries
    filename = i
    ts_raw = np.loadtxt(filename)

# check zero columns
    missingn = np.where(~ts_raw.any(axis=0))[0]
    missingarray.append(missingn)

# select the ones that don't have missing data
ids = np.where([len(i) == 0 for i in missingarray])[0]
selected = [onlyfiles[i] for i in ids]
# could be useful to have one without pathnames later one
selected2 = [os.path.basename(onlyfiles[i]) for i in ids]
print(len(selected))

# run the diffusion embedding
from mapalign import embed

for i in selected:
    # load timeseries
    print i
    filename = i
    ts = np.loadtxt(filename)
    # create correlation matrix
    dcon = np.corrcoef(ts.T)
    dcon[np.isnan(dcon)] = 0

    # Get number of nodes
    N = dcon.shape[0]

    # threshold
    perc = np.array([np.percentile(x, 90) for x in dcon])

    for ii in range(dcon.shape[0]):
        #print "Row %d" % ii
        dcon[ii, dcon[ii,:] < perc[ii]] = 0

    # If there are any left then set them to zero
    dcon[dcon < 0] = 0

    # compute the pairwise correctionlation distances
    aff = 1 - pairwise_distances(dcon, metric = 'cosine')

    # start saving
    savename = os.path.basename(filename)
    np.save("./Affn/"+savename+"_cosine_affinity.npy", aff)
    # get the diffusion maps
    emb, res = embed.compute_diffusion_map(aff, alpha = 0.5)
    # Save results
    np.save("./Embs/"+savename+"_embedding_dense_emb.npy", emb)
    np.save("./Embs/"+savename+"_embedding_dense_res.npy", res)
    np.save("./Embs/"+savename+"_embedding_dense_res_veconly.npy", res['vectors']) #store vectors only

# get dimension
#resolution = len(res['vectors'][0,:])
#a = [res['vectors'][:,i]/ res['vectors'][:,0] for i in range(resolution)]
#emb = np.array(a)[1:,:].T
#len(emb)

# stack the individual gradient files and create a groupwise gradient
from pySTATIS import statis

#load vectors
names = list(xrange(392))
X = [np.load("./Embs/"+ os.path.basename(filename)+"_embedding_dense_emb.npy") for filename in selected2]
out = statis.statis(X, names, fname='statis_results.npy')
statis.project_back(X, out['C_cols'], path = "./Regs/",fnames = selected2)
np.save("Mean_Vec.npy",out['F'])

# saving everything in one dump
import pickle
with open('output.pickle' ,'w') as f:
    pickle.dump([selected, out],f)
#with open('output.pickle') as f:  # Python 3: open(..., 'rb')
#   selected, out = pickle.load(f)

######################### plotting #######################
# plot to surface for inspection
# this cell in only necessary for plotting below
import matplotlib.pylab as plt
import nilearn
import nilearn.plotting

import numpy as np
import nibabel as nib

def rebuild_nii(num):

    data = np.load('Mean_Vec.npy')
    a = data[:,num].copy()
    nim = nib.load('cc400_roi_atlas.nii')
    imdat=nim.get_data()
    imdat_new = imdat.copy()

    for n, i in enumerate(np.unique(imdat)):
        if i != 0:
            imdat_new[imdat == i] = a[n-1] * 100000 # scaling factor. Could also try to get float values in nifti...

    nim_out = nib.Nifti1Image(imdat_new, nim.get_affine(), nim.get_header())
    nim_out.set_data_dtype('float32')
    # to save:
    nim_out.to_filename('Gradient_'+ str(num) +'_res.nii')

    nilearn.plotting.plot_epi(nim_out)
    return(nim_out)

for i in range(10):
    nims = rebuild_nii(i)

######################### excel #######################
import pandas as pd
# read in csv
df_phen = pd.read_csv('Phenotypic_V1_0b_preprocessed1.csv')
# add a column that matches the filename
for i in df_phen:
    df_phen['filename'] = join(df_phen['FILE_ID']+"_rois_cc400.1D")
    df_phen['filenamenpy'] = join(df_phen['FILE_ID']+"_rois_cc400.1D.npy") # useful to match up with registered gradient files
# add a selection variable for those files that we used
df_phen['selec'] = np.where(df_phen['filename'].isin((selected2)), 1, 0)

######################### double check files #######################
from os import listdir
from os.path import isfile, join

a = []
onlyfiles = [f for f in listdir('./Regs/') if isfile(join('./Regs/', f))]
for i in onlyfiles:
    b = np.load('./Regs/%s' % i)
    # normalize:
    c = (b - np.mean(b)) / np.std(b)
    a.append(c)

# all subjects in array
a = np.array(a)
mean_vec = np.mean(np.array(a), axis = 0)
# check to see if this is the same as the mean_vec in the other output?

######################### compare slopes #######################
## there is probably an easier way to loop through this and calculate the slopes...?
from scipy import stats
# start with an empty list
grdnt_slope = []
for i in selected2:
    # load gradients
    print i
    filename = i
    grdnt = np.load("./Regs/" + filename + ".npy")
    # do we need a specific ordering of the nodes??
    y = list(xrange(392))
    temp = [] # use a temporary subject specific list
    for ii in range(10):
        x = sorted(grdnt[:,ii]) # just sort in ascending order?
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        temp.append(slope)
        
    grdnt_slope.append(temp)
    
######################### integrate slopes #######################
    ## NB need to check to make sure that the phenotypic file and selected file are ordered the same!!!
data = df_phen.loc[df_phen["selec"] == 1]
data['slopes'] = grdnt_slope
data.to_csv('Combined.csv', sep='\t')
