#Author: Emma Carli 
# =============================================================================
# This code modifies CTA IRFs' Effective Areas with several bracketing functions, and saves+plots them
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 


#%%
#import general packages

import matplotlib.pyplot as plt
import yaml
import os

#%%
#imports

#import external scientific tools
from caldb_scaler import *
import gammalib

#import my plotting functions 
from emma_plotting.show_irf_fixedoffset import plot_irf_fixedoffset 
from emma_plotting.show_irf import plot_irf 


#%%

#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'
#other plotting params
plt.rcParams['axes.grid'] = True


#%%
# Set general parameters
caldb_name = 'prod3b-v2' #calibration database
irf_name = 'South_z40_50h' 
bracketed_irf_filename =  'irf_file.fits' 


#%%

#Get calibration database and original IRF into gammalib format
caldb_gammalib = gammalib.GCaldb('cta', caldb_name)        
irf_gammalib   = gammalib.GCTAResponseIrf(irf_name, caldb_gammalib)

#set minimal energy
emin = 0.1 #TeV 


#set emax as smallest max energy in IRF 
emaxs = []
emaxs.append(irf_gammalib.background().table().axis_hi(irf_gammalib.background().table().axis('ENERG'),irf_gammalib.background().table().axis_bins(irf_gammalib.background().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.aeff().table().axis_hi(irf_gammalib.aeff().table().axis('ENERG'), irf_gammalib.aeff().table().axis_bins(irf_gammalib.aeff().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.psf().table().axis_hi(irf_gammalib.psf().table().axis('ENERG'), irf_gammalib.psf().table().axis_bins(irf_gammalib.psf().table().axis('ENERG'))-1))
emaxs.append(irf_gammalib.edisp().table().axis_hi(irf_gammalib.edisp().table().axis('ENERG'), irf_gammalib.edisp().table().axis_bins(irf_gammalib.edisp().table().axis('ENERG'))-1))
emax = min(emaxs) #in TeV

#%%
#Plot the original IRF

fig0 = plt.figure(figsize=(16,8))
plot_irf_fixedoffset(irf=irf_gammalib, fig=fig0, offset=0.5)
fig0.savefig(irf_name+'_fixedoffset.pdf' )
plt.close()

#%%
#Bracket the IRF with different functions and plot the results on the same graph for comparison

config = yaml.safe_load(open('config.yaml'))

fig1 = plt.figure(figsize=(16,8)) #on this will be plotted all the bracketed IRFs at fixed offset

for function in ['constant', 'step', 'gradient']:
    for sign, sign_str in zip([-1,1],['minus','plus']):
        for component in ['AEff']: #add here 'EDisp' if do IRF EDisp bracketing
        
            bracketed_irf_name = sign_str + '_'+ function +'_'+ component + '_' + irf_name #the folder in which the new IRF will be!
            bracketed_irf_path = os.environ['CALDB']+ '/data/cta/' + caldb_name + '/bcf/' + bracketed_irf_name
            os.mkdir(bracketed_irf_path)
            
            #%%
            
            if function == 'constant':
                scale_aeff = 1+sign*0.05 
                scale_edisp = 1+sign*0.06
            else:
                scale_aeff = sign*0.05
                scale_edisp = sign*0.06
            
            #%%
                
            config['general']['caldb'] = caldb_name
            config['general']['irf'] = irf_name
            config['general']['output_irf_file_name'] = bracketed_irf_filename
            config['general']['output_irf_name'] = bracketed_irf_name
            
            #%%
            
            if component == 'AEff':
                config['aeff']['energy_scaling']['err_func_type'] = function
                config['aeff']['energy_scaling'][function]['scale'] = scale_aeff
                
                
                config['edisp']['energy_scaling']['err_func_type'] = 'constant'
                config['edisp']['energy_scaling']['constant']['scale'] = 1 #ensure no EDisp bracketing
                
                
                if function == 'gradient':
                    config['aeff']['energy_scaling'][function]['range_min'] = emin
                    config['aeff']['energy_scaling'][function]['range_max'] = emax

                    
                if function == 'step':
                    config['aeff']['energy_scaling'][function]['transition_widths'] = [0.11, 0.06] #as per paper
                    config['aeff']['energy_scaling'][function]['transition_pos'] = [0.15, 5]
                     
            #%%
            
            #angle dependent scaling - not used so ensure no scaling (constant 1)
            config['psf']['angular_scaling']['err_func_type'] = 'constant'
            config['psf']['angular_scaling']['constant']['scale'] = 1.0
            config['aeff']['angular_scaling']['err_func_type'] = 'constant'
            config['aeff']['angular_scaling']['constant']['scale'] = 1.0
            config['edisp']['angular_scaling']['err_func_type'] = 'constant'
            config['edisp']['angular_scaling']['constant']['scale'] = 1.0
            
            #make sure psf is not scaled either
            config['psf']['energy_scaling']['err_func_type'] = 'constant'
            config['psf']['energy_scaling']['constant']['scale'] = 1.0
        
            #%%
            
            irf_ievgen = CalDB(caldb_name, irf_name, verbose=True) #get the original IRF into Ievgen's format
            
            #%%
            
            irf_ievgen.scale_irf(config) #scale/bracket the IRF

            
            #%%
            #Get bracketed IRF into gammalib format and plot it

            #unsure why I have to use this long path, I would just use the folder name before, as for the original IRF.. 
            bracketed_irf_gammalib = gammalib.GCTAResponseIrf('data/cta/' + caldb_name + '/bcf/' + bracketed_irf_name + '/' + bracketed_irf_filename , caldb_gammalib)         
            plot_irf(irf=bracketed_irf_gammalib, plotfile=bracketed_irf_name+'.pdf')
            plot_irf_fixedoffset(irf=bracketed_irf_gammalib, fig=fig1, offset=0.5, label=sign_str+' '+function+' '+component )
            
            #%%
            # Plot bracketed irf scale maps

            if component == 'AEff':
                fig2 = plt.figure()
                irf_ievgen.plot_aeff_scale_map()
                plt.savefig(sign_str + function  + '_aeff_scalemap.jpg')
                plt.close()


fig1.suptitle('Bracketed IRFs comparison at 0.5deg offset')
fig1.legend()
fig1.savefig('bracketed_IRFs_fixedoffset.pdf' )
plt.close()