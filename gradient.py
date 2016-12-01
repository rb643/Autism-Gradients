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

# download ABIDE data:
# http://preprocessed-connectomes-project.org/abide/download.html 
# python download_abide_preproc.py -d rois_cc400 -p cpac -s filt_noglobal -o data/ -x 'M' -gt 18 -lt 55

## lets start with some actual script
# import useful things
import numpy as np
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
    np.save("Affn/"+savename+"_cosine_affinity.npy", aff)
    # get the diffusion maps
    emb, res = embed.compute_diffusion_map(aff, alpha = 0.5)
    # Save results
    np.save("Embs/"+savename+"_embedding_dense_emb.npy", emb)
    np.save("Embs/"+savename+"_embedding_dense_res.npy", res)
    np.save("Embs/"+savename+"_embedding_dense_res_veconly.npy", res['vectors']) #store vectors only

# get dimension
#resolution = len(res['vectors'][0,:])
#a = [res['vectors'][:,i]/ res['vectors'][:,0] for i in range(resolution)]
#emb = np.array(a)[1:,:].T
#len(emb)

# stack the individual gradient files and create a groupwise gradient
from pySTATIS import statis

#load vectors
names = list(xrange(392))
X = [np.load("Embs/"+ os.path.basename(filename)+"_embedding_dense_res_veconly.npy") for filename in selected] 
out = statis.statis(X, names, fname='statis_results.npy')


### THIS IS STILL WORK IN PROGRESS...
# saving everything in one dump
import pickle
with open('output.pickle' ,'w') as f:
    pickle.dump([selected, out],f)
#with open('output.pickle') as f:  # Python 3: open(..., 'rb')
#   selected, out = pickle.load(f)

# plot to surface for inspection (DOESN'T WORK... :( yet..)
from cluster_roi import make_image_from_bin_renum
binfile = out['F'][:,1]
make_image_from_bin_renum(image,binfile,mask)
