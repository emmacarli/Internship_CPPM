#Author: Emma Carli 
# =============================================================================
# This code fixes all parameters except source cutoff before asymmetrical error computation
# =============================================================================


from IPython import get_ipython
get_ipython().magic('reset -f') 


#%%
import xml.etree.ElementTree as ET
import os
orig_irf = 'South_z40_50h' 




for cutoff in ['1','2','3']: #50, 100, 200 TeV
    
    for flux in ['a', 'b', 'c', 'd']: #20, 40, 60, 80 mCrab
        
        for function in ['none', 'constant', 'step', 'gradient']:
            
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

                    xmlfile = ET.parse(wd+'obsmodel_binned.xml')
                    root = xmlfile.getroot()
                    root[0][0][0].attrib['free']='0'
                    root[0][0][1].attrib['free']='0'
                    root[1][0][0].attrib['free']='0'
                    root[1][0][1].attrib['free']='0'
                    xmlfile.write(wd+'obsmodel_binned.xml')


