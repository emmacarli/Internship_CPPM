
import math
import gammalib
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.colors import LogNorm


#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'
#other plotting params
plt.rcParams['axes.grid'] = True

# ========= #
# Plot Aeff #
# ========= #
def plot_aeff(sub, aeff):
    """
    Plot effective area

    Parameters
    ----------
    sub : figure
        Subplot
    aeff : `~gammalib.GCTAAeff2d`
        Instrument Response Function
    """

    nengs = 100
    nthetas = 100

    # Determine energy range
    if aeff.table().has_axis('ENERG'):
        ieng = aeff.table().axis('ENERG')
    else:
        ieng = aeff.table().axis('ETRUE')
    neng = aeff.table().axis_bins(ieng)

    emin = aeff.table().axis_lo(ieng, 0)

    emax = aeff.table().axis_hi(ieng, neng-1)

    # Determine offset angle range
    itheta = aeff.table().axis('THETA')
    ntheta = aeff.table().axis_bins(itheta)

    tmin = aeff.table().axis_lo(itheta, 0)

    tmax = aeff.table().axis_hi(itheta, ntheta-1)

    # Use log energies
    emin = math.log10(emin)
    emax = math.log10(emax)

    # Set axes
    denergy     = (emax - emin)/(nengs-1)
    dtheta      = (tmax - tmin)/(nthetas-1)
    logenergies = [emin+i*denergy for i in range(nengs)]
    thetas      = [tmax-i*dtheta  for i in range(nthetas)]

    # Initialise image
    image = []

    # Loop over offset angles
    for theta in thetas:

        # Initialise row
        row = []

        # Loop over energies
        for logenergy in logenergies:

            # Get effective area value
            value = aeff(logenergy, theta*gammalib.deg2rad)

            # Append value
            row.append(value)

        # Append row
        image.append(row)

    # Plot image
    c    = sub.imshow(image, extent=[emin,emax,tmin,tmax], aspect=0.5, vmin=1e6, norm=LogNorm())
    cbar = plt.colorbar(c, orientation='horizontal', pad=0.2, shrink=0.8)
    cbar.set_label('cm$^2$')

    # Show boundary contours
    contours = sub.contour(logenergies, thetas, image, [0.0], colors=('white'))
    sub.clabel(contours, inline=1, fontsize=8)

    # Plot title and axis
    sub.set_title('Effective area')
    sub.set_xlabel('log10(E/TeV)')
    sub.set_ylabel('Offset angle (deg)')
    

    # Return
    return


# ======== #
# Plot PSF #
# ======== #
def plot_psf(sub, psf):
    """
    Plot Point Spread Function

    Parameters
    ----------
    sub : figure
        Subplot
    psf : `~gammalib.GCTAPsf2D`
        Instrument Response Function
    """

    nengs = 100
    nthetas = 100

    # Determine energy range
    if psf.table().has_axis('ENERG'):
        ieng = psf.table().axis('ENERG')
    else:
        ieng = psf.table().axis('ETRUE')
    neng = psf.table().axis_bins(ieng)

    emin = psf.table().axis_lo(ieng, 0)
    emax = psf.table().axis_hi(ieng, neng-1)

    # Determine offset angle range
    itheta = psf.table().axis('THETA')
    ntheta = psf.table().axis_bins(itheta)

    tmin = psf.table().axis_lo(itheta, 0)
    tmax = psf.table().axis_hi(itheta, ntheta-1)

    # Use log energies
    emin = math.log10(emin)
    emax = math.log10(emax)

    # Set axes
    denergy     = (emax - emin)/(nengs-1)
    dtheta      = (tmax - tmin)/(nthetas-1)
    logenergies = [emin+i*denergy for i in range(nengs)]
    thetas      = [tmax-i*dtheta  for i in range(nthetas)]

    # Initialise image
    image = []

    # Loop over offset angles
    for theta in thetas:

        # Initialise row
        row = []

        # Loop over energies
        for logenergy in logenergies:

            # Get containment radius value
            value = psf.containment_radius(0.68, logenergy, theta*gammalib.deg2rad) * \
                    gammalib.rad2deg

            # Append value
            row.append(value)

        # Append row
        image.append(row)

    # Plot image
    c    = sub.imshow(image, extent=[emin,emax,tmin,tmax], aspect=0.5) #, vmin=0.0, vmax=18/60)
    cbar = plt.colorbar(c, orientation='horizontal', pad=0.2, shrink=0.8)
    tick_locator = ticker.MaxNLocator(nbins=5)
    cbar.locator = tick_locator
    cbar.set_label('deg')

    # Show boundary contours
    contours = sub.contour(logenergies, thetas, image, [0.0], colors=('white'))
    sub.clabel(contours, inline=1, fontsize=8)

    # Plot title and axis
    if psf.classname() == 'GCTAPsfKing':
        sub.set_title('King function PSF 68% containment radius')
    else:
        sub.set_title('Gaussian PSF 68% containment radius')
    sub.set_xlabel('log10(E/TeV)')
    sub.set_ylabel('Offset angle (deg)')

    

    # Return
    return


