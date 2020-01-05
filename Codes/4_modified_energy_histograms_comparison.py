#Author: Emma Carli 

# =============================================================================
# This code plots the modified energy simulations compared with the originals
# =============================================================================


from IPython import get_ipython
get_ipython().magic('reset -f') 




#%%

from astropy.io import fits
import os

from scipy import log10
import numpy as np
import matplotlib.pyplot as plt
import gammalib



#%%

#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'
#other plotting params
plt.rcParams['axes.grid'] = True

#%%

caldb = 'prod3b-v2'
orig_irf = 'South_z40_50h' 


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



bins = np.logspace(log10(emin), log10(emax), num=int(log10(emax/emin)*10)) #create ten bins per energy decade in the range for histogram
bins = [log10(x) for x in bins]
#%%

for cutoff in ['1','2','3']: #50, 100, 200 TeV
    
    for flux in ['a', 'b', 'c', 'd']: #20, 40, 60, 80 mCrab
        
        for function in ['constant', 'step', 'gradient']:
            
    
            function_signs = ['minus','plus']
            function_components = ['EDisp' ] 
        
            for sign in function_signs:
                for component in function_components:
        
                    irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                        
                    
                    if sign == 'minus':
                        scale = -0.06
                    else:
                        scale = 0.06
                                        
                    #%%
                    name = 'source'+cutoff+flux
                    
                    wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+ irf+'/'+name+'/'
                    os.chdir(wd)
                    
                    
                    fits_file = fits.open(wd+'/obs.fits')
                    fits_orig = fits.open( '/cta/carli/CPPM_Internship/Simulations_and_Analyses/South_z40_50h/'+name+'/obs.fits')


                    #Plot histogram
                    fig1 = plt.figure()
                    ax1 = plt.gca()
                    ax1.set_yscale('log')
                    ax1.set_xlabel('Log10(Energy) (TeV)')
                    ax1.set_ylabel('Number of events')
        
                    ax1.hist(log10(fits_file[1].data['ENERGY']), bins=bins, range=(log10(emin),log10(emax)), color='cornflowerblue', alpha=0.5, label='Modified' )
                    ax1.hist(log10(fits_orig[1].data['ENERGY']), bins=bins, range=(log10(emin),log10(emax)), color='salmon', alpha=0.5, label='Original')
                    ax1.set_title('Observed counts')
                    plt.legend(loc='best')
                    fig1.savefig(wd+'energy_histogram_comparison.pdf')
                    plt.close(fig1)
                                        