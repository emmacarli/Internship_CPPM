#Author: Emma Carli 
from IPython import get_ipython
get_ipython().magic('reset -sf') 

# Code parameters

#%%

import ctools
import matplotlib.pyplot as plt
import math
import cscripts

#I have taken the "anaconda3/share/examples" folder and moved it to "site-packages" as "ctools_plotting"
#could also have just added the folder to the system path 
from emma_plotting.show_butterfly import plot_butterfly
from emma_plotting.show_residuals import plot_residuals


#%%


#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'



#%%

# General simulation parameters
caldb = 'prod3b-v2'
irf   = 'North_z20_50h' #picked south because only there can go at 50TeV.
tmin = 0.0
tmax = 3600*40 #15 hour observation in Galactic survey, sometimes shortened for trials, or lengthened to limit statistical influences
#altitude recommended by Gaia
emin  = 0.013 #TeV #put 0.013 and 160 to comply with background response limits
emax  = 160 #TeV
fovradius = 0.8 #radius of the field of view, degrees


#%%


#source1a-specific parameters
name = 'source1a'
source_model = "${CTOOLS}/share/models/source1a.xml"
offset = 0.5 #deg   
ra = 83.6331 + offset #orginal 83.6331, added 0.5deg offset
dec = 22.0145

#%%

#Input file
events_file = "source1a_obs.fits"
#Output files
obsmodel_file = 'source1a_obsmodel_onoff.xml'
butterfly_file = 'source1a_butterfly_onoff.ascii'
residuals_file = 'source1a_residuals_onoff.fits'



onoffobs_file = 'source1a_obs_onoff.xml'
onoffmodel_file = 'source1a_sourcemodel_onoff.xml'

logfile = open('data_analysis_onoff.txt', 'w')


#create onoff observation

#%%
onoff = cscripts.csphagen()
onoff['inmodel'] = source_model
onoff['srcname'] = name
onoff['inobs'] = events_file
onoff["emin"] = emin
onoff["emax"] = emax
onoff['ra'] = ra
onoff['dec'] = dec
onoff['outobs'] = onoffobs_file
onoff['outmodel'] = onoffmodel_file
onoff["caldb"] = caldb
onoff['irf'] = irf
onoff['bkgmethod'] = 'REFLECTED'

onoff['rad'] = 0.25 
onoff['maxoffset'] = fovradius
#onoff['srcregfile'] = to be produced
onoff['use_model_bkg'] = False
onoff['debug'] = True
onoff['chatter'] = 4

#%%
print(onoff)

#%%
onoff.logFileOpen()
onoff.execute()
logfile.write('csphagen:' + str(onoff.telapse()) + 'seconds \n')
onoff.logFileClose()



# onoff data fitting

#%%


obs_model = ctools.ctlike()
obs_model['inobs'] = onoffobs_file
obs_model['inmodel'] = onoffmodel_file
obs_model['outmodel'] = obsmodel_file
obs_model["caldb"] = caldb
obs_model["irf"] = irf
obs_model['statistic'] = 'DEFAULT' 
obs_model['chatter'] = 4
obs_model["edisp"] = True #takes much longer to compute

obs_model['bkgcube'] = ''
obs_model['psfcube'] = ''
obs_model['expcube'] = ''
obs_model['edispcube'] = ''


#%%

print(obs_model)


#%%


obs_model.logFileOpen()
obs_model.execute()
logfile.write('ctlike:' + str(obs_model.telapse()) + 'seconds \n')
obs_model.logFileClose()


# Plot model butterfly

#%%


butterfly = ctools.ctbutterfly() 
butterfly['inobs'] = onoffobs_file
butterfly['inmodel'] = onoffmodel_file
butterfly['outfile'] = butterfly_file
butterfly['srcname'] = name 
butterfly["caldb"] = caldb
butterfly["irf"] = irf
butterfly['statistic'] = 'DEFAULT' 
butterfly['chatter'] = 4
butterfly['emin'] = emin
butterfly['emax'] = emax
butterfly["edisp"] = True

butterfly['enumbins'] = int(10 * math.log10(emax/emin))


butterfly['bkgcube'] = ''
butterfly['psfcube'] = ''
butterfly['expcube'] = ''
butterfly['edispcube'] = ''



#%%


print(butterfly)


#%%


butterfly.logFileOpen()
butterfly.execute()
logfile.write('ctbutterfly:' + str(butterfly.telapse()) + 'seconds \n')
butterfly.logFileClose()


#%%


plot_butterfly(butterfly_file,'butterfly_onoff.pdf')
plt.close() 



#%%
residuals = cscripts.csresspec() #simulation.obs()
residuals['outfile'] = residuals_file
residuals['inmodel'] = obsmodel_file
residuals['inobs'] =   onoffobs_file
residuals["edisp"] = True
residuals["caldb"] = caldb
residuals["irf"] = irf
residuals['emin'] = emin
residuals['emax'] = emax
residuals['components'] = True
residuals['statistic'] = 'DEFAULT' 
residuals['chatter'] = 4

residuals['enumbins'] = int(10 * math.log10(emax/emin))


residuals['bkgcube'] = ''
residuals['psfcube'] = ''
residuals['expcube'] = ''
residuals['edispcube'] = ''
residuals['modcube'] = ''



#%%

print(residuals)

#%%
residuals.logFileOpen()
residuals.execute()
logfile.write('csresspec:' + str(residuals.telapse()) + 'seconds \n')
residuals.logFileClose()

#%%
plot_residuals(residuals_file,'residuals_onoff.pdf',0) #0 is number of observations to plot -1
plt.close()





logfile.close()