# ====================== #
# Plot energy dispersion #
# ====================== #
def plot_edisp(edisp):
    """
    Plot Background template

    Parameters
    ----------
    edisp : `~gammalib.GCTAEdisp2D`
        Instrument Response Function
    """


    nengs = 100
    nthetas = 100

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

    # Determine offset angle range
    itheta = edisp.table().axis('THETA')
    ntheta = edisp.table().axis_bins(itheta)

    tmin = edisp.table().axis_lo(itheta, 0)

    tmax = edisp.table().axis_hi(itheta, ntheta-1)

    # Use log energies
    emin = math.log10(emin)
    emax = math.log10(emax)

    # Set axes
    denergy     = (emax - emin)/(nengs-1)
    dmigra      = (migramax - migramin)/(nmigra-1)
    dtheta      = (tmax - tmin)/(nthetas-1)
    logenergies = [emin+i*denergy for i in range(nengs)]
    migras      = [migramin+i*dmigra  for i in range(nmigra)]
    thetas      = [tmax-i*dtheta  for i in range(nthetas)]

    # Initialise images
    image_mean = []
    image_std  = []

    # Initialise true and reconstructed energies
    etrue = gammalib.GEnergy()
    ereco = gammalib.GEnergy()

    # Loop over offset angles
    for theta in thetas:

        # Initialise rows
        row_mean = []
        row_std  = []

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
                    value  = edisp(ereco, etrue, theta*gammalib.deg2rad)
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
            row_mean.append(mean)
            row_std.append(std)

        # Append rows
        image_mean.append(row_mean)
        image_std.append(row_std)

    # First subplot
    f1 = plt.subplot(223)

    # Plot image
    c1    = f1.imshow(image_mean, extent=[emin,emax,tmin,tmax], aspect=0.5)
    cbar1 = plt.colorbar(c1, orientation='horizontal', pad=0.2, shrink=0.8)
    tick_locator = ticker.MaxNLocator(nbins=5)
    cbar1.locator = tick_locator
    cbar1.set_label('E$_{reco}$ / E$_{true}$')

    # Show boundary contours
    contours = f1.contour(logenergies, thetas, image_mean, [0.0], colors=('white'))
    f1.clabel(contours, inline=1, fontsize=8)

    # Plot title and axis
    f1.set_title('Mean of energy dispersion')
    f1.set_xlabel('log10(E/TeV)')
    f1.set_ylabel('Offset angle (deg)')
    

    # Second subplot
    f2 = plt.subplot(224)

    # Plot image
    c2    = f2.imshow(image_std, extent=[emin,emax,tmin,tmax], aspect=0.5)
    cbar2 = plt.colorbar(c2, orientation='horizontal', pad=0.2, shrink=0.8)
    tick_locator = ticker.MaxNLocator(nbins=5)
    cbar2.locator = tick_locator
    cbar2.set_label('E$_{reco}$ / E$_{true}$')

    # Show boundary contours
    contours = f2.contour(logenergies, thetas, image_std, [0.0], colors=('white'))
    f2.clabel(contours, inline=1, fontsize=8)

    # Plot title and axis
    f2.set_title('Standard deviation of energy dispersion')
    f2.set_xlabel('log10(E/TeV)')
    f2.set_ylabel('Offset angle (deg)')
    

    # Return
    return


