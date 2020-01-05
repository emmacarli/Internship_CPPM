#Author: Emma Carli 
# Code parameters

#%%

import ctools
import matplotlib.pyplot as plt

#I have taken the "anaconda3/share/examples" folder and moved it to "site-packages" as "ctools_plotting"
#could also have just added the folder to the system path 
from ctools_plotting.show_butterfly import plot_butterfly


#%%


#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'


# General ctools parameters

#%%


caldb = 'prod3b-v2'
irf   = 'North_z20_50h' #North up to 20 TeV, South up to 300 TeV
#altitude recommended by Gaia
#energy range complies with background response limits
emin  = 0.013 #TeV 
emax  = 160.0 #TeV
tmin = 0.0
tmax = 3600*40 #15 hour observation in Galactic survey, sometimes shortened for trials, or lengthened to limit statistical influences
fovradius = 5 #radius of the field of view, degrees


#%%


#Model1-specific parameters
ra = 83.6331
dec = 22.0145
name = 'model1'
source_model = "${CTOOLS}/share/models/model1.xml"


#%%


#Name of files produced by this code
events_file = "model1_obs.fits"
skymap_file = 'model1_skymap.xml'
obsmodel_file = 'model1_obsmodel.xml'
butterfly_file = 'model1_butterfly.ascii'


# Fit the simulated data

#%%


obs_model = ctools.ctlike()
obs_model['inobs'] = events_file
obs_model['inmodel'] = source_model
obs_model['outmodel'] = obsmodel_file
obs_model["caldb"] = caldb
obs_model["irf"] = irf
obs_model['statistic'] = 'DEFAULT' 
obs_model['chatter'] = 4
obs_model["edisp"] = True #takes much longer to compute

obs_model['bkgcube'] = ''
obs_model['psfcube'] = ''
obs_model['expcube'] = ''


#%%


print(obs_model)


#%%


obs_model.logFileOpen()
obs_model.execute()
obs_model.telapse()


# Generate butterfly that shows spectral energy distribution of the model with errors

#%%


butterfly = ctools.ctbutterfly() 
butterfly['inobs'] = events_file
butterfly['inmodel'] = obsmodel_file
butterfly['outfile'] = butterfly_file
butterfly['srcname'] = name 
butterfly["caldb"] = caldb
butterfly["irf"] = irf
butterfly['statistic'] = 'DEFAULT' 
butterfly['chatter'] = 4
butterfly['emin'] = emin
butterfly['emax'] = emax
butterfly["edisp"] = True

butterfly['bkgcube'] = ''
butterfly['psfcube'] = ''
butterfly['expcube'] = ''


#%%


print(butterfly)


#%%


butterfly.logFileOpen()
butterfly.execute()
butterfly.telapse()


#%%


plot_butterfly(butterfly_file,'butterfly.jpg')
plt.close() 

