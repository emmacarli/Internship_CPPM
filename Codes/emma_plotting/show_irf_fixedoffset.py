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



# =============== #
# Plot Background #
# =============== #
def plot_background_fixedoffset(sub, background, offset):
    """
    Plot Background template at fixed offset angle

    Parameters
    ----------
    sub : figure
        Subplot    
    background : `~gammalib.GCTABackground3D`
        Instrument Response Function Background
    offset : float, optional
       Value of fixed offset angle in degrees
    """
    nengs = 100
    # Determine energy range
    if background.table().has_axis('ENERG'):
        ieng = background.table().axis('ENERG')
    else:
        ieng = background.table().axis('ETRUE')
    neng = background.table().axis_bins(ieng)

    emin = background.table().axis_lo(ieng, 0)

    emax = background.table().axis_hi(ieng, neng-1)

    # Use log energies
    emin = math.log10(emin)
    emax = math.log10(emax)

    # Set energy axis
    denergy     = (emax - emin)/(nengs-1)
    logenergies = [emin+i*denergy for i in range(nengs)]


    backgrounds=[]


    # Loop over energies
    for logenergy in logenergies:

        # Get background acceptance value
        value = background(logenergy, offset*gammalib.deg2rad, 0.0)

        # Append value
        backgrounds.append(value)




    plt.semilogy(logenergies, backgrounds)
    sub.set_xlabel('log10(E/TeV)')
    sub.set_ylabel('s$^{-1}$ MeV$^{-1}$ sr$^{-1}$')
    sub.set_title('Background acceptance')
    



    # Return
    return


# ========= #
# Plot Aeff #
# ========= #
def plot_aeff_fixedoffset(sub ,aeff, offset):
    """
    Plot effective area at fixed offset angle

    Parameters
    ----------
    sub : figure
        Subplot
    aeff : `~gammalib.GCTAAeff2d`
        Instrument Response Function Effective Area
    offset : float, optional
        Value of fixed offset angle
    """
    nengs = 100
    # Determine energy range
    if aeff.table().has_axis('ENERG'):
        ieng = aeff.table().axis('ENERG')
    else:
        ieng = aeff.table().axis('ETRUE')
    neng = aeff.table().axis_bins(ieng)

    emin = aeff.table().axis_lo(ieng, 0)

    emax = aeff.table().axis_hi(ieng, neng-1)

    # Use log energies
    emin = math.log10(emin)
    emax = math.log10(emax)

    # Set energy axis
    denergy     = (emax - emin)/(nengs-1)
    logenergies = [emin+i*denergy for i in range(nengs)]


    aeffs=[]


    # Loop over energies
    for logenergy in logenergies:

        # Get effective area value
        value = aeff(logenergy, offset*gammalib.deg2rad, 0.0)

        # Append value
        aeffs.append(value)



 
    plt.semilogy(logenergies, aeffs)

    sub.set_xlabel('log10(E/TeV)')
    sub.set_ylabel('cm$^2$')
    sub.set_title('Effective area')
    






    # Return
    return




# ======== #
# Plot PSF #
# ======== #
def plot_psf_fixedoffset(sub, psf, offset, label):
    """
    Plot point spread function at fixed offset angle

     Parameters
    ----------
    sub : figure
        Subplot    
    psf : `~gammalib.GCTAPsf2D`
        Instrument Response Function PSF
    offset : float, optional
       Value of fixed offset angle
    label : str
       Name of the bracketed IRF if applicable
    """
    nengs = 100
    # Determine energy range
    if psf.table().has_axis('ENERG'):
        ieng = psf.table().axis('ENERG')
    else:
        ieng = psf.table().axis('ETRUE')
    neng = psf.table().axis_bins(ieng)

    emin = psf.table().axis_lo(ieng, 0)

    emax = psf.table().axis_hi(ieng, neng-1)

    # Use log energies
    emin = math.log10(emin)
    emax = math.log10(emax)

    # Set energy axis
    denergy     = (emax - emin)/(nengs-1)
    logenergies = [emin+i*denergy for i in range(nengs)]


    psfs=[]


    # Loop over energies
    for logenergy in logenergies:

        # Get containment radius value
        value = psf.containment_radius(0.68, logenergy, offset*gammalib.deg2rad) * \
                    gammalib.rad2deg

        # Append value
        psfs.append(value)



    plt.plot(logenergies, psfs, label=label)
    sub.set_xlabel('log10(E/TeV)')
    sub.set_ylabel('deg')


    # Plot title and axis
    if psf.classname() == 'GCTAPsfKing':
        sub.set_title('King function PSF 68% containment radius')
    else:
        sub.set_title('Gaussian PSF 68% containment radius')
    





    # Return
    return
















