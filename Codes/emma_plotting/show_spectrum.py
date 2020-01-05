#Author: Emma Carli 
import matplotlib.pyplot as plt
#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'
#other plotting params
plt.rcParams['axes.grid'] = True
import gammalib


# ============= #
# Plot spectrum #
# ============= #
def plot_spectrum(filename, plotfile):
    """
    Plot spectrum

    Parameters
    ----------
    filename : str
        Name of spectrum FITS file
    plotfile : str
        Plot file name
    """
    # Read spectrum file    
    fits     = gammalib.GFits(filename)
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
    plt.figure()
    plt.loglog()
    plt.errorbar(energies, flux, yerr=e_flux, xerr=[ed_engs, eu_engs],
                 fmt='o', color='0')
    plt.errorbar(ul_energies, ul_flux, xerr=[ul_ed_engs, ul_eu_engs],
                 yerr=yerr, uplims=True, fmt='o', color='0.2')
    plt.xlabel('Energy (TeV)')
    plt.ylabel(r'E$^2$ $\times$ dN/dE (erg cm$^{-2}$ s$^{-1}$)')
    plt.title('Flux spectrum inferred from observation counts')
    plt.tight_layout()
    plt.savefig(plotfile)
    plt.close()


    # Return
    return


