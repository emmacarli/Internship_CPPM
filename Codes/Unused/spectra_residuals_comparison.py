#Author: Emma Carli 
# =============================================================================
# This code allows a comparison of the residuals between fitted and observed (inferred) spectrum for each bracketing function
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 


#%%

import matplotlib.pyplot as plt
import gammalib
import os

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
orig_irf = 'South_z40_50h' 

#%%    
fig = plt.figure()
ax = plt.gca()
ax.set_xlabel('Energy (TeV)')
ax.set_ylabel(r'E$^2$ $\times$ dN/dE (erg cm$^{-2}$ s$^{-1}$)')
ax.set_title('Residuals of flux inferred from observation and fitted model')

for cutoff in ['1','2','3']: #50, 100, 200 TeV
    
    for flux in ['a', 'b', 'c', 'd']: #20, 40, 60, 80 mCrab
        
        for function in ['constant', 'step', 'gradient']:
            
            if function == 'none': #no bracketing
                function_signs = ['']
                function_components = ['']
            else:
                function_signs = ['minus','plus']
                function_components = ['AEff', 'EDisp']
        
            for sign in function_signs:
                for component in function_components:
        
        
                    if function =='none':
                        irf=orig_irf
                    else:
                        irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                        
                        
                    name = 'source'+cutoff+flux
                    
                    wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+ irf+'/'+name+'/' 
                    os.chdir(wd)
                    spectrum_file = wd + 'spectrum_binned.fits' 
                    butterfly_file = wd + 'butterfly_binned.ascii'
                
                    # Read spectrum file    
                    fits     = gammalib.GFits(spectrum_file)
                    table    = fits.table(1)
                    c_energy = table['Energy']
                    c_flux   = table['Flux']
            
                    # Read butterfly file
                    csv = gammalib.GCsv(butterfly_file)
                    
                    # Initialise arrays to be filled
                    energies    = []
                    fluxx        = []
                    line_x      = []
                    line_y      = []
                    
                    # Loop over rows of the file
                    nrows = table.nrows()
                    for row in range(nrows):       
                        energies.append(c_energy.real(row))
                        fluxx.append(c_flux.real(row))
            
                    
                    # Loop over rows of the file
                    nrows = csv.nrows()
                    for row in range(nrows):
                        # Set line values
                        line_x.append(csv.real(row,0)/1.0e6) # TeV
                        line_y.append(csv.real(row,1)*csv.real(row,0)*csv.real(row,0)*gammalib.MeV2erg)
            
                    
                    # Plot the spectrum  residuals
                    residuals =  [ obs-model for model,obs in zip(line_y,fluxx) ]
                    ax.semilogx(energies, residuals, linewidth='0.5', label=sign+' '+function)






#%%
ax.legend(loc='best')
os.chdir('/cta/carli/CPPM_Internship/Codes')
fig.savefig('bracketing_spectra_residuals_comparison.pdf')
plt.close()





