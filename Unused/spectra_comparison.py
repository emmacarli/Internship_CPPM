#Author: Emma Carli 
# =============================================================================
# This code plots together spectra inferred from observations with differently bracketed IRFs
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%%

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
#other parameters
plt.rcParams['axes.grid'] = True

#%%
orig_irf = 'South_z40_50h' 

#%%            ax.grid()


fig = plt.figure()
ax = plt.gca()
ax.loglog()

#%%
#Loop over bracketed simulations

cmap = plt.get_cmap('tab10')
plot = 0
totalplots = 7
errorbars = False

for function in ['none', 'constant', 'step', 'gradient']:           

    
    if function == 'none': #no bracketing
        function_signs = ['']
        function_components = ['']
    else:
        function_signs = ['minus','plus']
        function_components = ['AEff'] # , 'EDisp'

    for sign in function_signs:
        for component in function_components:

            if function =='none':
                irf=orig_irf
            else:
                irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+ irf+'/'

            spectrum_file = wd + 'source1b_spectrum_binned.fits' 
            plot = plot+1
            
        #%%
            # Read spectrum file    
            fits     = gammalib.GFits(spectrum_file)
            table    = fits.table(1)
            c_energy = table['Energy']
            c_ed     = table['ed_Energy']
            c_eu     = table['eu_Energy']
            c_flux   = table['Flux']
            c_eflux  = table['e_Flux']
            c_ts     = table['TS']
            c_upper  = table['UpperLimit']
            
            # Initialise arrays to be filled
            energies    = []
            flux        = []
            ed_engs     = []
            eu_engs     = []
            e_flux      = []
            ul_energies = []
            ul_ed_engs  = []
            ul_eu_engs  = []
            ul_flux     = []
        
            # Loop over rows of the file
            nrows = table.nrows()
            for row in range(nrows):
            
                # Get Test Statistic, flux and flux error
                ts    = c_ts.real(row)
                flx   = c_flux.real(row)
                e_flx = c_eflux.real(row)
            
                # If Test Statistic is larger than 9 and flux error is smaller than
                # flux then append flux plots ...
                if ts > 9.0 and e_flx < flx:
                    energies.append(c_energy.real(row))
                    flux.append(c_flux.real(row))
                    ed_engs.append(c_ed.real(row))
                    eu_engs.append(c_eu.real(row))
                    e_flux.append(c_eflux.real(row))
            
                # ... otherwise append upper limit
                else:
                    ul_energies.append(c_energy.real(row))
                    ul_flux.append(c_upper.real(row))
                    ul_ed_engs.append(c_ed.real(row))
                    ul_eu_engs.append(c_eu.real(row))
            
            # Set upper limit errors
            yerr = [0.6 * x for x in ul_flux]
            
            # Plot the spectrum 
            color = cmap(plot/totalplots)
            
            if errorbars:
                ax.errorbar(energies, flux, label=sign+' '+function,  color=color, yerr=e_flux, xerr=[ed_engs, eu_engs], elinewidth=0.5, linestyle='none' )
                ax.errorbar(ul_energies, ul_flux, color=color, xerr=[ul_ed_engs, ul_eu_engs],yerr=yerr, uplims=True, elinewidth=0.5,   linestyle='none')
            else:
                ax.plot(energies, flux, label=sign+' '+function,  color=color,linewidth=0.5)

#%%

plt.xlabel('Energy (TeV)')
plt.ylabel(r'Flux (erg cm$^{-2}$ s$^{-1}$)')
plt.title('Flux spectrum fitted from observation counts')


ax.legend(loc='best')
if errorbars:
    fig.savefig('bracketing_spectra_comparison.pdf')
else:
    fig.savefig('bracketing_spectra_comparison_noerrobars.pdf')
plt.close()