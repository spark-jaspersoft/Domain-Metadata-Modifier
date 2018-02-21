'''
Created on Aug 10, 2017

@author: stevepark
'''
from lxml import etree
from metadata.Common import Common

class AdhocAction():
    
    sort_order_map = None
    common = Common()
    
    def removeFieldFromJRXMLFile(self, filename, fieldname, log):
        log.debug('Preparing to remove field(s) from JRXML file: ' + filename[filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
        with open(filename) as h:
            report_xml = h.read()
        report_tuple = self.common.removeDeclarationNode(xml_string=report_xml)
        report_xml = report_tuple[1]
        parser = etree.XMLParser(strip_cdata=False)
        # remove queryString node that contains an extra XML declaration to avoid syntax error
        try:
            begin_index = report_xml.index('<?xml', 2)
        except ValueError:
            log.debug('Report does not contain a domain query.  Skipping...')
            begin_index = -1
        if begin_index > 0:
            end_index = report_xml.find(']]>', begin_index)
            report_xml_outer = report_xml[0:begin_index] + report_xml[end_index:len(report_xml)]
            report_xml_inner = report_xml[begin_index:end_index]
            report_root = etree.fromstring(report_xml_outer, parser)
            self.removeFieldFromJRXML(root=report_root, fieldname=fieldname, log=log)
            # remove the <?xml ?> declaration from the beginning because lxml fromstring() can't handle the encoding
            jasperreport_tag_index = report_xml_inner.find('<' + Common.QUERY)
            report_xml_inner = report_xml_inner[jasperreport_tag_index:]
            query_root = etree.fromstring(report_xml_inner)
            self.removeQueryFieldFromAdhocQuery(root=query_root, fieldname=fieldname, log=log)
            # re-insert domain query back into topic
            query_bytea = etree.tostring(query_root, pretty_print=True, encoding='UTF-8')
            query_str = "".join(map(chr, query_bytea))
            self.reinsertQueryIntoAdhocTopic(root=report_root, query_str=query_str)
        else:
            report_root = etree.fromstring(report_xml, parser)
            self.removeFieldFromJRXML(root=report_root, fieldname=fieldname, log=log)
        report_bytea = etree.tostring(report_root, pretty_print=True, encoding='UTF-8')
        report_xml = "".join(map(chr, report_bytea))
        # re-insert original XML declaration
        report_xml = report_tuple[0] + report_xml
        with open(filename, 'w') as h:
            h.write(report_xml)
    
    def removeFieldFromJRXML(self, root, fieldname, log):
        semantic_tree_sort_order = None
        semantic_tree_sort_order_set = False
        semantic_tree_sort_order_deleted = False
        # remove parameter
        for param in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.PARAMETER, namespaces=Common.JRXML_NAMESPACE):
            if param.get(Common.NAME).find(fieldname) >= 0:
                log.debug('removing parameter: ' + param.get(Common.NAME))
                param.getparent().remove(param)
        # remove field
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.JRXML_NAMESPACE):
            if semantic_tree_sort_order_set == False and semantic_tree_sort_order_deleted == False:
                for child in field:
                    if child.get(Common.NAME) == Common.SORT_ORDER:
                        semantic_tree_sort_order = self.fixSortOrder(fieldname=fieldname, semantic_tree_sort_order=child.text)
            if field.get(Common.NAME).find(fieldname) >= 0:
                log.debug('removing field: ' + field.get(Common.NAME))
                field.getparent().remove(field)
                semantic_tree_sort_order_deleted = True
            else:
                for child in field:
                    if (child.get(Common.NAME) == Common.SORT_ORDER):
                        if semantic_tree_sort_order_set == False:
                            if (child.get(Common.VALUE) != None):
                                del child.attrib[Common.VALUE]
                            if semantic_tree_sort_order != None:
                                child.text = etree.CDATA(semantic_tree_sort_order)
                                semantic_tree_sort_order_set = True
                        else:
                            field_key = field.get(Common.NAME)
                            if field_key.find('.') >= 0:
                                field_key = field_key[field_key.rfind('.')+1:]
                            child.attrib[Common.VALUE] = self.sort_order_map['"' + field_key + '"']
                                
    def fixSortOrder(self, fieldname, semantic_tree_sort_order):
        if semantic_tree_sort_order != None:
            # Strip the curly braces and convert to a map
            semantic_tree_sort_order = semantic_tree_sort_order[semantic_tree_sort_order.find('{')+1:semantic_tree_sort_order.find('}')]
            self.sort_order_map = dict(item.split(':') for item in semantic_tree_sort_order.split(','))
            if '"' + fieldname + '"' in self.sort_order_map.keys():
                del self.sort_order_map['"' + fieldname + '"']
            self.fixSortingValues()
            semantic_tree_sort_order = ','.join('%s:%d' % (k,int(v)) for k,v in self.sort_order_map.items())
            return '{' + semantic_tree_sort_order + '}'
        else:
            return None
                            
    def fixSortingValues(self):
        if self.sort_order_map != None:
            smallest_value = 99999
            for value in self.sort_order_map.values():
                if int(value) < smallest_value:
                    smallest_value = int(value)
            value_diff = smallest_value - 1
            for key in self.sort_order_map.keys():
                self.sort_order_map[key] = str(int(self.sort_order_map[key]) - value_diff)
                
    def removeQueryFieldFromAdhocQuery(self, root, fieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:' +  Common.QUERY_FIELD, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            if field.get(Common.ID).find(fieldname) >= 0:
                log.debug('removing field: ' + field.get(Common.ID))
                field.getparent().remove(field)
                    
    def reinsertQueryIntoAdhocTopic(self, root, query_str):
        query_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + query_str
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.QUERY_STRING, namespaces=Common.JRXML_NAMESPACE):
            field.text = etree.CDATA(query_str)
        return query_str
                    
    def removeFieldFromStateFile(self, filename, fieldname, log):
            log.debug('Preparing to remove field(s) from state file: ' + filename[filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
            with open(filename) as h:
                state_xml = h.read()
            state_tuple = self.common.removeDeclarationNode(xml_string=state_xml)
            state_root = etree.fromstring(state_tuple[1])
            self.removeFieldFromState(root=state_root, fieldname=fieldname, log=log)
            state_bytea = etree.tostring(state_root, pretty_print=True, encoding='UTF-8')
            state_xml = "".join(map(chr, state_bytea))
            # re-insert original XML declaration
            state_xml = state_tuple[0] + state_xml
            if state_xml.endswith('\n'):
                state_xml = state_xml[0:len(state_xml) - 1]
            with open(filename, 'w') as h:
                h.write(state_xml)
        
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
        # if the field is a field
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            if field.get(Common.ID) != None and field.get(Common.ID).find(fieldname) >= 0:
                log.debug('removing field: ' + field.get(Common.ID))
                field.getparent().remove(field)
        # if the field is used in a parameter
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.EXPRESSION_STRING):
            if field.text.find(fieldname) >= 0:
                parent = field.getparent()
                log.debug('removing parameter: ' + parent.get(Common.ID))
                parent.getparent().remove(parent)
                    
    def removeField(self, state_filename, jrxml_filename, fieldname, log):
        if isinstance(fieldname, list):
            for singular in fieldname:
                self.removeFieldFromJRXMLFile(jrxml_filename, singular, log)
                self.removeFieldFromStateFile(state_filename, singular, log)
        else:
            self.removeFieldFromJRXMLFile(jrxml_filename, fieldname, log)
            self.removeFieldFromStateFile(state_filename, fieldname, log)
        
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
        if isinstance(fieldname, list):
            for singular in fieldname:
                self.removeInputControlFromMetadataFiles(root=metadata_root, fieldname=singular, log=log)
        else:
            self.removeInputControlFromMetadataFiles(root=metadata_root, fieldname=fieldname, log=log)
        metadata_bytea = etree.tostring(metadata_root, pretty_print=True, encoding='UTF-8')
        metadata_xml = "".join(map(chr, metadata_bytea))
        # re-insert original XML declaration
        metadata_xml = metadata_tuple[0] + metadata_xml
        if metadata_xml.endswith('\n'):
            metadata_xml = metadata_xml[0:len(metadata_xml) - 1]
        with open(metadata_filename, 'w') as h:
            h.write(metadata_xml)
            