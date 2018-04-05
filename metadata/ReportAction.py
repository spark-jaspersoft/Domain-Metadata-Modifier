'''
Created on Aug 10, 2017

@author: stevepark
'''
import re
from lxml import etree
from metadata.Common import Common

class ReportAction():
    
    common = Common()
    
    def removeRenameParameter(self, root, fieldname, newfieldname, log):
        for param in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.PARAMETER, namespaces=Common.JRXML_NAMESPACE):
            paramName = param.get(Common.NAME)
            if paramName.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming parameter ' + paramName + ' to ' + paramName.replace(fieldname, newfieldname))
                    param.attrib[Common.NAME] = paramName.replace(fieldname, newfieldname)
                    for child in param:
                        if child.tag.find('parameterDescription') >= 0:
                            childtext = child.text
                            if childtext.find(fieldname) >= 0:
                                log.debug('changing parameter description to: ' + childtext.replace(fieldname, newfieldname))
                                child.text = etree.CDATA(childtext.replace(fieldname, newfieldname))
                else:
                    log.debug('removing parameter: ' + paramName)
                    param.getparent().remove(param)
    
    def removeRenameFieldInFieldList(self, root, fieldname, newfieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.JRXML_NAMESPACE):
            fieldName = field.get(Common.NAME)
            if fieldName.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming field ' + fieldName + ' to ' + fieldName.replace(fieldname, newfieldname))
                    field.attrib[Common.NAME] = fieldName.replace(fieldname, newfieldname)
                    # rename associated level property
                    for child in field:
                        childvalue = child.get(Common.VALUE)
                        if childvalue is not None and childvalue.find(fieldname) >= 0:
                            log.debug('renaming field level property to ' + childvalue.replace(fieldname, newfieldname))
                            child.attrib[Common.VALUE] = childvalue.replace(fieldname, newfieldname)
                        elif child.tag.find('fieldDescription') >= 0:
                            childtext = child.text
                            if childtext is not None and childtext.find(fieldname) >= 0:
                                log.debug('changing field description to ' + childtext.replace(fieldname, newfieldname))
                                child.text = etree.CDATA(childtext.replace(fieldname, newfieldname))
                else:
                    log.debug('removing field: ' + fieldName)
                    field.getparent().remove(field)
                
    def removeRenameQueryFieldInReportQuery(self, root, fieldname, newfieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.QUERY_FIELD):
            fieldID = field.get(Common.ID) 
            if fieldID.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming query field ' + fieldID + ' to ' + fieldID.replace(fieldname, newfieldname))
                    field.attrib[Common.ID] = fieldID.replace(fieldname, newfieldname)
                else:
                    log.debug('removing field from query: ' + fieldID)
                    field.getparent().remove(field)
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'queryFilterString'):
            filterString = field.text 
            if filterString.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('changing query filter string to ' + filterString.replace(fieldname, newfieldname))
                    field.text = filterString.replace(fieldname, newfieldname)
                else:
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
    
    def removeRenameDetailFieldInTable(self, root, fieldname, newfieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.TEXTFIELD_EXPR_TAG, namespaces=Common.JRXML_NAMESPACE):
            fieldText = field.text
            if fieldText.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming detail field ' + fieldText + ' to ' + fieldText.replace(fieldname, newfieldname))
                    field.text = etree.CDATA(fieldText.replace(fieldname, newfieldname))
                    # Fix the patternExpression node text if there is one
                    sibling = field.getnext()
                    if sibling is not None and sibling.tag.find('patternExpression') >= 0:
                        siblingText = sibling.text
                        if siblingText is not None and siblingText.find(fieldname) >= 0:
                            log.debug('renaming field name in pattern expression to ' + siblingText.replace(fieldname, newfieldname))
                            sibling.text = etree.CDATA(siblingText.replace(fieldname, newfieldname))
                else:
                    log.debug('removing detail field: ' + fieldText)
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
                    
    def removeRenameFieldInGroup(self, root, fieldname, newfieldname, log):
        for group in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.GROUP, namespaces=Common.JRXML_NAMESPACE):
            fieldName = group.get(Common.NAME)
            if fieldName.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming group ' + fieldName + ' to ' + fieldName.replace(fieldname, newfieldname))
                    group.attrib[Common.NAME] = fieldName.replace(fieldname, newfieldname)
                    # change groupExpression
                    groupExpression = group[0].text
                    if groupExpression.find(fieldname) >= 0:
                        log.debug('changing groupExpression ' + groupExpression + ' to ' + groupExpression.replace(fieldname, newfieldname))
                        group[0].text = etree.CDATA(groupExpression.replace(fieldname, newfieldname))
                else:
                    log.debug('removing group: ' + fieldName)
                    group.getparent().remove(group)
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.CGROUPHEADER, namespaces=Common.JRXML_COMPONENTS_NAMESPACE):
            fieldGroupName = field.get(Common.GROUPNAME) 
            if fieldGroupName.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming column group ' + fieldGroupName + ' to ' + fieldGroupName.replace(fieldname, newfieldname))
                    field.attrib[Common.GROUPNAME] = fieldGroupName.replace(fieldname, newfieldname)
                else:
                    log.debug('removing column group: ' + fieldGroupName)
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
                
    def removeRenameRowGroupInCrosstab(self, root, fieldname, newfieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.ROWGROUP, namespaces=Common.JRXML_NAMESPACE):
            fieldName = field.get(Common.NAME) 
            if fieldName.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming row group ' + fieldName + ' to ' + fieldName.replace(fieldname, newfieldname))
                    field.attrib[Common.NAME] = fieldName.replace(fieldname, newfieldname)
                    self.fixGroupChildNodes(field=field, fieldname=fieldname, newfieldname=newfieldname, log=log)
                else:
                    log.debug('removing row group: ' + fieldName)
                    field.getparent().remove(field)
                    # fix row group count
                    for param in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:crosstabParameter[@name="CrosstabRowGroupsCount"]', namespaces=Common.JRXML_NAMESPACE):
                        rowGroupText = param[Common.STATE_FILE_NODE_INDEX].text
                        rowGroupCount = int(rowGroupText[rowGroupText.find('(') + 1:rowGroupText.find(')')]) - 1
                        if rowGroupCount == 0:
                            self.insertDummyRowGroup(root=root, log=log)
                        else:
                            param[Common.STATE_FILE_NODE_INDEX].text = etree.CDATA('new Integer(' + str(rowGroupCount) + ')')
                    
    def removeRenameColumnGroupInCrosstab(self, root, fieldname, newfieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.COLUMNGROUP, namespaces=Common.JRXML_NAMESPACE):
            fieldName = field.get(Common.NAME) 
            if fieldName.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming column group ' + fieldName + ' to ' + fieldName.replace(fieldname, newfieldname))
                    field.attrib[Common.NAME] = fieldName.replace(fieldname, newfieldname)
                    self.fixGroupChildNodes(field=field, fieldname=fieldname, newfieldname=newfieldname, log=log)
                else:
                    log.debug('removing column group: ' + fieldName)
                    field.getparent().remove(field)
                    # fix column group count
                    for param in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:crosstabParameter[@name="CrosstabColumnGroupsCount"]', namespaces=Common.JRXML_NAMESPACE):
                        rowGroupText = param[Common.STATE_FILE_NODE_INDEX].text
                        rowGroupCount = int(rowGroupText[rowGroupText.find('(') + 1:rowGroupText.find(')')]) - 1
                        param[Common.STATE_FILE_NODE_INDEX].text = etree.CDATA('new Integer(' + str(rowGroupCount) + ')')
                        
    def fixGroupChildNodes(self, field, fieldname, newfieldname, log):
        # Fix bucket expression
        for bucket in field.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:bucketExpression', namespaces=Common.JRXML_NAMESPACE):
            bucketText = bucket.text
            if bucketText.find(fieldname) >= 0:
                log.debug('changing bucketExpression to: ' + bucketText.replace(fieldname, newfieldname))
                bucket.text = etree.CDATA(bucketText.replace(fieldname, newfieldname))
        # fix hyperlinkTooltipExpression
        for tooltipExpr in field.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:hyperlinkTooltipExpression', namespaces=Common.JRXML_NAMESPACE):
            textFieldExprText = tooltipExpr.text
            if textFieldExprText.find(fieldname) >= 0:
                log.debug('changing hyperlinkTooltipExpression to: ' + textFieldExprText.replace(fieldname, newfieldname))
                tooltipExpr.text = etree.CDATA(textFieldExprText.replace(fieldname, newfieldname))
        # fix reportElement style
        for reportElementExpr in field.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:reportElement', namespaces=Common.JRXML_NAMESPACE):
            reportElementExprStyle = reportElementExpr.get(Common.STYLE_TAG)
            if reportElementExprStyle.find(fieldname) >= 0:
                log.debug('changing reportElement style to: ' + reportElementExprStyle.replace(fieldname, newfieldname))
                reportElementExpr.attrib[Common.STYLE_TAG] = reportElementExprStyle.replace(fieldname, newfieldname)
    
    def removeRenameFieldInMeasureExpression(self, exprText, fieldname, newfieldname, log):
        if exprText.find(fieldname) >= 0:
            if newfieldname is not None and newfieldname != '_':
                log.debug('renaming field in measure expression to' + exprText.replace(fieldname, newfieldname))
                exprText = exprText.replace(fieldname, newfieldname)
            else:
                log.debug('removing field ' + fieldname + 'from measureExpression: ' + exprText)
                exprText = exprText.replace('$F{' + fieldname + '__DISCRIMINATOR}', '')
                if exprText.find('||  ||') >= 0:
                    exprText = exprText.replace('||  ||', '||')
                elif exprText.endswith(' || '):
                    exprText = self.rreplace(exprText, ' || ', '')
        return exprText
                    
    def removeRenameFieldInMeasureExpressionWrapper(self, root, fieldname, newfieldname, log):
        for expr in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:measureExpression', namespaces=Common.JRXML_NAMESPACE):
            expr.text = etree.CDATA(self.removeRenameFieldInMeasureExpression(exprText=expr.text, fieldname=fieldname, newfieldname=newfieldname, log=log))
            
    def fixConditionalStyleExpression(self, root, fieldname, newfieldname, log):
        for expr in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:conditionExpression', namespaces=Common.JRXML_NAMESPACE):
            exprText = expr.text
            if exprText.find(fieldname) >= 0:
                grandparent = expr.getparent().getparent()
                if grandparent.tag.find(Common.STYLE_TAG) >= 0:
                    grandparentName = grandparent.get(Common.NAME)
                    if grandparentName.find(fieldname) >= 0:
                        if newfieldname is not None and newfieldname != '_':
                            log.debug('changing conditional style expression to: ' + exprText.replace(fieldname, newfieldname))
                            expr.text = etree.CDATA(exprText.replace(fieldname, newfieldname))
                            log.debug('changing style name to: ' + grandparentName.replace(fieldname, newfieldname))
                            grandparent.attrib[Common.NAME] = grandparentName.replace(fieldname, newfieldname)
                        else:
                            log.debug('removing style: ' + grandparentName)
                            grandparent.getparent().remove(grandparent)
        # check parent style
        for style in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + 'n:' + Common.STYLE_TAG, namespaces=Common.JRXML_NAMESPACE):
            parentStyle = style.get(Common.STYLE_TAG)
            if parentStyle is not None and parentStyle.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('changing parent style name to: ' + parentStyle.replace(fieldname, newfieldname))
                    style.attrib[Common.STYLE_TAG] = parentStyle.replace(fieldname, newfieldname)
                else:
                    log.debug('removing style ' + style.get(Common.NAME) + ' with parent style: ' + parentStyle)
                    style.getparent().remove(style)
                        
    
    def removeRenameFieldInJRXML(self, root, fieldname, newfieldname, log):
        self.removeRenameParameter(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        self.removeRenameFieldInFieldList(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        self.removeRenameDetailFieldInTable(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        self.removeRenameFieldInGroup(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        self.removeRenameRowGroupInCrosstab(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        self.removeRenameColumnGroupInCrosstab(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        self.removeRenameFieldInMeasureExpressionWrapper(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        self.fixConditionalStyleExpression(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
                
    def removeRenameFieldInJRXMLFile(self, jrxml_filename, fieldname, newfieldname, log):
        if jrxml_filename.find(Common.PROPERTIES_EXT) == -1:
            log.debug('Preparing to remove field(s) from JRXML file: ' + jrxml_filename[jrxml_filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
            with open(jrxml_filename, 'r', encoding='utf-8') as h:
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
                self.removeRenameFieldInJRXML(root=report_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
                query_root = etree.fromstring(report_xml_inner)
                self.removeRenameQueryFieldInReportQuery(root=query_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
                # re-insert domain query back into topic
                query_bytea = etree.tostring(query_root, pretty_print=True, encoding='UTF-8')
                query_str = "".join(map(chr, query_bytea))
                self.reinsertQueryIntoReport(root=report_root, query_str=query_str)
            else:
                report_root = etree.fromstring(report_xml, parser)
                self.removeRenameFieldInJRXML(root=report_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
            report_bytea = etree.tostring(report_root, pretty_print=True, encoding='UTF-8')
            report_xml = "".join(map(chr, report_bytea))
            # re-insert original XML declaration
            report_xml = report_tuple[0] + report_xml
            with open(jrxml_filename, 'w', encoding='utf-8') as h:
                h.write(report_xml)
        
    def removeRenameFieldInState(self, root, fieldname, newfieldname, log):
        # if the field is a measure
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.MEASURE):
            fieldFieldName = field.get(Common.FIELD_NAME) 
            if fieldFieldName != None and fieldFieldName.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming measure fieldName attribute ' + fieldFieldName + ' to ' + fieldFieldName.replace(fieldname, newfieldname))
                    field.attrib[Common.FIELD_NAME] = fieldFieldName.replace(fieldname, newfieldname)
                    # check and rename the "name" attribute if necessary
                    fieldName = field.get(Common.NAME)
                    if fieldName is not None and fieldName.find(fieldname) >= 0:
                        log.debug('renaming measure name attribute ' + fieldName + ' to ' + fieldName.replace(fieldname, newfieldname))
                        field.attrib[Common.NAME] = fieldName.replace(fieldname, newfieldname)
                    # check and rename the labelOverride property if necessary
                    labelOverride = field.get(Common.LABEL_OVERRIDE)
                    if labelOverride is not None and labelOverride.find(fieldname) >= 0:
                        log.debug('changing labelOverride property from ' + labelOverride + ' to ' + labelOverride.replace(fieldname, newfieldname))
                        field.attrib[Common.LABEL_OVERRIDE] = labelOverride.replace(fieldname, newfieldname)
                else:
                    log.debug('removing measure: ' + fieldFieldName)
                    field.getparent().remove(field)
        # if the field is a dimension
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.QUERY_DIMENSION):
            fieldFieldName = field.get(Common.FIELD_NAME) 
            if fieldFieldName != None and fieldFieldName.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming dimension fieldName attribute ' + fieldFieldName + ' to ' + fieldFieldName.replace(fieldname, newfieldname))
                    field.attrib[Common.FIELD_NAME] = fieldFieldName.replace(fieldname, newfieldname)
                    # check and rename the "name" attribute if necessary
                    fieldName = field.get(Common.NAME)
                    if fieldName is not None and fieldName.find(fieldname) >= 0:
                        log.debug('renaming measure name attribute ' + fieldName + ' to ' + fieldName.replace(fieldname, newfieldname))
                        field.attrib[Common.NAME] = fieldName.replace(fieldname, newfieldname)
                else:
                    log.debug('removing dimension: ' + fieldFieldName)
                    field.getparent().remove(field)
        # if the field is a subfilter
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.EXPRESSION_STRING):
            fieldText = field.text 
            if fieldText.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming subfilter ' + fieldText + ' to ' + fieldText.replace(fieldname, newfieldname))
                    field.text = fieldText.replace(fieldname, newfieldname)
                    # check and fix parameterizedExpressionString if necessary
                    sibling = field.getnext()
                    if sibling is not None and sibling.tag == 'parameterizedExpressionString':
                        siblingText = sibling.text
                        if siblingText is not None and siblingText.find(fieldname) >= 0:
                            log.debug('renaming column(s) in parameterizedExpressionString to ' + siblingText.replace(fieldname, newfieldname))
                            sibling.text = siblingText.replace(fieldname, newfieldname)
                else:
                    parent = field.getparent()
                    log.debug('removing subfilter: ' + parent.get(Common.ID))
                    parent.getparent().remove(parent)
        # fix visible levels
        self.common.fixVisibleLevels(root=root, fieldname=fieldname, newfieldname=newfieldname, log=log)
                
    def removeRenameFieldInStateFile(self, state_filename, fieldname, newfieldname, log):
        if state_filename is not None and state_filename.find(Common.PROPERTIES_EXT) == -1:
            log.debug('Preparing to remove field(s) from state file: ' + state_filename[state_filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
            with open(state_filename, 'r', encoding='utf-8') as h:
                try:
                    state_xml = h.read()
                except UnicodeDecodeError:
                    log.debug('Ignoring non-text file: ' + state_filename)
                    return
            state_tuple = self.common.removeDeclarationNode(xml_string=state_xml)
            state_root = etree.fromstring(state_tuple[1])
            self.removeRenameFieldInState(root=state_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
            state_bytea = etree.tostring(state_root, pretty_print=True, encoding='UTF-8')
            state_xml = "".join(map(chr, state_bytea))
            # re-insert original XML declaration
            state_xml = state_tuple[0] + state_xml
            with open(state_filename, 'w', encoding='utf-8') as h:
                h.write(state_xml)
                    
    def removeRenameField(self, state_filename, jrxml_filename, fieldname, newfieldname, log):
        if isinstance(fieldname, list):
            if newfieldname is None:
                newfieldname = []
                for _ in fieldname:
                    newfieldname.append('_')
            for s1, s2 in zip(fieldname, newfieldname):
                self.removeRenameFieldInStateFile(state_filename=state_filename, fieldname=s1, newfieldname=s2, log=log)
                self.removeRenameFieldInJRXMLFile(jrxml_filename=jrxml_filename, fieldname=s1, newfieldname=s2, log=log)
        else:
            self.removeRenameFieldInStateFile(state_filename=state_filename, fieldname=fieldname, newfieldname=newfieldname, log=log)
            self.removeRenameFieldInJRXMLFile(jrxml_filename=jrxml_filename, fieldname=fieldname, newfieldname=newfieldname, log=log)
        
    def removeRenameInputControlInMetadata(self, root, fieldname, newfieldname, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + 'queryValueColumn'):
            fieldText = field.text
            if fieldText.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming input control ' + fieldText + ' to ' + fieldText.replace(fieldname, newfieldname))
                    field.text = fieldText.replace(fieldname, newfieldname)
                    # change the queryVisibleColumn field value
                    sibling = field.getprevious()
                    if sibling is not None and sibling.tag.find('queryVisibleColumn') >= 0:
                        siblingText = sibling.text
                        if siblingText.find(fieldname) >= 0:
                            log.debug('renaming queryVisibleColumn value ' + siblingText + ' to ' + siblingText.replace(fieldname, newfieldname))
                            sibling.text = siblingText.replace(fieldname, newfieldname)
                    # replace any occurences in the query string
                    for query in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + 'queryString'):
                        queryText = query.text
                        if queryText.find(fieldname) >= 0:
                            log.debug('replacing all occurences of ' + fieldname + ' in query string with ' + newfieldname)
                            query.text = queryText.replace(fieldname, newfieldname)
                    # change folder and name properties
                    for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + 'folder'):
                        fieldText = field.text
                        if fieldText.find(fieldname) >= 0:
                            log.debug('changing folder property from ' + fieldText + ' to ' + fieldText.replace(fieldname, newfieldname))
                            field.text = fieldText.replace(fieldname, newfieldname)
                            sibling = field.getnext()
                            if sibling is not None and sibling.tag.find(Common.NAME) >= 0:
                                siblingText = sibling.text
                                if siblingText.find(fieldname) >= 0:
                                    log.debug('changing name property from ' + siblingText + ' to ' + siblingText.replace(fieldname, newfieldname))
                                    sibling.text = siblingText.replace(fieldname, newfieldname)
                                # update the label if necessary
                                labelProp = sibling.getnext().getnext()
                                if labelProp is not None and labelProp.tag.find(Common.LABEL) >= 0:
                                    labelText = labelProp.text
                                    if labelText.find(fieldname) >= 0:
                                        log.debug('changing label property from ' + labelText + ' to ' + labelText.replace(fieldname, newfieldname))
                                        labelProp.text = labelText.replace(fieldname, newfieldname)
                    # change any name properties we may have missed
                    for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.LOCAL_RESOURCE + Common.REPO_PATH_SEPARATOR + Common.NAME):
                        fieldText = field.text
                        if fieldText.find(fieldname) >= 0:
                            log.debug('changing name property from ' + fieldText + ' to ' + fieldText.replace(fieldname, newfieldname))
                            field.text = fieldText.replace(fieldname, newfieldname)
                else:
                    parent = field.getparent()
                    log.debug('removing input control: ' + parent[Common.ID_NODE_INDEX].text)
                    parent.getparent().remove(parent)
            
    def removeRenameInputControlInMetadataFile(self, metadata_filename, fieldname, newfieldname, log):
        log.debug('Checking metadata file for input controls to remove: ' + metadata_filename[metadata_filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
        with open(metadata_filename) as h:
            metadata_xml = h.read()
        metadata_tuple = self.common.removeDeclarationNode(xml_string=metadata_xml)
        metadata_root = etree.fromstring(metadata_tuple[1])
        self.removeRenameInputControlInMetadata(root=metadata_root, fieldname=fieldname, newfieldname=newfieldname, log=log)
        metadata_bytea = etree.tostring(metadata_root, pretty_print=True, encoding='UTF-8')
        metadata_xml = "".join(map(chr, metadata_bytea))
        # re-insert original XML declaration
        metadata_xml = metadata_tuple[0] + metadata_xml
        if metadata_xml.endswith('\n'):
            metadata_xml = metadata_xml[0:len(metadata_xml) - 1]
        with open(metadata_filename, 'w') as h:
            h.write(metadata_xml)
            
    def rreplace(self, s, old, new):
        li = s.rsplit(old, 1)
        return new.join(li)