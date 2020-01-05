#Author: Emma Carli 
# =============================================================================
# This code produces a max likelihood model from an observation
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%%

import ctools
import matplotlib.pyplot as plt
import cscripts
import os
import gammalib
from scipy import log10

from emma_plotting.show_butterfly import plot_butterfly
from emma_plotting.show_residuals import plot_residuals

#%%
#General simulation parameters

caldb = 'prod3b-v2' #calibration database
orig_irf = 'South_z40_50h' 
tmin = 0.0
tmax = 3600*40 #length of observation

fovradius = 0.8 #radius of the field of view, degrees
#ebinfile =  '/cta/carli/CPPM_Internship/Running/'+ orig_irf+'_ebounds.fits' #define the energy bins with a custom fits file
offset = 0.5 #deg


#%%
#set the energy limits of the IRF by finding the most limiting components

#Get calibration database and original IRF into gammalib format
caldb_gammalib = gammalib.GCaldb('cta', caldb)        
irf_gammalib   = gammalib.GCTAResponseIrf(orig_irf, caldb_gammalib)

emin = 0.1 #TeV #set minimum at 100Gev 

emaxs = []
emaxs.append(irf_gammalib.background().table().axis_hi(irf_gammalib.background().table().axis('ENERG'),irf_gammalib.background().table().axis_bins(irf_gammalib.background().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.aeff().table().axis_hi(irf_gammalib.aeff().table().axis('ENERG'), irf_gammalib.aeff().table().axis_bins(irf_gammalib.aeff().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.psf().table().axis_hi(irf_gammalib.psf().table().axis('ENERG'), irf_gammalib.psf().table().axis_bins(irf_gammalib.psf().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.edisp().table().axis_hi(irf_gammalib.edisp().table().axis('ENERG'), irf_gammalib.edisp().table().axis_bins(irf_gammalib.edisp().table().axis('ENERG'))-1))
emax = min(emaxs) #in TeV

#%%
#source1b-specific parameters

ra = 83.6331 + offset 
dec = 22.0145

#%%

#Input file
events_file = 'obs.fits'
#Output files
obscube_file = 'obs_cube.fits'
expcube_file = 'exposure_cube.fits'
psfcube_file = 'PSF_cube.fits'
bkgcube_file = 'background_cube.fits'
edispcube_file = 'edisp_cube.fits'
obsmodel_file = 'obsmodel_binned.xml' #fitted model from observations
butterfly_file = 'butterfly_binned.ascii' #fitted model flux with errors
obsmodelcube_file = 'obsmodel_cube.fits' #binned fitted model
residuals_file = 'residuals_binned.fits' #residuals between flux observations (inferred from counts) and fitted model

source_model_cube_file = 'sourcemodel_cube.xml' #input source model, but binned

#%%
#Generate fit for each IRF version
for cutoff in ['1','2','3']: #50, 100, 200 TeV
    
    for flux in ['a', 'b', 'c', 'd']: #20, 40, 60, 80 mCrab
        for function in ['none', 'constant', 'step', 'gradient']: #'none',
            
            if function == 'none': #if there is no bracketing
                function_signs = ['']
                function_components = ['']
            else:
                function_signs = ['minus','plus']
                function_components = ['AEff','EDisp' ]
        
            for sign in function_signs:
                for component in function_components:
        
                    if function =='none':
                        irf=orig_irf
                    else:
                        irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                    
                    name = 'source'+cutoff+flux
                    source_model = '${CTOOLS}/share/models/'+name+'.xml'

                    
                    wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
                    os.chdir(wd)
                    
                    if component == 'EDisp':
                        irf=orig_irf
        
                    logfile = open('data_analysis_binned.txt', 'w')
                              
                    #%%
                    
                    obscube = ctools.ctbin() #bin the simulation observation
                    obscube['inobs'] = wd+events_file
                    obscube['outobs'] = wd+obscube_file
                    obscube['usepnt'] = True #use the simulation's pointing to find sky position
                    obscube['binsz'] = 0.02 #spatial resolution
                    obscube['nxpix'] = int(2*fovradius/float(obscube['binsz'].value()))
                    obscube['nypix'] = int(obscube['nxpix'].value())
                    obscube['chatter'] = 4 #max output info in the log file
                    obscube['ebinalg'] = 'LOG'
                    obscube['emin'] = emin
                    obscube['emax'] = emax
                    obscube['enumbins'] = int((log10(emax/emin) * 10)) 
        # =============================================================================
        #             obscube['ebinalg'] = 'FILE'
        #             obscube['ebinfile'] = ebinfile 
        # =============================================================================
                    
                    #%%
                    
                    print(obscube)
                    
                    #%%
                    
                    obscube.logFileOpen()
                    obscube.execute()
                    logfile.write('ctbin:' + str(obscube.telapse()) + 'seconds \n')
                    obscube.logFileClose()
                    
                    #%%
                    #Compute exposure cube : 'provides the effective area multiplied by the livetime of the observation'
        
                    expcube = ctools.ctexpcube()
                    expcube['inobs'] = wd+events_file
                    expcube['incube'] = wd+obscube_file #pixel info is taken here
                    expcube['caldb'] = caldb
                    expcube['irf'] = irf
                    expcube['addbounds'] = True #this should help with PSF/Edisp spillover (see ctools doc)
                    expcube['usepnt'] = True 
                    expcube['outcube'] = wd+expcube_file
                    expcube['chatter'] = 4
        # =============================================================================
        # parameters below are redudant because they are given by the 'incube' 
        #             expcube['ebinalg'] = 'FILE'
        #             expcube['ebinfile'] = ebinfile
        #             expcube['binsz'] = 0.02 #spatial resolution
        #             expcube['nxpix'] = int(2*fovradius/float(obscube['binsz'].value()))
        #             expcube['nypix'] = int(obscube['nxpix'].value())
        # =============================================================================
        
                    
                    #%%
                    
                    print(expcube)
                    
                    #%%
                    
                    expcube.logFileOpen()
                    expcube.execute()
                    logfile.write('ctexpcube:' + str(expcube.telapse()) + 'seconds \n')
                    expcube.logFileClose()
                    
                    #%%
                    
                    psfcube = ctools.ctpsfcube()
                    psfcube['inobs'] = wd+events_file 
                    psfcube['incube'] = '' #do not input the obscube, since we want different pixels
                    psfcube['caldb'] = caldb
                    psfcube['irf'] = irf
                    psfcube['addbounds'] = True
                    psfcube['usepnt'] = True 
                    psfcube['nxpix'] = int(2*fovradius) #since bin size is 1 degree
                    psfcube['nypix'] = int(2*fovradius)
                    psfcube['binsz'] =  1 #recommended by ctools
                    psfcube['outcube'] = wd+psfcube_file
                    psfcube['chatter'] = 4
                    psfcube['ebinalg'] = 'LOG'
                    psfcube['emin'] = emin
                    psfcube['emax'] = emax
                    psfcube['enumbins'] = int((log10(emax/emin) * 10)) 
        # =============================================================================
        #             psfcube['ebinalg'] = 'FILE'
        #             psfcube['ebinfile'] = ebinfile
        # =============================================================================
                    #angular separation bins is left at 200 as recommended
                    
                    #%%
                    
                    print(psfcube)
                    
                    #%%
                    
                    psfcube.logFileOpen()
                    psfcube.execute()
                    logfile.write('ctpsfcube:' + str(psfcube.telapse()) + 'seconds \n')
                    psfcube.logFileClose()
                    
                    #%%
                    
                    bkgcube = ctools.ctbkgcube()
                    bkgcube['inobs'] = wd+events_file
                    bkgcube['incube'] = wd+obscube_file
                    bkgcube['inmodel'] = source_model
                    bkgcube['caldb'] = caldb
                    bkgcube['irf'] = irf
                    bkgcube['outcube'] = wd+bkgcube_file
                    bkgcube['outmodel'] = wd+source_model_cube_file
                    bkgcube['chatter'] = 4
                    
                    #%%
                           
                    print(bkgcube)
                    
                    #%%
                    
                    bkgcube.logFileOpen()
                    bkgcube.execute()
                    logfile.write('ctbkgcube:' + str(bkgcube.telapse()) + 'seconds \n')
                    bkgcube.logFileClose()
                       
                    #%%
                    
                    edispcube = ctools.ctedispcube()
                    edispcube['inobs'] = wd+events_file 
                    edispcube['incube'] = ''
                    edispcube['caldb'] = caldb
                    edispcube['irf'] = irf
                    edispcube['ebinalg'] = 'LOG'
                    edispcube['emin'] = emin
                    edispcube['emax'] = emax
                    edispcube['enumbins'] = int((log10(emax/emin) * 10)) 
        # =============================================================================
        #             edispcube['ebinalg'] = 'FILE'
        #             edispcube['ebinfile'] = ebinfile
        # =============================================================================
                    edispcube['addbounds'] = True
                    edispcube['usepnt'] = True 
                    edispcube['nxpix'] = int(2*fovradius) #since bin size is 1 degree
                    edispcube['nypix'] = int(2*fovradius)
                    edispcube['binsz'] =  1 #recommended by ctools
                    edispcube['outcube'] = wd+edispcube_file
                    edispcube['chatter'] = 4
                    #energy migration bins is left at 200 
                    
                    #%%
                    
                    print(edispcube)
                    
                    #%%
                    
                    edispcube.logFileOpen()
                    edispcube.execute()
                    logfile.write('ctedispcube:' + str(edispcube.telapse()) + 'seconds \n')
                    edispcube.logFileClose()
                    
                    #%%
                    
                    obs_model = ctools.ctlike() #likelihood fitting of the observation
                    obs_model['inobs'] = wd+obscube_file
                    obs_model['expcube'] = wd+expcube_file
                    obs_model['psfcube'] = wd+psfcube_file
                    obs_model['bkgcube'] = wd+bkgcube_file
                    obs_model['edispcube'] = wd+edispcube_file
                    obs_model['inmodel'] = source_model_cube_file
                    obs_model['outmodel'] = wd+obsmodel_file
                    obs_model['caldb'] = caldb
                    obs_model['irf'] = irf
                    obs_model['statistic'] = 'DEFAULT' 
                    obs_model['chatter'] = 4
                    obs_model['edisp'] = True 
                    
                    #%%
                    
                    print(obs_model)
                    
                    #%% 
                    obs_model.logFileOpen()
                    obs_model.execute()
                    logfile.write('ctlike:' + str(obs_model.telapse()) + 'seconds \n')
                    obs_model.logFileClose()
                               
                    #%%
                    
                    
                    butterfly = ctools.ctbutterfly() #the fit flux with errors
                    butterfly['inobs'] = wd+obscube_file
                    butterfly['inmodel'] = wd+obsmodel_file
                    butterfly['outfile'] = wd+butterfly_file
                    butterfly['srcname'] = name 
                    butterfly['caldb'] = caldb
                    butterfly['expcube'] = wd+expcube_file
                    butterfly['psfcube'] = wd+psfcube_file
                    butterfly['bkgcube'] = wd+bkgcube_file
                    butterfly['edispcube'] = wd+edispcube_file
                    butterfly['irf'] = irf
                    butterfly['statistic'] = 'DEFAULT' 
                    butterfly['chatter'] = 4
                    butterfly['ebinalg'] = 'LOG'
                    butterfly['emin'] = emin
                    butterfly['emax'] = emax
                    butterfly['enumbins'] = int((log10(emax/emin) * 10)) 
        # =============================================================================
        #             butterfly['ebinalg'] = 'FILE'
        #             butterfly['ebinfile'] = ebinfile
        # =============================================================================
                    butterfly['edisp'] = True
        
                    
                    #%%
                    
                    print(butterfly)
                    
                    #%%
                    
                    butterfly.logFileOpen()
                    butterfly.execute()
                    logfile.write('ctbutterfly:' + str(butterfly.telapse()) + 'seconds \n')
                    butterfly.logFileClose()
                    
                    #%%
                    
                    plot_butterfly(wd+butterfly_file,'butterfly_binned.pdf')
                    plt.close() 
                    
                    #%%
                    obs_modelcube = ctools.ctmodel() #bin the model
                    obs_modelcube['inobs'] = wd+obscube_file
                    obs_modelcube['incube'] = wd+obscube_file
                    obs_modelcube['inmodel'] = wd+obsmodel_file
                    obs_modelcube['expcube'] = wd+expcube_file
                    obs_modelcube['psfcube'] = wd+psfcube_file
                    obs_modelcube['bkgcube'] = wd+bkgcube_file
                    obs_modelcube['edispcube'] = wd+edispcube_file
                    obs_modelcube['caldb'] = caldb
                    obs_modelcube['irf'] = irf
                    obs_modelcube['outcube'] = wd+obsmodelcube_file
                    obs_modelcube['ra'] = ra
                    obs_modelcube['dec'] =  dec
                    obs_modelcube['rad'] = fovradius 
                    obs_modelcube['tmin'] = tmin
                    obs_modelcube['tmax'] = tmax
                    obs_modelcube['ebinalg'] = 'LOG'
                    obs_modelcube['emin'] = emin
                    obs_modelcube['emax'] = emax
                    obs_modelcube['enumbins'] = int((log10(emax/emin) * 10)) 
        # =============================================================================
        #             obs_modelcube['ebinalg'] = 'FILE'
        #             obs_modelcube['ebinfile'] = ebinfile
        # =============================================================================
                    obs_modelcube['edisp'] = True
                    obs_modelcube['usepnt'] = True 
                    obs_modelcube['nxpix'] = int(obscube['nxpix'].value())
                    obs_modelcube['nypix'] = int(obscube['nxpix'].value())
                    obs_modelcube['binsz'] = float(obscube['binsz'].value()) 
                    obs_modelcube['chatter'] = 4
                    
                    #%%
                    print(obs_modelcube)
                    
                    #%%
                    
                    obs_modelcube.logFileOpen()
                    obs_modelcube.execute()
                    logfile.write('ctmodel:' + str(obs_modelcube.telapse()) + 'seconds \n')
                    obs_modelcube.logFileClose()
                    
                    #%%
                    
        
                    
                    residuals = cscripts.csresspec()
                    residuals['outfile'] = wd+residuals_file #residuals between observed counts and counts inferred from flux model
                    residuals['inmodel'] = wd+obsmodel_file
                    residuals['modcube'] = wd+obsmodelcube_file
                    residuals['inobs'] =  wd+obscube_file 
                    residuals['expcube'] = wd+expcube_file
                    residuals['psfcube'] = wd+psfcube_file
                    residuals['bkgcube'] = wd+bkgcube_file
                    residuals['edispcube'] = wd+edispcube_file
                    residuals['edisp'] = True
                    residuals['caldb'] = caldb
                    residuals['irf'] = irf
                    residuals['ebinalg'] = 'LOG'
                    residuals['emin'] = emin
                    residuals['emax'] = emax
                    residuals['enumbins'] = int((log10(emax/emin) * 10)) 
        # =============================================================================
        #             residuals['ebinalg'] = 'FILE'
        #             residuals['ebinfile'] = ebinfile
        # =============================================================================
                    residuals['components'] = True
                    residuals['statistic'] = 'DEFAULT' 
                    residuals['chatter'] = 4
                    residuals['algorithm'] = 'SUB' #subtract to get residuals
                    
                    #%%
                    
                    print(residuals)
                    
                    #%%
                    residuals.logFileOpen()
                    residuals.execute()
                    logfile.write('csresspec:' + str(residuals.telapse()) + 'seconds \n')
                    residuals.logFileClose()
                    
                    #%%
                    plot_residuals(wd+residuals_file,'residuals_binned.pdf')
                    
                    #%%
                    logfile.close()







