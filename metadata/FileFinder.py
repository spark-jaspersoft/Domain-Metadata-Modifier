'''
Created on Sep 26, 2017

@author: stevepark
'''
import os
from lxml import etree
from metadata.Common import Common
from metadata.DomainAction import DomainAction
from metadata.AdhocAction import AdhocAction
from metadata.ReportAction import ReportAction

class FileFinder():
    
    common = Common()
    domainAction = DomainAction()
    adhocAction = AdhocAction()
    reportAction = ReportAction()
    domain_id = None
    resources_folder = None
    adhoc_topic_files_list = []
    adhoc_view_files_list = []
    report_list = []
    
    def findDomainSchemaFile(self, root):
        for child in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE):
            folderPath = child[Common.STATE_FILE_NODE_INDEX].text
            if folderPath is None:
                folderPath = ''
            return self.resources_folder + folderPath  + Common.REPO_PATH_SEPARATOR + child.get(Common.DATA_FILE)
        
    def findDomainSchema(self, metadata_filename):
        with open(metadata_filename) as h:
            metadata_xml = h.read()
        metadata_tuple = self.common.removeDeclarationNode(xml_string=metadata_xml)
        metadata_root = etree.fromstring(metadata_tuple[1])
        return self.findDomainSchemaFile(root=metadata_root)
            
    def findAdhocTopicFiles(self, root, adhoc_topic_id):
        jrxmlfile = None
        statefile = None
        adhoc_topic_id_node = root[Common.ID_NODE_INDEX]
        if adhoc_topic_id_node.text.find(adhoc_topic_id) >= 0 and self.checkDatasource(root=root):
            for child in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'mainReport' + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE):
                folderPath = child[Common.STATE_FILE_NODE_INDEX].text
                if folderPath is None:
                    folderPath = ''
                jrxmlfile = self.resources_folder + folderPath + Common.REPO_PATH_SEPARATOR + child.get(Common.DATA_FILE)
            for child in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'resource' + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE):
                folderPath = child[Common.STATE_FILE_NODE_INDEX].text
                if folderPath is None:
                    folderPath = ''
                statefile = self.resources_folder + folderPath + Common.REPO_PATH_SEPARATOR + child.get(Common.DATA_FILE)
        if statefile is not None and jrxmlfile is not None:
            self.adhoc_topic_files_list.append([statefile, jrxmlfile])
                
    def findAdhocTopic(self, metadata_filename, adhoc_topic_id):
        with open(metadata_filename) as h:
            metadata_xml = h.read()
        metadata_tuple = self.common.removeDeclarationNode(xml_string=metadata_xml)
        metadata_root = etree.fromstring(metadata_tuple[1])
        self.findAdhocTopicFiles(root=metadata_root, adhoc_topic_id=adhoc_topic_id)
            
    def findAdhocViewFiles(self, root, adhoc_view_id):
        jrxmlfile = None
        statefile = None
        adhoc_view_id_node = root[Common.ID_NODE_INDEX]
        if adhoc_view_id_node.text.find(adhoc_view_id) >= 0 and self.checkDatasource(root):
            for child in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'resource' + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE):
                secondchild = child[Common.ID_NODE_INDEX]
                folderPath = child[Common.STATE_FILE_NODE_INDEX].text
                if folderPath is None:
                    folderPath = ''
                if secondchild.text.find('stateXML') >= 0:
                    statefile = self.resources_folder + folderPath + Common.REPO_PATH_SEPARATOR + child.get(Common.DATA_FILE)
                else:
                    jrxmlfile = self.resources_folder + folderPath + Common.REPO_PATH_SEPARATOR + child.get(Common.DATA_FILE)
        if statefile is not None and jrxmlfile is not None:
            self.adhoc_view_files_list.append([statefile, jrxmlfile])
            return True
        else:
            return False
                
    def findAdhocView(self, metadata_filename, adhoc_view_id):
        with open(metadata_filename) as h:
            metadata_xml = h.read()
        metadata_tuple = self.common.removeDeclarationNode(xml_string=metadata_xml)
        metadata_root = etree.fromstring(metadata_tuple[1])
        return self.findAdhocViewFiles(root=metadata_root, adhoc_view_id=adhoc_view_id)
        
    def findReportFiles(self, root, report_id):
        jrxmlfile = None
        statefile = None
        report_id_node = root[Common.ID_NODE_INDEX]
        if report_id_node.text.find(report_id) >= 0 and self.checkDatasource(root):
            for child in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'mainReport' + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE):
                folderPath = child[Common.STATE_FILE_NODE_INDEX].text
                if folderPath is None:
                    folderPath = ''
                jrxmlfile = self.resources_folder + folderPath + Common.REPO_PATH_SEPARATOR + child.get(Common.DATA_FILE)
            for child in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'resource' + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE):
                if child.get(Common.DATA_FILE) == Common.STATE_DATAFILE:
                    folderPath = child[Common.STATE_FILE_NODE_INDEX].text
                    if folderPath is None:
                        folderPath = ''
                    statefile = self.resources_folder + folderPath + Common.REPO_PATH_SEPARATOR + child.get(Common.DATA_FILE)
                    break
        if statefile is not None and jrxmlfile is not None:
            self.report_list.append([statefile, jrxmlfile])
            return False
        elif jrxmlfile is not None:
            # static report with domain data source
            self.report_list.append([None, jrxmlfile])
            return True
        else:
            return False
                
    def findReport(self, metadata_filename, report_id):
        with open(metadata_filename) as h:
            metadata_xml = h.read()
        metadata_tuple = self.common.removeDeclarationNode(xml_string=metadata_xml)
        metadata_root = etree.fromstring(metadata_tuple[1])
        return self.findReportFiles(root=metadata_root, report_id=report_id)
    
    def checkRootNodeTag(self, root_tag):
        if root_tag.find(Common.DOMAIN_METADATA_TAG) >= 0 or root_tag.find(Common.ADHOC_TOPIC_TAG) >= 0 or root_tag.find(Common.ADHOC_VIEW_TAG) >= 0 or root_tag.find(Common.REPORT_TAG) >= 0:
            return True
        else:
            return False
    
    def checkDatasource(self, root):
        if root.tag.find(self.common.DOMAIN_METADATA_TAG) >= 0:
            if root[Common.ID_NODE_INDEX].text.find(self.domain_id) >= 0:
                return True
            else:
                return False
        else:
            # check parent
            for child in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.DATA_SOURCE + Common.REPO_PATH_SEPARATOR + 'uri'):
                with open(self.resources_folder + child.text + '.xml') as h:
                    metadata_xml = h.read()
                metadata_tuple = self.common.removeDeclarationNode(metadata_xml)
                metadata_root = etree.fromstring(metadata_tuple[1])
                return self.checkDatasource(metadata_root)
    
    def walk(self, folderpath, domain_id, fieldname, newfieldname, is_rename, log):
        self.domain_id = domain_id
        for root, _, files in os.walk(folderpath, topdown=True):
            for filename in files:
                if filename.find(Common.PROPERTIES_EXT) == -1:
                    xml_file = None
                    filepath = os.path.join(root, filename)
                    log.info('Inspecting file: ' + filepath)
                    if self.resources_folder is None and str(root).find(Common.RESOURCES_FOLDER) > -1:
                        self.resources_folder = str(root)[:str(root).find(Common.RESOURCES_FOLDER) + len(Common.RESOURCES_FOLDER)]
                    with open(filepath) as h:
                        try:
                            xml_file = h.read()
                        except UnicodeDecodeError:
                            log.debug('Ignoring non-text file: ' + filepath)
                    if xml_file != None:
                        xml_tuple = self.common.removeDeclarationNode(xml_string=xml_file)
                        root_node = None
                        try:
                            root_node = etree.fromstring(xml_tuple[1])
                        except etree.XMLSyntaxError:
                            log.debug('Ignoring non-XML file: ' + filepath)
                        if root_node != None:
                            root_tag = root_node.tag
                            if self.checkRootNodeTag(root_tag):
                                id_value = root_node[Common.ID_NODE_INDEX]
                                id_name = id_value.text
                                if root_tag.find(Common.DOMAIN_METADATA_TAG) >= 0 and id_name == domain_id:
                                    log.info('Processing domain: ' + id_name)
                                    domain_schemafile = self.findDomainSchema(metadata_filename=filepath)
                                    if domain_schemafile is not None:
                                        self.domainAction.removeOrRenameField(filename=domain_schemafile, fieldname=fieldname, newfieldname=newfieldname, is_rename=is_rename, log=log)
                                elif root_tag.find(Common.ADHOC_TOPIC_TAG) >= 0:
                                    log.info('Processing Ad Hoc Topic: ' + id_name)
                                    self.findAdhocTopic(metadata_filename=filepath, adhoc_topic_id=id_name)
                                elif root_tag.find(Common.ADHOC_VIEW_TAG) >= 0:
                                    log.info('Processing Ad Hoc View: ' + id_name)
                                    if self.findAdhocView(metadata_filename=filepath, adhoc_view_id=id_name):
                                        self.adhocAction.removeInputControlFromMetadata(metadata_filename=filepath, fieldname=fieldname, log=log)
                                elif root_tag.find(Common.REPORT_TAG) >= 0:
                                    log.info('Processing Report: ' + id_name)
                                    if self.findReport(metadata_filename=filepath, report_id=id_name):
                                        # check metadata for input control(s) if report is static
                                        self.reportAction.removeInputControlFromMetadata(metadata_filename=filepath, fieldname=fieldname, log=log)
        self.processFiles(fieldname, log)
                                    
    def processFiles(self, fieldname, log):
        for files in self.adhoc_topic_files_list:
            self.adhocAction.removeField(files[0], files[1], fieldname, log)
        for files in self.adhoc_view_files_list:
            self.adhocAction.removeField(files[0], files[1], fieldname, log)
        for files in self.report_list:
            self.reportAction.removeField(files[0], files[1], fieldname, log)