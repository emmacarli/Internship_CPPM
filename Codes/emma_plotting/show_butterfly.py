#Author: Emma Carli 
import gammalib
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

# ============== #
# Plot butterfly #
# ============== #
def plot_butterfly(filename, plotfile):
    """
    Plot butterfly diagram

    Parameters
    ----------
    filename : str
        Butterfly CSV file
    plotfile : str
        Plot filename
    """
    # Read butterfly file
    csv = gammalib.GCsv(filename)

    # Initialise arrays to be filled
    butterfly_x = []
    butterfly_y = []
    line_x      = []
    line_y      = []

    # Loop over rows of the file
    nrows = csv.nrows()
    for row in range(nrows):

        # Get conversion coefficient
        conv = csv.real(row,0) * csv.real(row,0) * gammalib.MeV2erg

        # Compute upper edge of confidence band
        butterfly_x.append(csv.real(row,0)/1.0e6) # TeV
        butterfly_y.append(csv.real(row,2)*conv)

        # Set line values
        line_x.append(csv.real(row,0)/1.0e6) # TeV
        line_y.append(csv.real(row,1)*conv)

    # Loop over the rows backwards to compute the lower edge of the
    # confidence band
    for row in range(nrows):
        index = nrows - 1 - row
        conv  = csv.real(index,0) * csv.real(index,0) * gammalib.MeV2erg
        butterfly_x.append(csv.real(index,0)/1.0e6)
        low_error = max(csv.real(index,3)*conv, 1e-26)
        butterfly_y.append(low_error)
    
    # Plot the butterfly and spectral line       
    plt.figure()
    plt.loglog()
    plt.plot(line_x,line_y,color='black',ls='-')
    plt.fill(butterfly_x,butterfly_y,color='lightgray')
    plt.xlabel('Energy (TeV)')
    plt.ylabel(r'E$^2$ $\times$ dN/dE (erg cm$^{-2}$ s$^{-1}$)')
    plt.title('Fitted model flux spectrum')
    plt.tight_layout()

    plt.savefig(plotfile)


    # Return
    return



