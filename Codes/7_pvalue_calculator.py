#Author: Emma Carli 
# =============================================================================
# This code calculates p-values for the fits performed with each bracketed IRF
# =============================================================================


from IPython import get_ipython
get_ipython().magic('reset -f') 


#%%

from scipy import stats
from astropy.io import fits

#%%
orig_irf = 'South_z40_50h' 

#%%

logfile = open('pvalues.txt', 'w')
logfile2 = open('chisquares.txt', 'w' )

#%%
#Loop over bracketing functions and models
for cutoff in ['1','2','3']: #50, 100, 200 TeV
    
    for flux in ['a', 'b', 'c', 'd']: #20, 40, 60, 80 mCrab
        
        for function in ['none', 'constant', 'step', 'gradient']:
            
            if function == 'none': #no bracketing
                function_signs = ['']
                function_components = ['']
            else:
                function_signs = ['minus','plus']
                function_components = ['AEff', 'EDisp']
        
            for sign in function_signs:
                for component in function_components:
        
        
                    if function =='none':
                        irf=orig_irf
                    else:
                        irf = sign +  '_' +function + '_' + component + '_' + orig_irf
                        
                        
                    name = 'source'+cutoff+flux
                    
                    wd = '/cta/carli/CPPM_Internship/Simulations_and_Analyses/'+ irf+'/'+name+'/'                    
                    fits_file = fits.open( wd + '/residuals_binned.fits')
                    fits_data = fits_file[1].data
                   
        
                    operator = fits_data['Residuals']**2
                    operator = list(filter((0.0).__ne__, operator))
                    denominator = fits_data['Counts'] #other calculation method, comment out either
                    denominator = list(filter((0.0).__ne__, denominator))
                    mychi2 = sum([ (op_i / den_i) for op_i, den_i in zip(operator, denominator) ])
                    freeparams = 5
                    dof = len(operator) - freeparams - 1 #degrees of freedom
                    logfile2.write(irf+' '+name+' chi2 '+str(mychi2)+' dof '+str(dof)+' \n')

                    pval = 1 - stats.chi2.cdf(mychi2, dof) 
                    logfile.write(irf+','+name+','+ str(pval) + '\n')
                      
logfile.close()
logfile2.close()
