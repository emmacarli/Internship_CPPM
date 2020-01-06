#Author: Emma Carli 
# =============================================================================
# This code makes LaTeX tables from my data 
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -f') 


import xml.etree.ElementTree as ET
import os
import numpy as np
import re


pvalues = np.genfromtxt('pvalues.txt', delimiter=',', dtype=None, encoding='latin1')


logfile = open('tables.txt', 'w')
orig_irf = 'South_z40_50h' 














def data_finder(flux_number,cutoff_number, irf, name):

    wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
    os.chdir(wd)
    xmlfile = ET.parse(wd+'obsmodel_binned.xml')
    root = xmlfile.getroot()
    
    flux_number=float(flux_number)
    cutoff_number=float(cutoff_number)
    
    fit_flux = (float(root[0][0][0].attrib['value'])*float(root[0][0][0].attrib['scale']))/3.8e-20 #convert ph/MeV.cm2.s to mCrab
    fit_flux_error = (float(root[0][0][0].attrib['error'])*float(root[0][0][0].attrib['scale']))/3.8e-20 #convert ph/MeV.cm2.s to mCrab
    fit_flux = round(fit_flux,2)
    fit_flux_error = round(fit_flux_error,2)
    if flux_number>=fit_flux-fit_flux_error and flux_number<=fit_flux+fit_flux_error:
        cellcolor_fit_flux = ''
    else: 
        cellcolor_fit_flux = '/cellcolor{pink}'
        
    fit_flux = str(fit_flux)
    fit_flux_error = str(fit_flux_error)
    
    index = -float(root[0][0][1].attrib['value'])*float(root[0][0][1].attrib['scale'])
    index_error = -float(root[0][0][1].attrib['error'])*float(root[0][0][1].attrib['scale'])
    index =  round(index,3)
    index_error =  round(index_error,3)
    if 2>=index-index_error and 2<=index+index_error:
        cellcolor_index = ''
    else: 
        cellcolor_index = '/cellcolor{pink}'

    index = str(index)
    index_error = str(index_error)
    
    fit_cutoff = (float(root[0][0][2].attrib['value'])*float(root[0][0][2].attrib['scale']))/1e6 #convert MeV into TeV
    fit_cutoff = round(fit_cutoff,1)
    
    try: 
        cl95 = open(wd+'cterror95.log')
        cl95 = cl95.read()
        fit_cutoff_error_minus95 = re.findall('Negative profile error ....: (\d+\.\d+)', cl95)
        fit_cutoff_error_minus95 = float(fit_cutoff_error_minus95[0])/1e6
        fit_cutoff_error_minus95 = round(fit_cutoff_error_minus95,1)
        fit_cutoff_error_plus95 = re.findall('Positive profile error ....: (\d+\.\d+)', cl95)
        fit_cutoff_error_plus95 = float(fit_cutoff_error_plus95[0])/1e6
        fit_cutoff_error_plus95 = round(fit_cutoff_error_plus95,1)
        cl68 = open(wd+'cterror68.log')
        cl68 = cl68.read()
        fit_cutoff_error_minus68 = re.findall('Negative profile error ....: (\d+\.\d+)', cl68)
        fit_cutoff_error_minus68 = float(fit_cutoff_error_minus68[0])/1e6
        fit_cutoff_error_minus68 = round(fit_cutoff_error_minus68,1)
        fit_cutoff_error_minus68 = str(fit_cutoff_error_minus68)    
        fit_cutoff_error_plus68 = re.findall('Positive profile error ....: (\d+\.\d+)', cl68)
        fit_cutoff_error_plus68 = float(fit_cutoff_error_plus68[0])/1e6
        fit_cutoff_error_plus68 = round(fit_cutoff_error_plus68,1)
        fit_cutoff_error_plus68 = str(fit_cutoff_error_plus68)

    except:
        fit_cutoff_error_minus95 =  0
        fit_cutoff_error_plus95 = 0
        fit_cutoff_error_minus68 =  str(0)
        fit_cutoff_error_plus68 = str(0)  
    
    if cutoff_number>=fit_cutoff-fit_cutoff_error_minus95 and cutoff_number<=fit_cutoff+fit_cutoff_error_plus95:
        cellcolor_fit_cutoff = ''
    else: 
        cellcolor_fit_cutoff = '/cellcolor{pink}'
    fit_cutoff_error_plus95 = str(fit_cutoff_error_plus95)
    fit_cutoff_error_minus95 = str(fit_cutoff_error_minus95)
    fit_cutoff =  str(fit_cutoff)

    
    for i in range(len(pvalues)):
        if pvalues[i][0] == irf and pvalues[i][1] == name:
            pvalue = pvalues[i][2]
            pvalue = round(pvalue,5)
            pvalue = str(pvalue)
            
    
    return fit_flux, fit_flux_error, cellcolor_fit_flux, index, index_error, cellcolor_index, fit_cutoff, fit_cutoff_error_minus95, fit_cutoff_error_plus95, fit_cutoff_error_minus68, fit_cutoff_error_plus68, cellcolor_fit_cutoff, pvalue





















