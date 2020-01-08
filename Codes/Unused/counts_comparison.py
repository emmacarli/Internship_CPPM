#Author: Emma Carli 
# =============================================================================
# This code plots together counts from simulations using differently bracketed IRFs
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 


#%%

import matplotlib.pyplot as plt
from astropy.io import fits

#%%
orig_irf = 'South_z40_50h' 

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

#create the two figures here
fig1 = plt.figure()
ax1 = plt.gca()
fig2 = plt.figure()
ax2 = plt.gca()

for function in ['none', 'constant', 'step', 'gradient']:
    
    if function == 'none': #no bracketing
        function_signs = ['']
        function_components = ['']
    else:
        function_signs = ['minus','plus']
        function_components = ['AEff' ] #, 'EDisp'

    for sign in function_signs:
        for component in function_components:


            if function =='none':
                irf=orig_irf
            else:
                irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                
                
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+ irf +'/' 
            
            fits_file = fits.open( wd + 'source1b_residuals_binned.fits')
            fits_data = fits_file[1].data
            
            energy_bins =  [ (emin+emax)/2 for emin,emax in zip(fits_data['Emin'],fits_data['Emax']) ]
           
            #figure with count residuals
            ax1.semilogx(energy_bins,fits_data['Residuals'], label=sign+' '+function,  linewidth='0.5')
            
            #figure with total counts
            ax2.loglog(energy_bins,fits_data['Counts'], label=sign+' '+function, linewidth='0.5')

#%%

ax1.set_xlabel('Energy (TeV)')
ax1.set_ylabel('Counts')
ax1.set_title('Residuals of observed and fitted counts comparison')

ax2.set_xlabel('Energy (TeV)')
ax2.set_ylabel('Counts')
ax2.set_title('Observed counts comparison')

ax1.legend(loc='best')
ax2.legend(loc='best')
fig1.show()
fig2.show()
fig1.savefig('bracketing_countresiduals_comparison.pdf')
fig2.savefig('bracketing_counts_comparison.pdf' )
plt.close()
plt.close()

