#Author: Emma Carli 
import math
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

# ======================= #
# Set residual label text #
# ======================= #
def set_residual_label(algorithm):
    """
    Set residual label text for a given algorithm.

    Parameters
    ----------
    algorithm : str
        Algorithm

    Returns
    -------
    label : str
        Label text
    """
    # Set algorithm dependent residual label text
    if algorithm == 'SUB':
        label = 'Residuals (counts)'
    elif algorithm == 'SUBDIV':
        label = 'Residuals (fraction)'
    elif algorithm == 'SUBDIVSQRT' or algorithm == 'SIGNIFICANCE':
        label = r'Residuals ($\sigma$)'
    else:
        label = ''

    # Return label
    return label


# ================================= #
# Fill counts/model/residual arrays #
# ================================= #
def fill_cmr(row, counts, model, resid, e_counts, e_resid, c_counts, c_model,
             c_resid, algorithm):
    """
    Helper function that fills in the counts, model, residuals lists and
    calculate relative errors for given table row

    Parameters
    ----------
    row : int
        Table row index
    counts : list of float
        Counts
    model : list of float
        Model
    resid : list of float
        Residual
    e_counts : list of float
        Counts error
    e_resid : list of float
        Residual error
    c_counts : `~gammalib.GFitsTableCol'
        Counts FITS table column
    c_model : `~gammalib.GFitsTableCol'
        Model FITS table column
    c_resid : `~gammalib.GFitsTableCol'
        Residual FITS table column
    algorithm : str
        Algorithm

    Returns
    -------
    counts, model, resid, e_counts, e_resid : tuple of float
        Counts, model and residual arrays
    """
    # Extract values
    counts.append(c_counts.real(row))
    model.append(c_model.real(row))
    resid.append(c_resid.real(row))

    # Calculate count error
    err = math.sqrt(c_counts.real(row))
    if err == 1:
        err = 0.99 # This prevents visualization problem in matplotlib
    e_counts.append(err)

    # Calculate residual error
    if algorithm == 'SUB':
        e_resid.append(err)
    elif algorithm == 'SUBDIV':
        if c_model.real(row) > 0.:
            e_resid.append(err / c_model.real(row))
        else:
            e_resid.append(0.)
    elif algorithm == 'SUBDIVSQRT':
        if c_model.real(row) > 0.:
            e_resid.append(err / math.sqrt(c_model.real(row)))
        else:
            e_resid.append(0.)
    elif algorithm == 'SIGNIFICANCE':
        e_resid.append(1.0)
    else:
        e_resid.append(0.0)

    # Return tuple
    return counts, model, resid, e_counts, e_resid


# ====================== #
# Plot residual spectrum #
# ====================== #
def plot_residuals(filename, plotfile):
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
    c_emin   = table['Emin']
    c_emax   = table['Emax']
    c_counts = table['Counts']
    c_model  = table['Model']
    c_resid  = table['Residuals']


    # Initialise arrays to be filled
    ebounds      = []
    ed_engs      = []
    eu_engs      = []
    em_engs      = []
    counts       = []
    e_counts     = []
    model        = []
    resid        = []
    e_resid      = []


    # Residual algorithm
    algorithm = table.header()['ALGORITHM'].string()

    # Loop over rows of the file
    nrows = table.nrows()

    # Add first energy boundary
    ebounds.append(c_emin.real(0))
    for row in range(nrows):

        # Boundaries
        ebounds.append(c_emax.real(row))

        # Geometrical mean energy and errors
        emean = math.sqrt(c_emin.real(row) * c_emax.real(row))
        em_engs.append(emean)
        ed_engs.append(emean - c_emin.real(row))
        eu_engs.append(c_emax.real(row) - emean)

        # counts, model, residuals
        counts, model, resid, e_counts, e_resid = fill_cmr(row, counts, model,
                                                           resid, e_counts,
                                                           e_resid, c_counts,
                                                           c_model, c_resid,
                                                           algorithm)



    # Initialise figure
    axarr = []

    f   = plt.figure()
    ax1 = f.add_subplot(211)
    ax2 = f.add_subplot(212)
    axarr.append(ax1)
    axarr.append(ax2)
    f.subplots_adjust(hspace=0)

    axarr[0].set_xscale('log')
    axarr[1].set_xscale('log')
    axarr[0].set_yscale('log')
    axarr[1].set_yscale('symlog')

    # Counts and model
    axarr[0].errorbar(em_engs, counts, yerr=e_counts, xerr=[ed_engs, eu_engs],
                      fmt='none', capsize=0, linewidth=0.5, zorder=2, label='Data', color='black')
    axarr[0].plot(ebounds, model, color='indianred', linewidth=1.5, zorder=1,
                      label='Fitted model', drawstyle ='steps')
    axarr[0].set_ylabel('Counts')

    # Residuals
    axarr[1].errorbar(em_engs, resid, 
                      fmt='o', markersize=2, capsize=0, linewidth=0.5, color='black') #yerr=e_resid, xerr=[ed_engs, eu_engs]
    axarr[1].set_xlabel('Energy (TeV)')
    axarr[1].set_ylabel(set_residual_label(algorithm))


    # Add spectra of individual components. Skip all standard columns.
    skiplist = ['Counts', 'Model', 'Residuals', 'Counts_Off', 'Model_Off',
                'Residuals_Off', 'Emin', 'Emax']
    colors = ['black','darkred']
    i = -1
    for s in range(table.ncols()):
        if table[s].name() not in skiplist:
            component = []
            for row in range(nrows):
                component.append(table[s].real(row))
            component = [component[0]] + component
            i = i+1
            if table[s].name()=='BackgroundModel':
                label = 'Background'
            else:
                label = 'Source'
            axarr[0].plot(ebounds, component, zorder=0, linewidth=2.5, label=label, drawstyle ='steps', color=colors[i])

    # Add legend
    axarr[0].legend(loc='best', prop={'size': 10})
    plt.suptitle('Counts: observed and fitted model')
    # Save figure
    plt.savefig(plotfile)
    plt.close()


    # Return
    return

