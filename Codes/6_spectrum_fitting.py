#Author: Emma Carli 
# =============================================================================
# This code infers a flux spectrum from observed counts
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%%

import matplotlib.pyplot as plt
import cscripts
import os
from math import log10
import gammalib

from emma_plotting.show_spectrum import plot_spectrum
from emma_plotting.show_spectrum_butterfly import plot_spectrum_butterfly

#%%

#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'

#%%

#General analysis parameters
caldb = 'prod3b-v2' #calibration database
orig_irf = 'South_z40_50h' 
               
#%%

#input files
obscube_file = 'obs_cube.fits'
expcube_file = 'exposure_cube.fits'
psfcube_file = 'PSF_cube.fits'
bkgcube_file = 'background_cube.fits'
edispcube_file = 'edisp_cube.fits'
obsmodel_file = 'obsmodel_binned.xml'
obsmodelcube_file = 'obsmodel_cube.fits'
butterfly_file = 'butterfly_binned.ascii'

#output file
spectrum_file = 'spectrum_binned.fits' #observed spectrum inferred from observation counts

#%%
#set the energy limits of the IRF by finding the most limiting components

#Get calibration database and original IRF into gammalib format
caldb_gammalib = gammalib.GCaldb('cta', caldb)        
irf_gammalib   = gammalib.GCTAResponseIrf(orig_irf, caldb_gammalib)

emin = 0.1 #TeV #set minimum at 100Gev 

#find smallest max energy range in IRF
emaxs = []
emaxs.append(irf_gammalib.background().table().axis_hi(irf_gammalib.background().table().axis('ENERG'),irf_gammalib.background().table().axis_bins(irf_gammalib.background().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.aeff().table().axis_hi(irf_gammalib.aeff().table().axis('ENERG'), irf_gammalib.aeff().table().axis_bins(irf_gammalib.aeff().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.psf().table().axis_hi(irf_gammalib.psf().table().axis('ENERG'), irf_gammalib.psf().table().axis_bins(irf_gammalib.psf().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.edisp().table().axis_hi(irf_gammalib.edisp().table().axis('ENERG'), irf_gammalib.edisp().table().axis_bins(irf_gammalib.edisp().table().axis('ENERG'))-1))
emax = min(emaxs) #in TeV

#%%

#bracketed IRFs simulations
for cutoff in ['1','2','3']: #50, 100, 200 TeV
    
    for flux in ['a', 'b', 'c', 'd']: #20, 40, 60, 80 mCrab
        
        for function in ['none','constant', 'step', 'gradient']:  
            
            if function == 'none': #no bracketing
                function_signs = ['']
                function_components = ['']
            else:
                function_signs = ['minus','plus']
                function_components = ['AEff','EDisp' ] 
        
            for sign in function_signs:
                for component in function_components:
        
                    if function =='none':
                        irf=orig_irf
                    else:
                        irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                    

                    
                                        
                    #%%
                    name = 'source'+cutoff+flux
                    
                    wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+ irf+'/'+name+'/'
                    os.chdir(wd)
        
                    if component == 'EDisp':
                        irf=orig_irf      
                        
                    logfile = open('spectrum_fitting.txt', 'w')
                    
                    #%%
                    spectrum = cscripts.csspec()
                    spectrum['inobs'] = wd+obscube_file
                    spectrum['inmodel'] = wd+obsmodel_file
                    spectrum['expcube'] = wd+expcube_file
                    spectrum['psfcube'] = wd+psfcube_file
                    spectrum['bkgcube'] = wd+bkgcube_file
                    spectrum['edispcube'] = wd+edispcube_file
                    spectrum['edisp'] = True 
                    spectrum['srcname'] = name
                    spectrum['caldb'] = caldb
                    spectrum['irf'] = irf
                    spectrum['outfile'] = wd+spectrum_file
                    spectrum['statistic'] = 'DEFAULT' 
                    spectrum['chatter'] = 4
                    spectrum['clobber'] = True
                    spectrum['ebinalg'] = 'LOG'
                    spectrum['emin'] = emin
                    spectrum['emax'] = emax
                    spectrum['enumbins'] = int((log10(emax/emin) * 10)) 
        # =============================================================================
        #             spectrum['ebinalg'] = 'FILE'
        #             spectrum['ebinfile'] = ebinfile
        # =============================================================================
                    
                    #computation choices:
                    spectrum['calc_ts'] = True
                    spectrum['calc_ulim'] = False
                    spectrum['fix_bkg'] = False
                    
                    #%%
                    
                    print(spectrum)
                    
                    #%%
                    
                    spectrum.logFileOpen()
                    spectrum.execute()
                    logfile.write('csspec:' + str(spectrum.telapse()) + 'seconds \n')
                    logfile.close()
                    spectrum.logFileClose()
                    
                    #%%
                    
                    plot_spectrum(wd+spectrum_file,'spectrum.pdf')
                    plt.close()
                    
                    #%%
                    
                    plot_spectrum_butterfly(wd+spectrum_file,wd+butterfly_file, 'spectrum_butterfly_binned.pdf')
                    plt.close()
                    
                    #%%
                    logfile.close()