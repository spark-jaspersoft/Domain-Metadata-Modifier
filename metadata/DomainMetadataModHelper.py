'''
Created on Feb 15, 2018

@author: stevepark
'''

import os
import requests
import time
import tempfile
import zipfile
import shutil
from lxml import etree
from metadata.Common import Common

class DomainMetadataModHelper():

    common = Common()
    server_URL = None
    server_pass = None
    session = None
    folderpath = None
    domain_id = None
    fieldname = None
    newfieldname = None
    newdbcolname = None
    
    def connectToServer(self, log):
        self.session = requests.post(self.server_URL + Common.LOGIN_PATH, data={Common.J_USERNAME:'superuser', Common.J_PASSWORD:self.server_pass})
        if self.session.status_code == 401:
            log.error('Error logging into JasperReports Server: Unauthorized')
            quit()
        elif self.session.status_code == 404:
            log.error('Error logging into JasperReports Server: no server found at location ' + self.server_URL)
            quit()
        elif self.session.status_code == 302:
            log.error('Error logging into JasperReports Server: License expired')
            quit()
        elif self.session.status_code != 200:
            self.session.raise_for_status()
            quit()
        
    def downloadExport(self, log):
        log.debug('starting repository export...')
        descriptor = { 'parameters':['everything']}
        startResult = requests.post(self.server_URL + Common.EXPORT_START_PATH, json=descriptor, cookies=self.session.cookies)
        if startResult.status_code == 200:
            startResultText = startResult.text
            startResultTuple = self.common.removeDeclarationNode(startResultText)
            startResultXml = etree.fromstring(startResultTuple[1])
            for node in startResultXml.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.ID):
                exportProcessID = node.text
                break
            if exportProcessID != None:
                log.debug('export process id: ' + exportProcessID)
                phase = Common.PHASE_INPROGRESS_STATUS
                while phase != Common.PHASE_READY_STATUS:
                    log.debug('waiting 5 seconds...')
                    time.sleep(Common.FIVE_SECONDS) 
                    pollingResult = requests.get(self.server_URL + Common.REPO_PATH_SEPARATOR + Common.REST_V2 + 
                                   Common.REPO_PATH_SEPARATOR + Common.EXPORT + 
                                   Common.REPO_PATH_SEPARATOR + exportProcessID + 
                                   Common.REPO_PATH_SEPARATOR + Common.STATE, cookies=self.session.cookies)
                    if pollingResult.status_code == 200:
                        pollingResultText = pollingResult.text
                        pollingResultTuple = self.common.removeDeclarationNode(pollingResultText)
                        pollingResultXml = etree.fromstring(pollingResultTuple[1])
                        for node in pollingResultXml.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.PHASE):
                            phase = node.text
                            break
                    else:
                        pollingResult.raise_for_status()
                        quit()
                    if phase == Common.PHASE_FAILURE_STATUS:
                        for node in pollingResultXml.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.MESSAGE):
                            message = node.text
                            break
                        log.error('Error while exporting the repository:  ' + message)
                        quit()
                if phase == Common.PHASE_READY_STATUS:
                    _, tmpfile = tempfile.mkstemp()
                    tmpfilefile = tmpfile[tmpfile.rfind(Common.REPO_PATH_SEPARATOR) + 1:]
                    # check to see if we're on Windows
                    if tmpfilefile.find(Common.WINDOWS_PATH_SEPARATOR) >= 0:
                        tmpfilefile = tmpfilefile[tmpfilefile.rfind(Common.WINDOWS_PATH_SEPARATOR) + 1:]
                    log.debug('export finished, starting download to ' + tmpfile)
                    downloadRestCall = (self.server_URL + Common.REPO_PATH_SEPARATOR + Common.REST_V2 +
                                    Common.REPO_PATH_SEPARATOR + Common.EXPORT +
                                    Common.REPO_PATH_SEPARATOR + exportProcessID + 
                                    Common.REPO_PATH_SEPARATOR + tmpfilefile)
                    log.debug('download rest API call: ' + downloadRestCall)
                    savingResult = requests.get(downloadRestCall, cookies=self.session.cookies)
                    if savingResult.status_code != 200:
                        savingResult.raise_for_status()
                        quit()
                    else:
                        with open(tmpfile, 'wb') as h:
                            h.write(savingResult.content)
                        tmpdir = tempfile.mkdtemp()
                        zipRef = zipfile.ZipFile(tmpfile, 'r')
                        log.debug('extracting zip archive ' + tmpfile + ' to ' + tmpdir)
                        zipRef.extractall(tmpdir)
                        zipRef.close()
                        log.debug('finished extracting, removing zip archive')
                        try:
                            os.remove(tmpfile)
                        except OSError as err:
                            log.error('unable to remove zip archive: {0}'.format(err))
                        log.debug('setting folderpath: ' + tmpdir)
                        self.folderpath = tmpdir
        
    def uploadImport(self, log):
        _, tmpfile = tempfile.mkstemp()
        log.debug('creating import archive at: ' + tmpfile)
        shutil.make_archive(tmpfile, 'zip', self.folderpath)
        log.debug('importing zip file into repository...')
        params =  {'update':'true','skipUserUpdate':'true','includeAccessEvents':'false','includeAuditEvents':'false','includeMonitoringEvents':'false','includeServerSetting':'false'}
        if tmpfile.rfind('/') == -1:
            tmpfilename = tmpfile[tmpfile.rfind('\\')+1:]
        else:
            tmpfilename = tmpfile[tmpfile.rfind('/')+1:]
        headers = {'Content-Disposition':'form-data; name="File"; filename="' + tmpfilename + '"','Content-Type':'application/zip','X-Remote-Domain':'true'}
        with open(tmpfile + Common.ZIP_EXT, 'rb') as h:
            data = h.read()
        startResult = requests.post(self.server_URL + Common.IMPORT_START_PATH, params=params, headers=headers, data=data, cookies=self.session.cookies)
        if startResult.status_code == 200:
            startResultText = startResult.text
            startResultTuple = self.common.removeDeclarationNode(startResultText)
            startResultXml = etree.fromstring(startResultTuple[1])
            for node in startResultXml.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.ID):
                importProcessID = node.text
                break
            if importProcessID != None:
                log.debug('import process id: ' + importProcessID)
                phase = Common.PHASE_INPROGRESS_STATUS
                while phase != Common.PHASE_READY_STATUS:
                    log.debug('waiting 5 seconds...')
                    time.sleep(Common.FIVE_SECONDS) 
                    pollingResult = requests.get(self.server_URL + Common.REPO_PATH_SEPARATOR + Common.REST_V2 + 
                                   Common.REPO_PATH_SEPARATOR + Common.IMPORT + 
                                   Common.REPO_PATH_SEPARATOR + importProcessID + 
                                   Common.REPO_PATH_SEPARATOR + Common.STATE, cookies=self.session.cookies)
                    if pollingResult.status_code == 200:
                        pollingResultText = pollingResult.text
                        pollingResultTuple = self.common.removeDeclarationNode(pollingResultText)
                        pollingResultXml = etree.fromstring(pollingResultTuple[1])
                        for node in pollingResultXml.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.PHASE):
                            phase = node.text
                            break
                    else:
                        pollingResult.raise_for_status()
                        quit()
                    if phase == Common.PHASE_FAILURE_STATUS:
                        for node in pollingResultXml.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.MESSAGE):
                            message = node.text
                            break
                        log.error('Error while exporting the repository:  ' + message)
                        quit()
                if phase == Common.PHASE_READY_STATUS:
                    log.debug('import complete, cleaning up temporary files...')
                    shutil.rmtree(self.folderpath)
                    os.remove(tmpfile)
                    os.remove(tmpfile + Common.ZIP_EXT)
        
    def processInputs(self, inputs):
        log = self.common.configureLogging()
        log.debug('inputs provided: ' + str(inputs))
        if len(inputs) < 5:
            raise ValueError(Common.NOT_ENOUGH_VALUES)
        if inputs[1].find('http') == -1:
            raise ValueError(Common.PROTOCOL_MISSING)
            quit()
        else:
            self.server_URL = inputs[1]
            self.server_pass = inputs[2]
            self.domain_id = inputs[3]
            self.fieldname = inputs[4]
            if self.fieldname.find(',') > 0:
                self.fieldname = self.fieldname.split(',')
            if len(inputs) >= 6:
                self.newfieldname = inputs[5]
                if self.newfieldname.find(',') > 0:
                    self.newfieldname = self.newfieldname.split(',')
                    if not isinstance(self.fieldname, list):
                        raise ValueError('Both the old and new field name parameters must be comma-separated lists')
                    if len(self.newfieldname) != len(self.fieldname):
                        raise ValueError('both the old and new field name parameter lists must be the same length')
            if len(inputs) >= 7:
                self.newdbcolname = inputs[6]
                if self.newdbcolname.find(',') > 0:
                    self.newdbcolname = self.newdbcolname.split(',')
                    if not isinstance(self.fieldname, list) or not isinstance(self.newfieldname, list):
                        raise ValueError('Old and new field name and database column name parameters must be comma-separated lists')
                    if len(self.newdbcolname) != len(self.fieldname) or len(self.newdbcolname) != len(self.newfieldname):
                        raise ValueError('Old and new field name and database column name parameter lists must be the same length')
            else:
                # use the new field name items as the database column items
                self.newdbcolname = self.newfieldname
        return log
        