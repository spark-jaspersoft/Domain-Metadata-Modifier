'''
Created on Aug 10, 2017

@author: stevepark
'''
from lxml import etree
from metadata.Common import Common

class AdhocAction():
    
    sort_order_map = None
    common = Common()
    
    def removeRenameFieldInJRXMLFile(self, filename, fieldname, newfieldname, log):
        log.debug('Preparing to remove field(s) from JRXML file: ' + filename[filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
        with open(filename, 'r', encoding='utf-8') as h:
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
            self.removeRenameFieldInJRXML(root=report_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
            # remove the <?xml ?> declaration from the beginning because lxml fromstring() can't handle the encoding
            query_tag_index = report_xml_inner.find('<' + Common.QUERY)
            report_xml_inner = report_xml_inner[query_tag_index:]
            query_root = etree.fromstring(report_xml_inner)
            self.removeRenameQueryFieldInAdhocQuery(root=query_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
            # re-insert domain query back into topic
            query_bytea = etree.tostring(query_root, pretty_print=True, encoding='UTF-8')
            query_str = "".join(map(chr, query_bytea))
            self.reinsertQueryIntoMainBody(root=report_root, query_str=query_str)
        else:
            report_root = etree.fromstring(report_xml, parser)
            self.removeRenameFieldInJRXML(root=report_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        report_bytea = etree.tostring(report_root, pretty_print=True, encoding='UTF-8')
        report_xml = "".join(map(chr, report_bytea))
        # re-insert original XML declaration
        report_xml = report_tuple[0] + report_xml
        with open(filename, 'w', encoding='utf-8') as h:
            h.write(report_xml)
    
    def removeRenameFieldInJRXML(self, root, fieldname, newfieldname, log):
        semantic_tree_sort_order = None
        semantic_tree_sort_order_set = False
        semantic_tree_sort_order_deleted = False
        # if field is a parameter
        for param in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.PARAMETER, namespaces=Common.JRXML_NAMESPACE):
            nameValue = param.get(Common.NAME)
            if nameValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming parameter ' + nameValue + ' to ' + nameValue.replace(fieldname, newfieldname))
                    param.attrib[Common.NAME] = nameValue.replace(fieldname, newfieldname)
                else:
                    log.debug('removing parameter: ' + nameValue)
                    param.getparent().remove(param)
        # remove or rename field
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.JRXML_NAMESPACE):
            nameValue = field.get(Common.NAME)
            if semantic_tree_sort_order_set == False and semantic_tree_sort_order_deleted == False:
                for child in field:
                    if child.get(Common.NAME) == Common.SORT_ORDER:
                        if newfieldname is not None and newfieldname != '_' and child.text is not None and child.text.find(fieldname) >= 0:
                            child.text = etree.CDATA(child.text.replace(fieldname, newfieldname))
                            semantic_tree_sort_order_set = True
                        else:
                            semantic_tree_sort_order = self.fixSortOrder(fieldname=fieldname, semantic_tree_sort_order=child.text)
                    # Fix any other property values where the fieldname appears
                    elif newfieldname is not None and newfieldname != '_' and child.get(Common.VALUE) is not None and child.get(Common.VALUE).find(fieldname) >= 0:
                        childValue = child.get(Common.VALUE)
                        log.debug('changing value for property ' + child.get(Common.NAME) + ' from ' + childValue + ' to ' + childValue.replace(fieldname, newfieldname))
                        child.attrib[Common.VALUE] = childValue.replace(fieldname, newfieldname)
            if nameValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming field ' + nameValue + ' to ' + nameValue.replace(fieldname, newfieldname))
                    field.attrib[Common.NAME] = nameValue.replace(fieldname, newfieldname)
                else:
                    log.debug('removing field: ' + nameValue)
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
                        elif newfieldname is None or newfieldname == '_':
                            field_key = field.get(Common.NAME)
                            if field_key.find('.') >= 0:
                                field_key = field_key[field_key.rfind('.')+1:]
                            child.attrib[Common.VALUE] = self.sort_order_map['"' + field_key + '"']
            # Fix any other property values where the fieldname appears
            if newfieldname is not None and newfieldname != '_':
                for child in field:
                    if (child.get(Common.NAME) != Common.SORT_ORDER) and child.get(Common.VALUE) is not None and child.get(Common.VALUE).find(fieldname) >= 0:
                        childValue = child.get(Common.VALUE)
                        log.debug('changing value for property ' + child.get(Common.NAME) + ' from ' + childValue + ' to ' + childValue.replace(fieldname, newfieldname))
                        child.attrib[Common.VALUE] = childValue.replace(fieldname, newfieldname)
                                
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
                
    def removeRenameQueryFieldInAdhocQuery(self, root, fieldname, newfieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:' +  Common.QUERY_FIELD, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            idValue = field.get(Common.ID)
            if idValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming field ' + idValue + ' to ' + idValue.replace(fieldname, newfieldname))
                    field.attrib[Common.ID] = idValue.replace(fieldname, newfieldname)
                else:
                    log.debug('removing field: ' + idValue)
                    field.getparent().remove(field)
                    
    def reinsertQueryIntoMainBody(self, root, query_str):
        query_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + query_str
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.QUERY_STRING, namespaces=Common.JRXML_NAMESPACE):
            field.text = etree.CDATA(query_str)
        return query_str
                    
    def removeRenameFieldInStateFile(self, filename, fieldname, newfieldname, log):
            log.debug('Preparing to remove field(s) from state file: ' + filename[filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
            with open(filename, 'r', encoding='utf-8') as h:
                state_xml = h.read()
            state_tuple = self.common.removeDeclarationNode(xml_string=state_xml)
            state_root = etree.fromstring(state_tuple[1])
            self.removeRenameFieldInState(root=state_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
            state_bytea = etree.tostring(state_root, pretty_print=True, encoding='UTF-8')
            state_xml = "".join(map(chr, state_bytea))
            # re-insert original XML declaration
            state_xml = state_tuple[0] + state_xml
            if state_xml.endswith('\n'):
                state_xml = state_xml[0:len(state_xml) - 1]
            with open(filename, 'w', encoding='utf-8') as h:
                h.write(state_xml)
        
    def removeRenameFieldInState(self, root, fieldname, newfieldname, log):
        # if the field is a measure
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.MEASURE):
            fieldnameValue = field.get(Common.FIELD_NAME)
            nameValue = field.get(Common.NAME)
            if fieldnameValue != None and fieldnameValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming measure from ' + fieldnameValue + ' to ' + fieldnameValue.replace(fieldname, newfieldname))
                    field.attrib[Common.FIELD_NAME] = fieldnameValue.replace(fieldname, newfieldname)
                    if nameValue.find(fieldname) >= 0:
                        log.debug('renaming measure name attribute from ' + nameValue + ' to ' + nameValue.replace(fieldname, newfieldname))
                        field.attrib[Common.NAME] = nameValue.replace(fieldname, newfieldname)
                    # check and rename the labelOverride property if necessary
                    labelOverride = field.get(Common.LABEL_OVERRIDE)
                    if labelOverride is not None and labelOverride.find(fieldname) >= 0:
                        log.debug('changing labelOverride property from ' + labelOverride + ' to ' + labelOverride.replace(fieldname, newfieldname))
                        field.attrib[Common.LABEL_OVERRIDE] = labelOverride.replace(fieldname, newfieldname)
                else:
                    log.debug('removing measure: ' + fieldnameValue)
                    field.getparent().remove(field)
        # if the field is a dimension
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.QUERY_DIMENSION):
            fieldnameValue = field.get(Common.FIELD_NAME)
            nameValue = field.get(Common.NAME)
            if fieldnameValue != None and fieldnameValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming dimension from ' + fieldnameValue + ' to ' + fieldnameValue.replace(fieldname, newfieldname))
                    field.attrib[Common.FIELD_NAME] = fieldnameValue.replace(fieldname, newfieldname)
                    if nameValue.find(fieldname) >= 0:
                        log.debug('renaming measure name attribute from ' + nameValue + ' to ' + nameValue.replace(fieldname, newfieldname))
                        field.attrib[Common.NAME] = nameValue.replace(fieldname, newfieldname)
                else:
                    log.debug('removing dimension: ' + fieldnameValue)
                    field.getparent().remove(field)
        # if the field is a field
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            idValue = field.get(Common.ID)
            if idValue != None and idValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming field ' + idValue + ' to ' + idValue.replace(fieldname, newfieldname))
                    field.attrib[Common.ID] = idValue.replace(fieldname, newfieldname)
                else:
                    log.debug('removing field: ' + idValue)
                    field.getparent().remove(field)
        # if the field is used in a parameter
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.EXPRESSION_STRING):
            if field.text.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    textValue = field.text
                    log.debug('changing expressionString ' + textValue + ' to ' + textValue.replace(fieldname, newfieldname))
                    field.text = textValue.replace(fieldname, newfieldname)
                    sibling = field.getnext()
                    if sibling is not None and sibling.text.find(fieldname) >= 0:
                        textField2 = sibling.text
                        log.debug('changing parameterizedExpressionString ' + textField2 + ' to ' + textField2.replace(fieldname, newfieldname))
                        sibling.text = textField2.replace(fieldname, newfieldname)
                else:
                    parent = field.getparent()
                    log.debug('removing parameter: ' + parent.get(Common.ID))
                    parent.getparent().remove(parent)
        # fix visible levels
        self.common.fixVisibleLevels(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
                    
    def removeRenameField(self, state_filename, jrxml_filename, fieldname, newfieldname, log):
        if isinstance(fieldname, list):
            if newfieldname is None:
                newfieldname = []
                for _ in fieldname:
                    newfieldname.append('_')
            for s1, s2 in zip(fieldname, newfieldname):
                self.removeRenameFieldInJRXMLFile(jrxml_filename, s1, s2, log)
                self.removeRenameFieldInStateFile(state_filename, s1, s2, log)
        else:
            self.removeRenameFieldInJRXMLFile(jrxml_filename, fieldname, newfieldname, log)
            self.removeRenameFieldInStateFile(state_filename, fieldname, newfieldname, log)
        
    def removeRenameInputControlInMetadata(self, root, fieldname, newfieldname, log):
        # remove entire IC or fix query value and visible columns
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + 'queryValueColumn'):
            textValue = field.text
            if textValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('Changing queryValueColumn ' + textValue + ' to ' + textValue.replace(fieldname, newfieldname))
                    field.text = textValue.replace(fieldname, newfieldname)
                    sibling = field.getprevious()
                    if sibling is not None and sibling.text.find(fieldname) >= 0:
                        textValue2 = sibling.text
                        log.debug('Changing queryVisibleColumn ' + textValue2 + ' to ' + textValue2.replace(fieldname, newfieldname))
                        sibling.text = textValue2.replace(fieldname, newfieldname)
                else:
                    parent = field.getparent()
                    log.debug('removing input control: ' + parent[Common.ID_NODE_INDEX].text)
                    parent.getparent().remove(parent)
        # fix query
        if newfieldname is not None and newfieldname != '_':
            for query in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + 'queryString'):
                queryText = query.text
                if queryText.find(fieldname) >= 0:
                    log.debug('Changing query to ' + queryText.replace(fieldname, newfieldname))
                    query.text = queryText.replace(fieldname, newfieldname)
            # fix name
            for name in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + Common.NAME):
                nameText = name.text
                if nameText.find(fieldname) >= 0:
                    log.debug('Changing name ' + nameText + ' to ' + nameText.replace(fieldname, newfieldname))
                    name.text = nameText.replace(fieldname, newfieldname)
            # fix folder
            for folder in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + 'folder'):
                folderText = folder.text
                if folderText is not None and folderText.find(fieldname) >= 0:
                    log.debug('Changing folder ' + folderText + ' to ' + folderText.replace(fieldname, newfieldname))
                    folder.text = folderText.replace(fieldname, newfieldname) 
            
    def removeRenameInputControlInMetadataFile(self, metadata_filename, fieldname, newfieldname, log):
        log.debug('Checking metadata file for input controls to remove: ' + metadata_filename[metadata_filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
        with open(metadata_filename) as h:
            metadata_xml = h.read()
        metadata_tuple = self.common.removeDeclarationNode(xml_string=metadata_xml)
        metadata_xml = metadata_tuple[1]
        metadata_root = etree.fromstring(metadata_xml)    
        if isinstance(fieldname, list):
            if newfieldname is None:
                newfieldname = []
                for _ in fieldname:
                    newfieldname.append('_')
            for s1, s2 in zip(fieldname, newfieldname):
                self.removeRenameInputControlInMetadata(root=metadata_root, fieldname=s1, newfieldname=s2, log=log)
        else:
            self.removeRenameInputControlInMetadata(root=metadata_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        metadata_bytea = etree.tostring(metadata_root, pretty_print=True, encoding='UTF-8')
        metadata_xml = "".join(map(chr, metadata_bytea))
        # re-insert original XML declaration
        metadata_xml = metadata_tuple[0] + metadata_xml
        if metadata_xml.endswith('\n'):
            metadata_xml = metadata_xml[0:len(metadata_xml) - 1]
        with open(metadata_filename, 'w') as h:
            h.write(metadata_xml)
            