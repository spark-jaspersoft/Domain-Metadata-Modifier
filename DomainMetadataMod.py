'''
Created on Nov 28, 2017

@author: stevepark
'''
import sys
from metadata.Common import Common
from metadata.FileFinder import FileFinder
from metadata.DomainMetadataModHelper import DomainMetadataModHelper

def main():
    domainMetadataModHelper = DomainMetadataModHelper()
    log = domainMetadataModHelper.processInputs(sys.argv)
    domainMetadataModHelper.connectToServer(log=log)
    domainMetadataModHelper.downloadExport(log=log)
    fileFinder = FileFinder()
    fileFinder.walk(folderpath=domainMetadataModHelper.folderpath, domain_id=domainMetadataModHelper.domain_id, 
                    fieldname=domainMetadataModHelper.fieldname, newfieldname=domainMetadataModHelper.newfieldname, 
                    is_rename=domainMetadataModHelper.is_rename, log=log)
    domainMetadataModHelper.uploadImport(log=log)

if __name__ == '__main__':
    main()