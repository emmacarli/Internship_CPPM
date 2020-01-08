#Author: Emma Carli 
#import xml.etree.ElementTree as ET

#%%


#calibration database
caldb_gammalib = gammalib.GCaldb('cta', caldb_str)

#original IRF
irf_gammalib   = gammalib.GCTAResponseIrf(irf_str, caldb_gammalib)

bracketed_irf_gammalib = irf_gammalib.copy() #create a copy container
#and load components of the bracketed irf into it
bracketed_irf_gammalib.load_aeff('$CALDB/data/cta/' + caldb_str + '/bcf/' + irf_str + '/' + bracketed_irf_filename) 
bracketed_irf_gammalib.load_psf('$CALDB/data/cta/' + caldb_str + '/bcf/' + irf_str + '/' + bracketed_irf_filename) 
bracketed_irf_gammalib.load_background('$CALDB/data/cta/' + caldb_str + '/bcf/' + irf_str + '/' + bracketed_irf_filename) 
bracketed_irf_gammalib.load_edisp('$CALDB/data/cta/' + caldb_str + '/bcf/' + irf_str + '/' + bracketed_irf_filename) 



#%%


#another way -- unfinished: 
# bracketed_irf_xml = ET.parse('bracketed_irf_xml.xml')
# root = bracketed_irf_xml.getroot()

# for parameter in root.iter('parameter'):
#     if parameter.attrib['name'] == 'Calibration':
#         parameter.attrib['database'] = caldb_str
#         parameter.attrib['response'] = bracketed_irf_name #that didnt work -> takes you to folder
#     else:
#         parameter.attrib['file'] = '$CALDB/data/cta/'+caldb_str+'/bcf/'+irf_str+'/'+bracketed_irf_filename
#     print(parameter.attrib)

#bracketed_irf_xml.write('bracketed_irf_xml.xml')
#bracketed_irf_xml = gammalib.GXml('bracketed_irf_xml.xml')
#bracketed_irf_gammalib.read(gammalib.GXml('bracketed_irf_xml.xml').element('observation_list'))


# Plot the whole IRF (original and bracketed)
