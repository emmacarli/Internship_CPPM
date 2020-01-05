#Author: Emma Carli 
# =============================================================================
# This code produces 68% and 85% C.L. asymmetrical errors for the spectral fit
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 



import ctools
import os

#%%
#General simulation parameters

caldb = 'prod3b-v2' #calibration database
orig_irf = 'South_z40_50h' 
offset = 0.5 #deg

#%%
#source1b-specific parameters

ra = 83.6331 + offset 
dec = 22.0145

#%%

#Input files
obscube_file = 'obs_cube.fits'
expcube_file = "exposure_cube.fits"
psfcube_file = "PSF_cube.fits"
bkgcube_file = "background_cube.fits"
edispcube_file = "edisp_cube.fits"
obsmodel_file = 'obsmodel_binned.xml' #fitted model from observations #Don't forget to fix background parameters!!



def asymmetrical_errors(cutoff, flux, function):
    """
    Calculate asymmetrical errors for a fit
    
    Parameters
    ----------
    cutoff : str
        '1','2', or '3' for 50, 100, or 200 TeV respectively
    flux : str
        'a', 'b', 'c', 'd' for 20, 40, 60, 80 mCrab respectively
    function : str
        'none', 'constant', 'step', 'gradient', bracketing of IRF
    """
    
    
    if function == 'none': #if there is no bracketing
        function_signs = ['']
        function_components = ['']
    else:
        function_signs = ['minus','plus']
        function_components = ['AEff', 'EDisp' ]

    for sign in function_signs:
        for component in function_components:


            if function =='none':
                irf=orig_irf
            else:
                irf = sign +  '_' +function + '_' + component + '_' + orig_irf
            
            
            
                                
            #%%
            name = 'source'+cutoff+flux
            
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+ irf+'/'+name+'/'
            os.chdir(wd)
        
            logfile = open('asymmetrical_errors.txt', 'w')                       
            #%%
            
            cl68 = ctools.cterror() #generate 68% C.L.
            cl68['inobs'] = wd+obscube_file
            cl68['inmodel'] = wd+obsmodel_file #Don't forget to fix background parameters!!
            cl68['srcname'] = name 
            cl68['expcube'] = wd+expcube_file
            cl68['psfcube'] = wd+psfcube_file
            cl68['bkgcube'] = wd+bkgcube_file
            cl68['edispcube'] = wd+edispcube_file
            cl68['outmodel'] = '' #ASYMMETRICAL errors are in log file only. in this is mean of asymmetrical errors, in which we are not interested
            cl68["caldb"] = caldb
            cl68["confidence"] = 0.68
            cl68["irf"] = irf
            cl68['statistic'] = 'DEFAULT' 
            cl68['chatter'] = 4
            cl68["edisp"] = True 
            cl68['logfile'] = 'cterror68.log'
            
            #%%
            
            print(cl68)
            
            #%%
            
            cl68.logFileOpen()
            cl68.execute()
            logfile.write('cterror, 68:' + str(cl68.telapse()) + 'seconds \n')
            cl68.logFileClose()
            
            #%%
            
            cl95 = ctools.cterror() 
            cl95['inobs'] = wd+obscube_file
            cl95['inmodel'] = wd+obsmodel_file
            cl95['srcname'] = name 
            cl95['expcube'] = wd+expcube_file
            cl95['psfcube'] = wd+psfcube_file
            cl95['bkgcube'] = wd+bkgcube_file
            cl95['edispcube'] = wd+edispcube_file
            cl95['outmodel'] = ''
            cl95["caldb"] = caldb
            cl95["confidence"] = 0.95
            cl95["irf"] = irf
            cl95['statistic'] = 'DEFAULT' 
            cl95['chatter'] = 4
            cl95["edisp"] = True
            cl95['logfile'] = 'cterror95.log'
            
            #%%
            
            print(cl95)
            
            #%%
            
            cl95.logFileOpen()
            cl95.execute()
            logfile.write('cterror, 95:' + str(cl95.telapse()) + 'seconds \n')
            cl95.logFileClose()
      

#takes a long time so use several marcta2 CPUs
from multiprocessing import Process
process1 = Process(target=asymmetrical_errors, args=('3','a','constant'))
process2 = Process(target=asymmetrical_errors, args=('3','b','constant'))
process3 = Process(target=asymmetrical_errors, args=('3','c','constant'))
process4 = Process(target=asymmetrical_errors, args=('3','d','constant'))

process1.start()
process2.start()
process3.start()
process4.start()
process1.join()
process2.join()
process3.join()
process4.join()






