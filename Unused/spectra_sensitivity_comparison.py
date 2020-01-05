#Author: Emma Carli 
from IPython import get_ipython
get_ipython().magic('reset -sf') 

# Code parameters

#%%

import matplotlib.pyplot as plt
import cscripts
import math
import gammalib


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
irf   = 'minusstepscale_North_z20_50h' #picked south because only there can go at 50TeV.
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


#%%


logfile = open('spectra_comparison.txt', 'w') #cta/carli/CPPM_Internship/Running/
#and 




for function in ['constant', 'step', 'gradient']:
    for sign in ['minus','plus']:
        #input
        spectrum_file = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+sign+function+'scale_bracketing/source1a_spectrum/source1a_spectrum.fits' #need to change to binned later
        #output
        sensitivity_file = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+sign+function+'scale_bracketing/source1a_simulation/source1a_sensitivity.ascii' 
        observation_file = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+sign+function+'scale_bracketing/source1a_binned_analysis/source1a_obs_cube.fits' 
        #model_file = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+sign+function+'scale_bracketing/source1a_binned_analysis/source1a_obsmodel_binned2.xml' 

        #Create sensitivity file for our observation
        #%%
        
        sensitivity = cscripts.cssens() 
        sensitivity["inmodel"] = source_model #model_file
        sensitivity["inobs"] = None #observation_file
        sensitivity["srcname"] = name
        sensitivity["caldb"] = caldb
        sensitivity["irf"] = irf
        sensitivity["edisp"] = True 
        sensitivity["outfile"] = sensitivity_file
        sensitivity["offset"] = 0.5
        sensitivity["duration"] = tmax
        sensitivity["emin"] = emin
        sensitivity["emax"] = emax
        sensitivity["bins"] = (int(10 * math.log10(emax/emin)))/2 #trying to reduce computing time
        sensitivity["binsz"] = 0.02
        sensitivity["npix"] = int(2*fovradius/float(sensitivity['binsz'].value()))
        sensitivity['chatter'] = 4
        sensitivity['rad'] = fovradius
        sensitivity["enumbins"] = int(10 * math.log10(emax/emin))

        
        #%%
        
        print(sensitivity)
        
        #%%
        
        sensitivity.logFileOpen()
        sensitivity.execute()
        logfile.write('cssens, '+sign+function+'scale_bracketing:'+ str(sensitivity.telapse()) + 'seconds \n')
        sensitivity.logFileClose()
        
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
        fig = plt.figure()
        ax = plt.gca()
        plt.loglog()
        plt.grid()
        plt.errorbar(energies, flux, yerr=e_flux, xerr=[ed_engs, eu_engs],label=sign+' '+function+' flux')
        plt.errorbar(ul_energies, ul_flux, xerr=[ul_ed_engs, ul_eu_engs],yerr=yerr, uplims=True)
        plt.xlabel('Energy (TeV)')
        plt.ylabel(r'Flux (erg cm$^{-2}$ s$^{-1}$)')
        plt.title('Flux spectrum fitted from observation counts')
        
        #Flux are E $\times$ F(E), F($>$E),dN/dE for differential sensitivity, integral sensitivity and source flux respectively
        
        
        
#%%
        # Read filename
        csv = gammalib.GCsv(sensitivity_file,',')
        
        # Create dictionnary
        sensitivity = {}
        for column in range(csv.ncols()):
            name   = csv[0,column].rstrip('\r')
            values = []
            for row in range(csv.nrows()-1):
                values.append(float(csv[row+1,column]))
            sensitivity[name] = values
        
        # Check where file contains differential or integral sensitivity
        mode = 'Integral'
        if 'emax' in sensitivity:
            emax_ref = -1.0
            for value in sensitivity['emax']:
                if emax_ref < 0.0:
                    emax_ref = value
                elif emax_ref != value:
                    mode = 'Differential'
                    break
        
        # Add mode
        sensitivity['mode'] = mode
        
        # Add linear energy values
        if mode == 'Differential':
            if 'loge' in sensitivity:
                name   = 'energy'
                values = []
                for value in sensitivity['loge']:
                    values.append(math.pow(10.0, value))
                sensitivity[name] = values
        else:
            if 'emin' in sensitivity:
                name   = 'energy'
                values = []
                for value in sensitivity['emin']:
                    values.append(value)
                sensitivity[name] = values


        # Show differential sensitivity
        plt.plot(sensitivity['energy'], sensitivity['sensitivity'], marker='x', label=sign+' '+function+' sensitivity' )
        
#%%
ax.legend(loc='best')
fig.savefig('bracketing_spectra_sensitivity_comparison.pdf')
plt.close()