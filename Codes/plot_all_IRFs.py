#Author: Emma Carli 
# =============================================================================
# This code plots all the IRFs available
# =============================================================================

from IPython import get_ipython
get_ipython().magic('reset -sf') 

import os
import gammalib
from emma_plotting.show_irf import plot_irf 



for caldb in ['prod2', 'prod3b-v1', 'prod3b-v2']:
    caldb_gammalib = gammalib.GCaldb('cta', caldb)
    irfs = os.listdir('/cta/carli/anaconda3/share/caldb/data/cta/'+caldb+'/bcf')        
    for irf in irfs:
            irf_gammalib   = gammalib.GCTAResponseIrf(irf, caldb_gammalib)
            plot_irf(irf=irf_gammalib, plotfile=caldb+'_'+irf+'.pdf')


            