#Author: Emma Carli 
# =============================================================================
# This code makes a custom energy bin file for a given IRF, 
# with 10 bins per energy decade and 3 double bins at the end of the energy range
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%%
from astropy.io import fits
from math import log10
import numpy as np
import gammalib

#%%
caldb = 'prod3b-v2' #calibration database
orig_irf = 'South_z40_50h' 
ebinfile =  '/cta/carli/CPPM_Internship/Running/ebinfile_template.fits'

#%%
#set the energy limits of the IRF by finding the most limiting components

#Get calibration database and original IRF into gammalib format
caldb_gammalib = gammalib.GCaldb('cta', caldb)        
irf_gammalib   = gammalib.GCTAResponseIrf(orig_irf, caldb_gammalib)


emin = 0.030 #TeV #set minimum at 30Gev 

emaxs = []
emaxs.append(irf_gammalib.background().table().axis_hi(irf_gammalib.background().table().axis('ENERG'),irf_gammalib.background().table().axis_bins(irf_gammalib.background().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.aeff().table().axis_hi(irf_gammalib.aeff().table().axis('ENERG'), irf_gammalib.aeff().table().axis_bins(irf_gammalib.aeff().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.psf().table().axis_hi(irf_gammalib.psf().table().axis('ENERG'), irf_gammalib.psf().table().axis_bins(irf_gammalib.psf().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.edisp().table().axis_hi(irf_gammalib.edisp().table().axis('ENERG'), irf_gammalib.edisp().table().axis_bins(irf_gammalib.edisp().table().axis('ENERG'))-1))
emax = min(emaxs) #in TeV

#%%
binlimits = np.logspace(log10(emin), log10(emax), num=int((log10(emax)-log10(emin))*10)) #create the limits of the bins, with ten bins per energy decade in the range
binlimits = np.delete(binlimits, (len(binlimits)-6,len(binlimits)-4,len(binlimits)-2)) #double up the last three bins, to avoid upper limits

newcolumn = []

for b in range(len(binlimits)-1):
    newcolumn.append(binlimits[b+1])
binlimits = np.delete(binlimits,len(binlimits)-1)
bins = np.vstack((binlimits,newcolumn))
bins = bins.transpose() * 10**9 #convert from TeV energy range to keV fits file data


ebounds = fits.open(ebinfile) #to get the energy bin file structure for reference
ebounds.info()
ebounds['PRIMARY'].header #PRIMARY only has header and no data
ebounds['EBOUNDS'].header 
edata = np.recarray(shape=(len(bins[:,0]),), dtype=[('E_MIN',float),('E_MAX',float)])
edata['E_MIN'] = bins[:,0]
edata['E_MAX'] = bins[:,1]
ebounds['EBOUNDS'].data = edata
ebounds['EBOUNDS'].header.set('TUNIT1', 'keV')
ebounds['EBOUNDS'].header.set('TUNIT2', 'keV')
ebounds.writeto(orig_irf+'_ebounds.fits', overwrite=True)


