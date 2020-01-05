#Author: Emma Carli 
import matplotlib.pyplot as plt
import gammalib
#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'
#other plotting params
plt.rcParams['axes.grid'] = True

# =========================== #
# Plot spectrum and butterfly #
# =========================== #
def plot_spectrum_butterfly(specfile, butterfile, plotfile):
    """
    Plot sensitivity data

    Parameters
    ----------
    specfile : str
        Name of spectrum FITS file
    butterfile : str
        Name of butterfly FITS file
    fmt : str
        Symbol format
    color : str
        Symbol color
    """
    # Read spectrum file    
    fits     = gammalib.GFits(specfile)
    table    = fits.table(1)
    c_energy = table['Energy']
    c_ed     = table['ed_Energy']
    c_eu     = table['eu_Energy']
    c_flux   = table['Flux']
    c_eflux  = table['e_Flux']
    c_ts     = table['TS']
    c_upper  = table['UpperLimit']

    # Read butterfly file
    csv = gammalib.GCsv(butterfile)

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
    butterfly_x = []
    butterfly_y = []
    line_x      = []
    line_y      = []

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

    # Loop over rows of the file
    nrows = csv.nrows()
    for row in range(nrows):

        # Compute upper edge of confidence band
        butterfly_x.append(csv.real(row,0)/1.0e6) # TeV
        butterfly_y.append(csv.real(row,2)*csv.real(row,0)*csv.real(row,0)*gammalib.MeV2erg)

        # Set line values
        line_x.append(csv.real(row,0)/1.0e6) # TeV
        line_y.append(csv.real(row,1)*csv.real(row,0)*csv.real(row,0)*gammalib.MeV2erg)

    # Loop over the rows backwards to compute the lower edge of the
    # confidence band
    for row in range(nrows):
        index = nrows - 1 - row
        butterfly_x.append(csv.real(index,0)/1.0e6)
        low_error = max(csv.real(index,3)*csv.real(index,0)*csv.real(index,0)*gammalib.MeV2erg, 1e-26)
        butterfly_y.append(low_error)

    plt.figure()
    ax = plt.gca()
    ax.set_xscale("log", nonposx='clip')
    ax.set_yscale("log", nonposy='clip')

    # Plot the spectrum 
    ax.errorbar(energies, flux, yerr=e_flux, xerr=[ed_engs, eu_engs],
                 fmt='o', color='0', label = 'Flux inferred from observations')
    ax.errorbar(ul_energies, ul_flux, xerr=[ul_ed_engs, ul_eu_engs],
                 yerr=yerr, uplims=True, fmt='o', color='0.2')

    # Plot the butterfly
    ax.plot(line_x, line_y, color='black', ls='-', label='Model')
    ax.fill(butterfly_x, butterfly_y, color='lightgrey', label='Model errors')
    ax.grid()
    ax.set_xlabel('Energy (TeV)')
    ax.set_ylabel(r'E$^2$ $\times$ dN/dE (erg cm$^{-2}$ s$^{-1}$)')
    ax.set_title('Comparison of inferred flux and fitted model')
    ax.legend()
    plt.tight_layout()
    plt.savefig(plotfile)
    plt.close()


    # Return
    return





