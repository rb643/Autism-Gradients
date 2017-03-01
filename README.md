## Autism gradients of hierarchical organization

#### Brainhack project on exploring the use of connectivity gradients to study cortical hierarchies in autism

#### Rationale
Most of the theoretical foundations on the use of gradient can be found [here] (http://www.pnas.org/content/113/44/12574) 

In short, Margulies et al. show how the primary connectivity gradient very closely resembles the topology of the default mode network and that there appears to be some hierarchy in this gradient that follows the hierarchy of complexity in cognitive processing (ranging from low-level sensory processing to higher order cognition).

In Autism research there are numerous theories regarding alterations in functional connectivity. Ranging from a global theory suggesting short-range over connectivity and long-range underconnectivity (Belmonte et al. 2004) and more specific examples of specific connection mainly in anterior-posterior connections (Courchesne et al.). From a more cognitive perspective it might be interesting to see if some of this is also represented in some for of disruption in cortical hierarchy. If for example individuals with autism have a strong talent for very detailed functions, but possibly less capacity to intergrate information from different sources/modalities one could hypothesize that the cortical hierarchy might be disrupted.

Thus, in the present project we would like to investigate these cortical hierarchy by looking at the steepness of the connectivity gradient. 

---

### Get set up
Make sure you have anaconda or miniconda installed:
https://conda.io/miniconda.html

Clone this repository:
`git clone https://github.com/rb643/Autism-Gradients`

Create a conda environment from the environment.yml file (you have to be inside the repo folder):
`conda env create -n rbbrainhack -f environment.yml`

download and unpack cluster_roi:
```
curl -LOk "https://github.com/ccraddock/cluster_roi/archive/v1.0.0.zip"
unzip v1.0.0
mv cluster_roi-1.0.0/ cluster_roi/
rm v1.0.0.zip 
```
