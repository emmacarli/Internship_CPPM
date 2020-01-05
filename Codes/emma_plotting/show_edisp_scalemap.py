#Author: Emma Carli 
#if ever bracket EDisp in IRF, can use this to plot scale map of energy dispersion

import math
import gammalib
import numpy as np
import matplotlib.pyplot as plt


def get_edisp(edisp):
    """
    Plot Background template

    Parameters
    ----------
    edisp : `~gammalib.GCTAEdisp2D`
        Instrument Response Function
    """

    nengs=100
    nthetas=100
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

    # Initialise true and reconstructed energies
    etrue = gammalib.GEnergy()
    ereco = gammalib.GEnergy()

    # Loop over offset angles
    for theta in thetas:

        # Initialise rows
        row_mean = []

        # Compute detx and dety
        #detx = theta*gammalib.deg2rad
        #dety = 0.0

        # Loop over energies
        for logenergy in logenergies:

            # Set true energy
            etrue.log10TeV(logenergy)

            # Compute mean migration
            mean = 0.0
            num  = 0.0
            for migra in migras:
                if migra > 0.0:
                    ereco.log10TeV(math.log10(migra) + logenergy)
                    value  = edisp(ereco, etrue, theta*gammalib.deg2rad)
                    mean  += migra * value
                    num   += value
            if num > 0.0:
                mean /= num


            # Append value
            row_mean.append(mean)

        # Append rows
        image_mean.append(row_mean)
        
    return np.array(image_mean), logenergies, thetas, emin, emax, tmin, tmax


def plot_edisp_scalemap(edisp, edisp_bracketed, plotfile):
    edisp_bracketed,logenergies , thetas, emin, emax, tmin, tmax = get_edisp(edisp=edisp_bracketed)
    edisp,_,_ ,_,_,_,_= get_edisp(edisp= edisp)
    #logenergies&thetas is the same for both
    
    div = np.divide(edisp_bracketed, edisp, out=np.zeros_like(edisp_bracketed), where= edisp!=0)
    plt.figure()  

    image = plt.imshow(div, extent=[emin,emax,tmin,tmax],  vmin=0.8, vmax=1.2, cmap='RdGy_r', aspect=0.5)
    
    contours = plt.contour(logenergies, thetas, div, [0.0], colors=('white'))
    plt.clabel(contours, inline=1, fontsize=8)
    
    cb = plt.colorbar(image, shrink=0.6)
    cb.set_label('IRF$_{\\rm scaled}$/IRF', rotation=90)
    plt.title('Mean of energy dispersion scale map')
    plt.xlabel('log10(Energy) (TeV)')
    plt.ylabel('Offset angle (deg)')  
    plt.tight_layout()
    plt.savefig(plotfile)
    plt.close()

