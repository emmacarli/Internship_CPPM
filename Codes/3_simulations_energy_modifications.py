#Author: Emma Carli 
# =============================================================================
# This code modifies the energies of simulations datasets with different bracketing functions. It does not modify the IRFs
# =============================================================================


from IPython import get_ipython
get_ipython().magic('reset -f') 


#%%

from astropy.io import fits
import os

from scaling_functions import gradient, step
from scipy import log10
import numpy as np
import matplotlib.pyplot as plt
import ctools
import gammalib

#%%

caldb = 'prod3b-v2' #calibration database
orig_irf = 'South_z40_50h' 
fovradius = 0.8 #radius of the field of view, degrees
offset = 0.5
ra = 83.6331 + offset 
dec = 22.0145


#%%

#Get calibration database and original IRF into gammalib format
caldb_gammalib = gammalib.GCaldb('cta', caldb)        
irf_gammalib   = gammalib.GCTAResponseIrf(orig_irf, caldb_gammalib)

emin = 0.1 #TeV #set minimum at 100Gev 

#find smallest max energy range
emaxs = []
emaxs.append(irf_gammalib.background().table().axis_hi(irf_gammalib.background().table().axis('ENERG'),irf_gammalib.background().table().axis_bins(irf_gammalib.background().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.aeff().table().axis_hi(irf_gammalib.aeff().table().axis('ENERG'), irf_gammalib.aeff().table().axis_bins(irf_gammalib.aeff().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.psf().table().axis_hi(irf_gammalib.psf().table().axis('ENERG'), irf_gammalib.psf().table().axis_bins(irf_gammalib.psf().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.edisp().table().axis_hi(irf_gammalib.edisp().table().axis('ENERG'), irf_gammalib.edisp().table().axis_bins(irf_gammalib.edisp().table().axis('ENERG'))-1))
emax = min(emaxs) #in TeV

breakpoints = log10(((0.15,0.11), (5.0, 0.06))) #breakpoints of the step function, as per paper


bins = np.logspace(log10(emin), log10(emax), num=int(log10(emax/emin)*10)) #create ten bins per energy decade in the range for histogram
bins = [log10(x) for x in bins]

#%%

for cutoff in ['1','2','3']: #50, 100, 200 TeV
    
    for flux in ['a', 'b', 'c', 'd']: #20, 40, 60, 80 mCrab
        
        for function in ['constant', 'step', 'gradient']: #bracketing functions 
            
    
            function_signs = ['minus','plus']
            function_components = ['EDisp'] 
        
            for sign in function_signs:
                for component in function_components:
        
                    irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                        
                    
                    if sign == 'minus':
                        scale = -0.06
                    else:
                        scale = 0.06
                                        
                    #%%
                    name = 'source'+cutoff+flux #name of the source
                    
                    wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+ irf+'/'+name+'/'
                    os.makedirs(wd)
                    os.chdir(wd)
                    
                    logfile = open('simulation.txt', 'w')
                    
                    fits_file = fits.open( '/cta/carli/CPPM_Internship/Simulations_and_Analyses/South_z40_50h/'+name+'/obs.fits')
                    fits_file[1].data.sort(order='ENERGY')
                    
                    if function == 'constant':
                        fits_file[1].data['ENERGY'] = fits_file[1].data['ENERGY'] * (1 + scale)
                    if function == 'step':
                        fits_file[1].data['ENERGY'] = fits_file[1].data['ENERGY'] * (1 + (scale*step(log10(fits_file[1].data['ENERGY']),breakpoints)))
                    if function == 'gradient':
                        fits_file[1].data['ENERGY'] = fits_file[1].data['ENERGY'] * (1 + (scale*gradient(log10(fits_file[1].data['ENERGY']), log10(emin), log10(emax))))
                    
                    fits_file.writeto(wd+'obs.fits')
                    
                    #Plot histogram
                    fig1 = plt.figure()
                    ax1 = plt.gca()
                    ax1.set_yscale('log')
                    ax1.set_xlabel('Log10(Energy) (TeV)')
                    ax1.set_ylabel('Number of events')
        
                    ax1.hist(log10(fits_file[1].data['ENERGY']), bins=bins, range=(log10(emin),log10(emax)), edgecolor='black', color='0' )
                    ax1.set_title('Observed counts')
                    fig1.savefig(wd+'energy_histogram.pdf')
                    plt.close(fig1)
                    
                                       
                    #%%
                    
                    #Generate skymap of the new "simulation"
                    skymap = ctools.ctskymap()
                    skymap['inobs'] = wd+'obs.fits'
                    skymap["caldb"] = caldb
                    skymap['irf'] = irf
                    skymap["usepnt"] = True #use the simulation's pointing to find sky position
                    skymap["binsz"] = 0.02 #spatial resolution
                    skymap["nxpix"] = int(2*fovradius/float(skymap['binsz'].value()))
                    skymap["nypix"] = int(skymap['nxpix'].value())
                    skymap["emin"] = emin
                    skymap["emax"] = emax
                    skymap["outmap"] = wd+'skymap.fits'
                    skymap['chatter'] = 4
                    skymap["bkgsubtract"] = "NONE"   #or "IRF"
                    
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
                               norm=SymLogNorm(1), cmap='viridis' ) 
                    ax2.set_xlabel('R.A. (deg)')
                    ax2.set_ylabel('Dec (deg)')
                    cbar = plt.colorbar(image, ax=ax2)
                    cbar.set_label('Counts')
                    ax2.set_title('Map of observed counts') 
                    fig2.savefig(wd+'skymap.pdf')
                    plt.close(fig2)
                    
                    #%%
                    
                    logfile.close()
            
                    

                    