'''
Created on Nov 28, 2017

@author: stevepark
'''
import sys
from metadata.FileFinder import FileFinder
from metadata.DomainMetadataModHelper import DomainMetadataModHelper

def main():
    domainMetadataModHelper = DomainMetadataModHelper()
    log = domainMetadataModHelper.processInputs(sys.argv)
    domainMetadataModHelper.connectToServer(log=log)
    domainMetadataModHelper.downloadExport(log=log)
    fileFinder = FileFinder()
    fileFinder.walk(dmmHelper=domainMetadataModHelper, log=log)
    domainMetadataModHelper.uploadImport(log=log)

if __name__ == '__main__':
    main()