# =============== #
# Plot Background #
# =============== #
def plot_bkg(sub, bkg):
    """
    Plot Background template

    Parameters
    ----------
    sub : figure
        Subplot
    bkg : `~gammalib.GCTABackground3D`
        Instrument Response Function
    """

    nengs = 100
    nthetas = 100
    # Determine energy range
    if bkg.table().has_axis('ENERG'):
        ieng = bkg.table().axis('ENERG')
    else:
        ieng = bkg.table().axis('ETRUE')
    neng = bkg.table().axis_bins(ieng)

    emin = bkg.table().axis_lo(ieng, 0)

    emax = bkg.table().axis_hi(ieng, neng-1)

    # Determine offset angle range

    tmin = 0.0

    tmax = 6.0

    # Use log energies
    emin = math.log10(emin)
    emax = math.log10(emax)

    # Set axes
    denergy     = (emax - emin)/(nengs-1)
    dtheta      = (tmax - tmin)/(nthetas-1)
    logenergies = [emin+i*denergy for i in range(nengs)]
    thetas      = [tmax-i*dtheta  for i in range(nthetas)]

    # Initialise image
    vmin  = None
    vmax  = None
    image = []

    # Loop over offset angles
    for theta in thetas:

        # Initialise row
        row = []

        # Compute detx and dety
        detx = theta*gammalib.deg2rad
        dety = 0.0

        # Loop over energies
        for logenergy in logenergies:

            # Get containment radius value
            value = bkg(logenergy, detx, dety)

            # Append value
            row.append(value)

            # Set minimum and maximum
            if value > 0.0:
                if vmin == None:
                    vmin = value
                elif value < vmin:
                    vmin = value
                if vmax == None:
                    vmax = value
                elif value > vmax:
                    vmax = value

        # Append row
        image.append(row)

    # Plot image
    c    = sub.imshow(image, extent=[emin,emax,tmin,tmax], aspect=0.5,
                      vmin=vmin, vmax=vmax, norm=LogNorm())
    cbar = plt.colorbar(c, orientation='horizontal', pad=0.2, shrink=0.8)
    cbar.set_label('s$^{-1}$ MeV$^{-1}$ sr$^{-1}$')

    # Show boundary contours
    contours = sub.contour(logenergies, thetas, image, [0.0], colors=('white'))
    sub.clabel(contours, inline=1, fontsize=8)

    # Plot title and axis
    sub.set_title('Background acceptance')
    sub.set_xlabel('log10(E/TeV)')
    sub.set_ylabel('Offset angle (deg)')
    

    # Return
    return


# ======== #
# Plot IRF #
# ======== #
def plot_irf(irf,plotfile):
    """
    Plot Instrument Response Function

    Parameters
    ----------
    irf : `~gammalib.GCTAResponseIrf`
        Instrument Response Function
    plotfile : str
        Plot filename
    """

    # Build title
    mission    = irf.caldb().mission()
    instrument = irf.caldb().instrument()
    response   = irf.rspname()
    title      = '%s "%s" Instrument Response Function "%s"' % \
                 (gammalib.toupper(mission), instrument, response)

    # Create figure
    fig = plt.figure(figsize=(16,8))

    # Add title
    fig.suptitle(title)

    # Plot Aeff
    ax1 = fig.add_subplot(231)
    plot_aeff(ax1, irf.aeff())

    # Plot Psf
    ax2 = fig.add_subplot(232)
    plot_psf(ax2, irf.psf())

    # Plot Background
    ax3 = fig.add_subplot(233)
    plot_bkg(ax3, irf.background())


    # Plot Edisp
    fig.add_subplot(234)
    plot_edisp(irf.edisp())


    plt.savefig(plotfile)
    plt.close()

    # Return
    return

