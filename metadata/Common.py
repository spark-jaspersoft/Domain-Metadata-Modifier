'''
Created on Aug 30, 2017

@author: stevepark
'''
import logging
import sys

class Common():
    
    RELATIVE_PATH = '.'
    REPO_PATH_SEPARATOR = '/'
    DATA_SOURCE = 'dataSource'
    MEASURE = 'measure'
    ID = 'id'
    FIELD = 'n:field'
    PARAMETER = 'n:parameter'
    NAME = 'name'
    VALUE = 'value'
    WIDTH = 'width'
    QUERY_DIMENSION = 'queryDimension'
    QUERY_STRING = "n:queryString"
    QUERY_FIELD = 'queryField'
    QUERY = 'query'
    QUERY_FIELDS = 'queryFields'
    FIELD_NAME = 'fieldName'
    DISCRIMINATOR = 'DISCRIMINATOR'
    DISTANCE_TO_TAG_START = 16
    DISTANCE_TO_TAG_END = 4
    SORT_ORDER = 'semantic.tree.sort.order'
    ITEM = 'n:item'
    JOIN_STRING = 'n:joinString'
    JRXML_NAMESPACE = {'n':'http://jasperreports.sourceforge.net/jasperreports'}
    JRXML_COMPONENTS_NAMESPACE = {'c':'http://jasperreports.sourceforge.net/jasperreports/components'}
    DOMAIN_QUERY_NAMESPACE = {'n':'http://www.jaspersoft.com/2007/SL/XMLSchema'}
    ID_NODE_INDEX = 1
    STATE_FILE_NODE_INDEX = 0
    PHASE = 'phase'
    PHASE_INPROGRESS_STATUS = 'inprogress'
    PHASE_READY_STATUS = 'finished'
    PHASE_FAILURE_STATUS = 'failed'
    LOCAL_RESOURCE = 'localResource'
    DATA_FILE = 'dataFile'
    EXPRESSION_STRING = 'expressionString'
    DOMAIN_METADATA_TAG = 'semanticLayerDataSource'
    ADHOC_TOPIC_TAG = 'dataDefinerUnit'
    ADHOC_VIEW_TAG = 'adhocDataView'
    REPORT_TAG = 'reportUnit'
    RESOURCES_FOLDER = 'resources'
    PROPERTIES_EXT = '.properties'
    STATE_DATAFILE = 'stateXML.data'
    GROUP = 'n:group'
    ROWGROUP = 'n:rowGroup'
    COLUMNGROUP = 'n:columnGroup'
    CGROUPHEADER = 'c:groupHeader'
    GROUPNAME = 'groupName'
    FIELD_DB_NAME = 'fieldDBName'
    DUMMY_ROW_GROUP = '''                <rowGroup name="DUMMY" width="0" headerPosition="Stretch">
                    <bucket class="java.lang.Comparable">
                        <bucketExpression><![CDATA[null]]></bucketExpression>
                    </bucket>
                    <crosstabRowHeader>
                        <cellContents/>
                    </crosstabRowHeader>
                    <crosstabTotalRowHeader>
                        <cellContents/>
                    </crosstabTotalRowHeader>
                </rowGroup>
                 '''
    NOT_ENOUGH_VALUES = 'DomainMetadataMod requires at least 4 command line parameters: <server_url> <superuser_password> <domain_id> <field_id> with optional <new_db_fieldname>'
    PROTOCOL_MISSING = 'Server URL must begin with either http or https'
    JASPERSERVER_PRO = 'jasperserver-pro'
    REST_V2 = 'rest_v2'
    J_USERNAME = 'j_username'
    J_PASSWORD = 'j_password'
    LOGIN_PATH = REPO_PATH_SEPARATOR + 'rest' + REPO_PATH_SEPARATOR + 'login'
    EXPORT = 'export'
    EXPORT_START_PATH = REPO_PATH_SEPARATOR + REST_V2 + REPO_PATH_SEPARATOR + EXPORT + REPO_PATH_SEPARATOR
    IMPORT = 'import'
    IMPORT_START_PATH = REPO_PATH_SEPARATOR + REST_V2 + REPO_PATH_SEPARATOR + IMPORT
    STATE = 'state'
    MESSAGE = 'message'
    FIVE_SECONDS = 5
    ZIP_EXT = '.zip'
    
    def removeDeclarationNode(self, xml_string):
        dec_end = xml_string.find('?>')
        if dec_end > -1:
            dec_end = dec_end + 3
            # Check to see if there's no newline character
            if xml_string[dec_end - 1] == '<':
                dec_end = dec_end - 1
            xml_declaration = xml_string[0:dec_end]
        else:
            dec_end = 0
            xml_declaration = ''
        xml_string = xml_string[dec_end:]
        return (xml_declaration, xml_string)
            
    def configureLogging(self):
        log = logging.getLogger(__name__)
        log.setLevel(logging.DEBUG)
        logFormatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
        fileHandler = logging.FileHandler('metadataReplace.log')
        fileHandler.setFormatter(logFormatter)
        log.addHandler(fileHandler)
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logFormatter)
        log.addHandler(consoleHandler)
        return log