'''
Created on Aug 10, 2017

@author: stevepark
'''
import re
from lxml import etree
from metadata.Common import Common

class ReportAction():
    
    common = Common()
    
    def removeParameter(self, root, fieldname, log):
        for param in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.PARAMETER, namespaces=Common.JRXML_NAMESPACE):
            if param.get(Common.NAME).find(fieldname) >= 0:
                log.debug('removing parameter: ' + param.get(Common.NAME))
                param.getparent().remove(param)
    
    def removeFieldFromFieldList(self, root, fieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.JRXML_NAMESPACE):
            if field.get(Common.NAME).find(fieldname) >= 0 and field.get(Common.NAME).find(fieldname + '__' + Common.DISCRIMINATOR) == -1:
                log.debug('removing field: ' + field.get(Common.NAME))
                field.getparent().remove(field)
                
    def removeQueryFieldFromReportQuery(self, root, fieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.QUERY_FIELD):
            if field.get(Common.ID).find(fieldname) >= 0:
                log.debug('removing field from query: ' + field.get(Common.ID))
                field.getparent().remove(field)
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'queryFilterString'):
            filterString = field.text 
            if filterString.find(fieldname) >= 0:
                # Break up the filter into parts separated by AND and OR
                filterList = re.split('AND |OR ', filterString)
                for clause in filterList:
                    if clause.find(fieldname) >= 0:
                        filterString = filterString.replace(clause, '')
                        # Fix this kludgy mess
                        filterString = filterString.replace('AND AND', 'AND')
                        filterString = filterString.replace('AND OR', 'OR')
                        filterString = filterString.replace('OR AND', 'AND')
                        filterString = filterString.replace('OR OR', 'OR')
                        filterString = filterString.strip()
                        if filterString.startswith('AND') or filterString.endswith('AND'):
                            filterString = filterString.replace('AND','').strip()
                        elif filterString.startswith('OR') or filterString.endswith('OR'):
                            filterString = filterString.replace('OR','').strip()
                        log.debug('modified query filter string: ' + filterString)
                        field.text = filterString
                if filterString is None or filterString == '':
                    field.getparent().remove(field)
                    
    def reinsertQueryIntoReport(self, root, query_str):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.QUERY_STRING, namespaces=Common.JRXML_NAMESPACE):
            field.text = etree.CDATA(query_str)
        return query_str
    
    def removeDetailFieldFromTable(self, root, fieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:textFieldExpression', namespaces=Common.JRXML_NAMESPACE):
            if field.text.find(fieldname) >= 0:
                log.debug('removing detail field: ' + field.text)
                ggparentfield = field.getparent().getparent().getparent()
                # subtract field width from parent
                field_width_str = ggparentfield.get(Common.WIDTH)
                if field_width_str != None:
                    # This report was created from an Ad Hoc view
                    field_width = int(field_width_str)
                    gggparentfield = ggparentfield.getparent()
                    gggparentfield.attrib[Common.WIDTH] = str(int(gggparentfield.get(Common.WIDTH)) - field_width)
                    gggparentfield.remove(ggparentfield)
                    # Fix the width in the reportElement in the header
                    for reportGroupField in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:reportElement', namespaces=Common.JRXML_NAMESPACE):
                        reportGroupGGParent = reportGroupField.getparent().getparent().getparent()
                        if reportGroupGGParent.tag.find('groupHeader') >= 0:
                            reportGroupField.attrib[Common.WIDTH] = gggparentfield.get(Common.WIDTH)
                else:
                    # This is a static report created using Jaspersoft Studio
                    parent = field.getparent()
                    parent.getparent().remove(parent)
                    
    def removeFieldFromGroup(self, root, fieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.GROUP, namespaces=Common.JRXML_NAMESPACE):
            if field.get(Common.NAME).find(fieldname) >= 0:
                log.debug('removing group: ' + field.get(Common.NAME))
                field.getparent().remove(field)
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.CGROUPHEADER, namespaces=Common.JRXML_COMPONENTS_NAMESPACE):
            if field.get(Common.GROUPNAME).find(fieldname) >= 0:
                log.debug('removing column group: ' + field.get(Common.GROUPNAME))
                field.getparent().remove(field)
                
    def insertDummyRowGroup(self, root, log):
        # Inserting dummy row group
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:crosstabDataset', namespaces=Common.JRXML_NAMESPACE):
            parent = field.getparent()
            parser = etree.XMLParser(strip_cdata=False)
            dummy_row_group_xml = etree.fromstring(Common.DUMMY_ROW_GROUP, parser)
            log.debug('inserting dummy row group at position: ' + str(parent.index(field) + 1))
            parent.insert(parent.index(field)+1, dummy_row_group_xml)
        # Removing crosstab header node
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:crosstabHeader', namespaces=Common.JRXML_NAMESPACE):
            log.debug('removing crosstabHeader node')
            field.getparent().remove(field)
                
    def removeRowGroupFromCrosstab(self, root, fieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.ROWGROUP, namespaces=Common.JRXML_NAMESPACE):
            if field.get(Common.NAME).find(fieldname) >= 0:
                log.debug('removing row group: ' + field.get(Common.NAME))
                field.getparent().remove(field)
                # fix row group count
                for param in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:crosstabParameter[@name="CrosstabRowGroupsCount"]', namespaces=Common.JRXML_NAMESPACE):
                    rowGroupText = param[Common.STATE_FILE_NODE_INDEX].text
                    rowGroupCount = int(rowGroupText[rowGroupText.find('(') + 1:rowGroupText.find(')')]) - 1
                    if rowGroupCount == 0:
                        self.insertDummyRowGroup(root=root, log=log)
                    else:
                        param[Common.STATE_FILE_NODE_INDEX].text = etree.CDATA('new Integer(' + str(rowGroupCount) + ')')
                    
    def removeColumnGroupFromCrosstab(self, root, fieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.COLUMNGROUP, namespaces=Common.JRXML_NAMESPACE):
            if field.get(Common.NAME).find(fieldname) >= 0:
                log.debug('removing column group: ' + field.get(Common.NAME))
                field.getparent().remove(field)
                # fix row group count
                for param in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:crosstabParameter[@name="CrosstabColumnGroupsCount"]', namespaces=Common.JRXML_NAMESPACE):
                    rowGroupText = param[Common.STATE_FILE_NODE_INDEX].text
                    rowGroupCount = int(rowGroupText[rowGroupText.find('(') + 1:rowGroupText.find(')')]) - 1
                    param[Common.STATE_FILE_NODE_INDEX].text = etree.CDATA('new Integer(' + str(rowGroupCount) + ')')
    
    def removeFieldFromJRXML(self, root, fieldname, log):
        self.removeParameter(root=root, fieldname=fieldname, log=log)
        self.removeFieldFromFieldList(root=root, fieldname=fieldname, log=log)
        self.removeDetailFieldFromTable(root=root, fieldname=fieldname, log=log)
        self.removeFieldFromGroup(root=root, fieldname=fieldname, log=log)
        self.removeRowGroupFromCrosstab(root=root, fieldname=fieldname, log=log)
        self.removeColumnGroupFromCrosstab(root=root, fieldname=fieldname, log=log)
                
    def removeFieldFromJRXMLFile(self, jrxml_filename, fieldname, log):
        if jrxml_filename.find(Common.PROPERTIES_EXT) == -1:
            log.debug('Preparing to remove field(s) from JRXML file: ' + jrxml_filename[jrxml_filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
            with open(jrxml_filename) as h:
                report_xml = h.read()
            report_tuple = self.common.removeDeclarationNode(xml_string=report_xml)
            report_xml = report_tuple[1]
            parser = etree.XMLParser(strip_cdata=False)
            # remove queryString node that contains an extra XML declaration to avoid syntax error
            try:
                begin_index = report_xml.index('<' + Common.QUERY + '>')
            except ValueError:
                log.debug('Report does not contain a domain query.  Skipping...')
                begin_index = -1
            if begin_index > 0:
                end_index = report_xml.find(']]>', begin_index)
                report_xml_outer = report_xml[0:begin_index] + report_xml[end_index:len(report_xml)]
                report_xml_inner = report_xml[begin_index:end_index]
                report_root = etree.fromstring(report_xml_outer, parser)
                self.removeFieldFromJRXML(root=report_root, fieldname=fieldname, log=log)
                query_root = etree.fromstring(report_xml_inner)
                self.removeQueryFieldFromReportQuery(root=query_root, fieldname=fieldname, log=log)
                # re-insert domain query back into topic
                query_bytea = etree.tostring(query_root, pretty_print=True, encoding='UTF-8')
                query_str = "".join(map(chr, query_bytea))
                self.reinsertQueryIntoReport(root=report_root, query_str=query_str)
            else:
                report_root = etree.fromstring(report_xml, parser)
                self.removeFieldFromJRXML(root=report_root, fieldname=fieldname, log=log)
            report_bytea = etree.tostring(report_root, pretty_print=True, encoding='UTF-8')
            report_xml = "".join(map(chr, report_bytea))
            # re-insert original XML declaration
            report_xml = report_tuple[0] + report_xml
            with open(jrxml_filename, 'w') as h:
                h.write(report_xml)
        
    def removeFieldFromState(self, root, fieldname, log):
        # if the field is a measure
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.MEASURE):
            if field.get(Common.FIELD_NAME) != None and field.get(Common.FIELD_NAME).find(fieldname) >= 0:
                log.debug('removing measure: ' + field.get(Common.FIELD_NAME))
                field.getparent().remove(field)
        # if the field is a dimension
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.QUERY_DIMENSION):
            if field.get(Common.FIELD_NAME) != None and field.get(Common.FIELD_NAME).find(fieldname) >= 0:
                log.debug('removing dimension: ' + field.get(Common.FIELD_NAME))
                field.getparent().remove(field)
        # if the field is a subfilter
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.EXPRESSION_STRING):
            if field.text.find(fieldname) >= 0:
                parent = field.getparent()
                log.debug('removing subfilter: ' + parent.get(Common.ID))
                parent.getparent().remove(parent)
                
    def removeFieldFromStateFile(self, state_filename, fieldname, log):
        if state_filename is not None and state_filename.find(Common.PROPERTIES_EXT) == -1:
            log.debug('Preparing to remove field(s) from state file: ' + state_filename[state_filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
            with open(state_filename) as h:
                try:
                    state_xml = h.read()
                except UnicodeDecodeError:
                    log.debug('Ignoring non-text file: ' + state_filename)
                    return
            state_tuple = self.common.removeDeclarationNode(xml_string=state_xml)
            state_root = etree.fromstring(state_tuple[1])
            self.removeFieldFromState(root=state_root, fieldname=fieldname, log=log)
            state_bytea = etree.tostring(state_root, pretty_print=True, encoding='UTF-8')
            state_xml = "".join(map(chr, state_bytea))
            # re-insert original XML declaration
            state_xml = state_tuple[0] + state_xml
            with open(state_filename, 'w') as h:
                h.write(state_xml)
                    
    def removeField(self, state_filename, jrxml_filename, fieldname, log):
        if isinstance(fieldname, list):
            for singular in fieldname:
                self.removeFieldFromStateFile(state_filename=state_filename, fieldname=singular, log=log)
                self.removeFieldFromJRXMLFile(jrxml_filename=jrxml_filename, fieldname=singular, log=log)
        else:
            self.removeFieldFromStateFile(state_filename=state_filename, fieldname=fieldname, log=log)
            self.removeFieldFromJRXMLFile(jrxml_filename=jrxml_filename, fieldname=fieldname, log=log)
        
    def removeInputControlFromMetadataFiles(self, root, fieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + 'queryValueColumn'):
            if field.text.find(fieldname) >= 0:
                parent = field.getparent()
                log.debug('removing input control: ' + parent[Common.ID_NODE_INDEX].text)
                parent.getparent().remove(parent)
            
    def removeInputControlFromMetadata(self, metadata_filename, fieldname, log):
        log.debug('Checking metadata file for input controls to remove: ' + metadata_filename[metadata_filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
        with open(metadata_filename) as h:
            metadata_xml = h.read()
        metadata_tuple = self.common.removeDeclarationNode(xml_string=metadata_xml)
        metadata_root = etree.fromstring(metadata_tuple[1])
        self.removeInputControlFromMetadataFiles(root=metadata_root, fieldname=fieldname, log=log)
        metadata_bytea = etree.tostring(metadata_root, pretty_print=True, encoding='UTF-8')
        metadata_xml = "".join(map(chr, metadata_bytea))
        # re-insert original XML declaration
        metadata_xml = metadata_tuple[0] + metadata_xml
        if metadata_xml.endswith('\n'):
            metadata_xml = metadata_xml[0:len(metadata_xml) - 1]
        with open(metadata_filename, 'w') as h:
            h.write(metadata_xml)