# ====================== #
# Plot energy dispersion #
# ====================== #
def plot_edisp_fixedoffset(edisp, offset):
    """
    Plot Background template

    Parameters
    ----------  
    edisp : `~gammalib.GCTAEdisp2D`
        Instrument Response Function Energy Dispersion
    offset : float, optional
       Value of fixed offset angle
    """
    nengs = 100
    # Determine energy range
    if edisp.table().has_axis('ENERG'):
        ieng = edisp.table().axis('ENERG')
    else:
        ieng = edisp.table().axis('ETRUE')
    neng = edisp.table().axis_bins(ieng)

    emin = edisp.table().axis_lo(ieng, 0)

    emax = edisp.table().axis_hi(ieng, neng-1)

    # Determine migration range
    imigra   = edisp.table().axis('MIGRA')
    nmigra   = edisp.table().axis_bins(imigra)
    migramin = edisp.table().axis_lo(imigra, 0)
    migramax = edisp.table().axis_hi(imigra, nmigra-1)


    # Use log energies
    emin = math.log10(emin)
    emax = math.log10(emax)

    # Set axes
    denergy     = (emax - emin)/(nengs-1)
    dmigra      = (migramax - migramin)/(nmigra-1)
    logenergies = [emin+i*denergy for i in range(nengs)]
    migras      = [migramin+i*dmigra  for i in range(nmigra)]


    # Initialise true and reconstructed energies
    etrue = gammalib.GEnergy()
    ereco = gammalib.GEnergy()

    # Initialise rows
    means = []
    stds  = []

    # Compute detx and dety
    #detx = theta*gammalib.deg2rad
    #dety = 0.0

    # Loop over energies
    for logenergy in logenergies:

        # Set true energy
        etrue.log10TeV(logenergy)

        # Compute mean migration
        mean = 0.0
        std  = 0.0
        num  = 0.0
        for migra in migras:
            if migra > 0.0:
                ereco.log10TeV(math.log10(migra) + logenergy)
                value  = edisp(ereco, etrue, offset*gammalib.deg2rad)
                mean  += migra * value
                std   += migra * migra * value
                num   += value
        if num > 0.0:
            mean /= num
            std  /= num
            arg   = std - mean * mean
            if arg > 0.0:
                std = math.sqrt(arg)
            else:
               std = 0.0
        # Append value
        means.append(mean)
        stds.append(std)


    # First subplot
    f1 = plt.subplot(223)
    f1.plot(logenergies, means)



    # Plot title and axis
    f1.set_title('Mean of energy dispersion')
    f1.set_xlabel('log10(Energy) (TeV)')
    f1.set_ylabel('E$_{reco}$ / E$_{true}$')

    

    # Second subplot
    f2 = plt.subplot(224)
    f2.plot(logenergies, stds)



    # Plot title and axis
    f2.set_title('Standard deviation of energy dispersion')
    f2.set_xlabel('log10(Energy) (TeV)')
    f2.set_ylabel('E$_{reco}$ / E$_{true}$')

    
    # Return
    return
















































# ======== #
# Plot IRF #
# ======== #
def plot_irf_fixedoffset(irf, fig=plt.figure(figsize=(16,8)), offset=0.5, label=''):
    """
    Plot Instrument Response Function

    Parameters
    ----------
    irf : `~gammalib.GCTAResponseIrf`
        Instrument Response Function
    fig : figure object
        Figure to allow plotting IRFs on top of each other
    offset : float, optional
       Value of fixed offset angle
    label : str
       Name of the bracketed IRF if applicable
    """
 
    # Build title
    mission    = irf.caldb().mission()
    instrument = irf.caldb().instrument()
    response   = irf.rspname()
    title      = '%s "%s" Instrument Response Function "%s" at %s degree offset' % \
                 (gammalib.toupper(mission), instrument, response, str(offset))


    # Add title
    fig.suptitle(title)

    # Plot Aeff
    ax1 = fig.add_subplot(231)
    plot_aeff_fixedoffset(ax1, irf.aeff(), offset=offset)


    # Plot Psf
    ax2 = fig.add_subplot(232)
    plot_psf_fixedoffset(ax2, irf.psf(),offset=offset, label=label)


    # Plot Background
    ax3 = fig.add_subplot(233)
    plot_background_fixedoffset(ax3, irf.background(), offset=offset)


    

    # Plot Edisp
    fig.add_subplot(234)
    plot_edisp_fixedoffset(irf.edisp(), offset=offset)

    plt.subplots_adjust(hspace=0.5)


    #no saving to plotfile so that can plot several irfs on top of each other.


    # Return
    return


