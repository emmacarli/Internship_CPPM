#Author: Emma Carli 
# =============================================================================
# This code simulates a high-energy source
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%%

import ctools
import matplotlib.pyplot as plt
import os
import gammalib
#import random
import numpy as np
from math import log10

#%%

#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'
#other parameters
plt.rcParams['axes.grid'] = True


#%%
#General simulation parameters

caldb = 'prod3b-v2' #calibration database
orig_irf = 'South_z40_50h' 
tmin = 0.0
tmax = 3600*40  #length of observation
fovradius = 0.8 #radius of the field of view, degrees
offset = 0.5 #deg

#%%
#set the energy limits of the IRF by finding the most limiting components

#Get calibration database and original IRF into gammalib format
caldb_gammalib = gammalib.GCaldb('cta', caldb)        
irf_gammalib   = gammalib.GCTAResponseIrf(orig_irf, caldb_gammalib)

emin = 0.1 #TeV #set minimum at 100Gev, like Ozi

#find the smallest max energy range in IRF
emaxs = []
emaxs.append(irf_gammalib.background().table().axis_hi(irf_gammalib.background().table().axis('ENERG'),irf_gammalib.background().table().axis_bins(irf_gammalib.background().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.aeff().table().axis_hi(irf_gammalib.aeff().table().axis('ENERG'), irf_gammalib.aeff().table().axis_bins(irf_gammalib.aeff().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.psf().table().axis_hi(irf_gammalib.psf().table().axis('ENERG'), irf_gammalib.psf().table().axis_bins(irf_gammalib.psf().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.edisp().table().axis_hi(irf_gammalib.edisp().table().axis('ENERG'), irf_gammalib.edisp().table().axis_bins(irf_gammalib.edisp().table().axis('ENERG'))-1))
emax = min(emaxs) #in TeV

bins = np.logspace(log10(emin), log10(emax), num=int(log10(emax/emin)*10)) #create ten bins per energy decade in the range for histogram
bins = [log10(x) for x in bins]
#%%
#source1b-specific parameters

ra = 83.6331 + offset 
dec = 22.0145

#%%
#Define some output files

events_file = 'obs.fits'
skymap_file = 'skymap.fits'

#%%
#Run the simulation for each IRF version
for cutoff in ['1','2','3']: #50, 100, 200 TeV
    
    for flux in ['a', 'b', 'c', 'd']: #20, 40, 60, 80 mCrab
               
        for function in ['none', 'constant', 'step', 'gradient']: 
            
            if function == 'none': #if there is no bracketing
                function_signs = ['']
                function_components = ['']
            else:
                function_signs = ['minus','plus']
                function_components = ['AEff' ] #add here 'EDisp' if do IRF EDisp bracketing
        
            for sign in function_signs:
                for component in function_components:
                    
                    if function =='none':
                        irf=orig_irf
                    else:
                        irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                    
                    name = 'source'+cutoff+flux
                    source_model = '${CTOOLS}/share/models/'+name+'.xml'

                    
                    wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
                    os.makedirs(wd)
                    os.chdir(wd)
                    
                    logfile = open('simulation.txt', 'w')
                    
                    #%%
        
                    simulation = ctools.ctobssim()
                    simulation['inmodel'] = source_model
                    simulation['outevents'] = wd+events_file
                    simulation['ra'] = ra
                    simulation['dec'] =  dec
                    simulation['rad'] = fovradius 
                    simulation['tmin'] = tmin
                    simulation['tmax'] = tmax
                    simulation['emin'] = emin
                    simulation['emax'] = emax
                    simulation['chatter'] = 4 #max output info in the log file
                    simulation['edisp'] = True  
                    simulation['caldb'] = caldb
                    simulation['irf'] = irf 
                    simulation['seed'] = 1000 #int(random.random() * 1000) #set to same integer for same simulation. randomise for repeated simulations
                    
                    #%%
                    
                    print(simulation)
                    
                    #%%
                    
                    simulation.logFileOpen()
                    simulation.execute()
                    logfile.write('ctobssim:' + str(simulation.telapse()) + 'seconds \n')
                    simulation.logFileClose()
                    
                    #%%
                    #Plot the energy spectrum
                    
                    fig1 = plt.figure()
                    ax1 = plt.gca()
                    ax1.set_yscale('log')
                    ax1.set_xlabel('Log10(Energy) (TeV)')
                    ax1.set_ylabel('Number of events')
                    
                    energies = []
                    for event in simulation.obs()[0].events():
                        energies.append(event.energy().log10TeV())
                        
        
                    ax1.hist(energies, bins=bins, range=(log10(emin),log10(emax)), edgecolor='black', color='0' )
                    ax1.set_title('Observed counts')
                    fig1.savefig(wd+'energy_histogram.pdf')
                    plt.close(fig1)
                    
                    #%%
                    
                    skymap = ctools.ctskymap()
                    skymap['inobs'] = wd+events_file
                    skymap['caldb'] = caldb
                    skymap['irf'] = irf
                    skymap['usepnt'] = True #use the simulation's pointing to find sky position
                    skymap['binsz'] = 0.02 #spatial resolution
                    skymap['nxpix'] = int(2*fovradius/float(skymap['binsz'].value()))
                    skymap['nypix'] = int(skymap['nxpix'].value())
                    skymap['emin'] = emin
                    skymap['emax'] = emax
                    skymap['outmap'] = wd+skymap_file
                    skymap['chatter'] = 4
                    skymap['bkgsubtract'] = 'NONE'   #or 'IRF'
                    
                    #%%
                    
                    print(skymap)
                    
                    #%%
                    
                    skymap.logFileOpen()
                    skymap.execute()
                    logfile.write('ctskymap:' + str(skymap.telapse()) + 'seconds \n')
                    skymap.logFileClose()
                    
                    
                    #%%
                    #Plot the sky map of the simulation
                    
                    from matplotlib.colors import SymLogNorm
                    #The SymLogNorm scale is a Log scale for both positive and negative values  (for background subtraction)
                    
                    fig2 = plt.figure()
                    ax2 = plt.gca()
                    image = ax2.imshow(skymap.skymap().array(),origin='lower',
                               extent=[ra+fovradius,ra-fovradius,dec-fovradius,dec+fovradius],
                               norm=SymLogNorm(1), cmap='viridis' ) # the scale will be linear within +-1 count
                    ax2.set_xlabel('R.A. (deg)')
                    ax2.set_ylabel('Dec (deg)')
                    cbar = plt.colorbar(image, ax=ax2)
                    cbar.set_label('Counts')
                    ax2.set_title('Map of observed counts') 
                    fig2.savefig(wd+'skymap.pdf')
                    plt.close(fig2)
                    
                    #%%
                    
                    logfile.close()
            
            