for j, cutoff in enumerate(['1','2','3']): #50, 100, 200 TeV
    cutoff_number=str([50,100,200][j])
    for i, flux in enumerate(['a', 'b', 'c', 'd']): #20, 40, 60, 80 mCrab
        
        flux_number=str(20*(i+1))

        name_str= 'Source '+cutoff+flux
        name = 'source'+cutoff+flux
        
        for component, component_str in zip(['AEff', 'EDisp' ], ['Effective Area', 'Energy Dispersion']):
               
        
            function='none'
            irf = orig_irf
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
            os.chdir(wd)
            

            fit_flux, fit_flux_error, cellcolor_fit_flux, index, index_error, cellcolor_index, fit_cutoff, fit_cutoff_error_minus95, fit_cutoff_error_plus95, fit_cutoff_error_minus68, fit_cutoff_error_plus68, cellcolor_fit_cutoff, pvalue = data_finder(flux_number,cutoff_number, irf, name)
            
            
            table_n = """
            /begin{table}[h!]
            /centering
            
                /begin{subtable}{/textwidth}
                /centering
                    {/begin{tabular}{c|c c c}
                         /textit{"""+name_str+'} parameters & '+flux_number+'mCrab prefactor & -2 index & '+cutoff_number+"""TeV cutoff //  
                        Observation parameters & 40h duration & 0.5deg offset & 1.6deg FoV //
                        Binning parameters & /multicolumn{3}{c}{0.02deg spatial resolution /hspace{2pt}  10 bins per energy decade} //
                    /end{tabular}}
                /caption{Input parameters: observation data.}
                /label{"""+name+'_'+component+"""_input}
                /end{subtable}
            
            
            /vspace{2pt}
                /begin{subtable}{/textwidth}
                /centering
                    {/begin{tabular}{|c|c c c|c|} 
                        /hline
                        Bracketing & Prefactor (mCrab) & - Index & Cutoff (TeV) & p-value // [0.5ex] 
                        /hline/hline
                        None &"""+cellcolor_fit_flux +fit_flux+ '$/pm$'+fit_flux_error+    '&'+cellcolor_index+index+'  $/pm$'+index_error+  '&'+cellcolor_fit_cutoff+fit_cutoff+'  $/substack{+'+fit_cutoff_error_plus95+' // -'+fit_cutoff_error_minus95+'}$  $/substack{+'+fit_cutoff_error_plus68+' // -'+fit_cutoff_error_minus68+'}$  & '+pvalue+"""  // 
                        /hline
                        Constant &  &  &  &   // """
            
            
            

            
            function= 'plus_constant'
            irf= function+'_' + component + '_' + orig_irf
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
            os.chdir(wd)
            
            fit_flux, fit_flux_error, cellcolor_fit_flux, index, index_error, cellcolor_index, fit_cutoff, fit_cutoff_error_minus95, fit_cutoff_error_plus95, fit_cutoff_error_minus68, fit_cutoff_error_plus68, cellcolor_fit_cutoff, pvalue = data_finder(flux_number,cutoff_number, irf, name)

            
            table_pc= """
            $/oplus$  &"""+cellcolor_fit_flux +fit_flux+ '$/pm$'+fit_flux_error+    '&'+cellcolor_index+index+'  $/pm$'+index_error+  '&'+cellcolor_fit_cutoff+fit_cutoff+'  $/substack{+'+fit_cutoff_error_plus95+' // -'+fit_cutoff_error_minus95+'}$  $/substack{+'+fit_cutoff_error_plus68+' // -'+fit_cutoff_error_minus68+'}$  & '+pvalue+'  //'  
      
        
            function= 'minus_constant'
            irf= function+'_' + component + '_' + orig_irf
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
            os.chdir(wd)
            
            fit_flux, fit_flux_error, cellcolor_fit_flux, index, index_error, cellcolor_index, fit_cutoff, fit_cutoff_error_minus95, fit_cutoff_error_plus95, fit_cutoff_error_minus68, fit_cutoff_error_plus68, cellcolor_fit_cutoff, pvalue = data_finder(flux_number,cutoff_number, irf, name)

            
            table_mc=  """
            $/circleddash$ & """+cellcolor_fit_flux +fit_flux+ '$/pm$'+fit_flux_error+    '&'+cellcolor_index+index+'  $/pm$'+index_error+  '&'+cellcolor_fit_cutoff+fit_cutoff+'  $/substack{+'+fit_cutoff_error_plus95+' // -'+fit_cutoff_error_minus95+'}$  $/substack{+'+fit_cutoff_error_plus68+' // -'+fit_cutoff_error_minus68+'}$  & '+pvalue+"""  // 
            /hline
            Gradient &  &  &  &   // """
            
            
            function= 'plus_gradient'
            irf= function+'_' + component + '_' + orig_irf
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
            os.chdir(wd)
            
            fit_flux, fit_flux_error, cellcolor_fit_flux, index, index_error, cellcolor_index, fit_cutoff, fit_cutoff_error_minus95, fit_cutoff_error_plus95, fit_cutoff_error_minus68, fit_cutoff_error_plus68, cellcolor_fit_cutoff, pvalue = data_finder(flux_number,cutoff_number, irf, name)

            
            
            table_pg= """
            $/oplus$ &"""+cellcolor_fit_flux +fit_flux+ '$/pm$'+fit_flux_error+    '&'+cellcolor_index+index+'  $/pm$'+index_error+  '&'+cellcolor_fit_cutoff+fit_cutoff+'  $/substack{+'+fit_cutoff_error_plus95+' // -'+fit_cutoff_error_minus95+'}$  $/substack{+'+fit_cutoff_error_plus68+' // -'+fit_cutoff_error_minus68+'}$  & '+pvalue+'  //'
       

            function= 'minus_gradient'
            irf= function+'_' + component + '_' + orig_irf
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
            os.chdir(wd)
            
            
            fit_flux, fit_flux_error, cellcolor_fit_flux, index, index_error, cellcolor_index, fit_cutoff, fit_cutoff_error_minus95, fit_cutoff_error_plus95, fit_cutoff_error_minus68, fit_cutoff_error_plus68, cellcolor_fit_cutoff, pvalue = data_finder(flux_number,cutoff_number, irf, name)

            
            table_mg= """        
            $/circleddash$ &"""+cellcolor_fit_flux +fit_flux+ '$/pm$'+fit_flux_error+    '&'+cellcolor_index+index+'  $/pm$'+index_error+  '&'+cellcolor_fit_cutoff+fit_cutoff+'  $/substack{+'+fit_cutoff_error_plus95+' // -'+fit_cutoff_error_minus95+'}$  $/substack{+'+fit_cutoff_error_plus68+' // -'+fit_cutoff_error_minus68+'}$  & '+pvalue+"""  // 
            /hline
            Step &  &  &  &   //"""

            

            function= 'plus_step'
            irf= function+'_' + component + '_' + orig_irf
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
            os.chdir(wd)
            
            
            fit_flux, fit_flux_error, cellcolor_fit_flux, index, index_error, cellcolor_index, fit_cutoff, fit_cutoff_error_minus95, fit_cutoff_error_plus95, fit_cutoff_error_minus68, fit_cutoff_error_plus68, cellcolor_fit_cutoff, pvalue = data_finder(flux_number,cutoff_number, irf, name)

            
            
            table_ps= """
            $/oplus$  & """+cellcolor_fit_flux +fit_flux+ '$/pm$'+fit_flux_error+    '&'+cellcolor_index+index+'  $/pm$'+index_error+  '&'+cellcolor_fit_cutoff+fit_cutoff+'  $/substack{+'+fit_cutoff_error_plus95+' // -'+fit_cutoff_error_minus95+'}$  $/substack{+'+fit_cutoff_error_plus68+' // -'+fit_cutoff_error_minus68+'}$  & '+pvalue+' //' 


            function= 'minus_step'
            irf= function+'_' + component + '_' + orig_irf
            wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+irf+'/'+name+'/'
            os.chdir(wd)
            
            
            
            fit_flux, fit_flux_error, cellcolor_fit_flux, index, index_error, cellcolor_index, fit_cutoff, fit_cutoff_error_minus95, fit_cutoff_error_plus95, fit_cutoff_error_minus68, fit_cutoff_error_plus68, cellcolor_fit_cutoff, pvalue = data_finder(flux_number,cutoff_number, irf, name)

            
            table_ms= """         
                        $/circleddash$ & """+cellcolor_fit_flux +fit_flux+ '$/pm$'+fit_flux_error+    '&'+cellcolor_index+index+'  $/pm$'+index_error+  '&'+cellcolor_fit_cutoff+fit_cutoff+'  $/substack{+'+fit_cutoff_error_plus95+' // -'+fit_cutoff_error_minus95+'}$  $/substack{+'+fit_cutoff_error_plus68+' // -'+fit_cutoff_error_minus68+'}$  & '+pvalue+"""  // 
                        /hline
                    /end{tabular}}
                /caption{Output parameters: spectral fit. The errors at 95/% and 68/% confidence levels (C.L.) are displayed. The parameters that do not match the source at 95/% C.L. are highlighted.} 
                /label{"""+name+'_'+component+"""_output}
                /end{subtable}
            
            /caption{Parameters for the fitting of observations of /textit{"""+name_str+'}  with differently bracketed '+component_str+""". }
            /label{"""+name+'_'+component+"""_table}
            /end{table}
            
            
            """       

            os.chdir('/cta/carli/CPPM_Internship/Running')
            logfile.write(table_n+table_pc+table_mc+table_pg+table_mg+table_ps+table_ms+'\n')



logfile.close()

#end by replacing all the / by \ and not found cutoffs!
            
    

            
     

            



