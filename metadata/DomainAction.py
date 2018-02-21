'''
Created on Sep 25, 2017

@author: stevepark
'''
from lxml import etree
from metadata.Common import Common

class DomainAction():
    
    common = Common()
    
    def removeFieldFromSchema(self, root, fieldname, log):
        # if field is foreign key
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.JOIN_STRING, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            if field.text.find(fieldname) >= 0:
                raise ValueError('We will probably be able to handle removing key fields in the future, but for now it is not allowed')
        # if field is an item
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.ITEM, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            if field.get(Common.ID).find(fieldname) >= 0:
                log.debug('removing item: ' + field.get(Common.ID))
                field.getparent().remove(field)
        # if field is a field
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            if field.get(Common.ID).find(fieldname) >= 0:
                log.debug('removing field: ' + field.get(Common.ID))
                field.getparent().remove(field)
    
    def removeOrRenameField(self, filename, fieldname, newfieldname, is_rename, log):
        log.debug('Preparing to remove field(s) from domain schema file: ' + filename[filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
        with open(filename) as h:
            schema_xml = h.read()
        schema_tuple = self.common.removeDeclarationNode(xml_string=schema_xml)
        schema_root = etree.fromstring(schema_tuple[1])
        if is_rename is True:
            if isinstance(fieldname, list):
                for s1, s2 in zip(fieldname, newfieldname):
                    self.renameDBColumn(root=schema_root, oldcolumn=s1, newcolumn=s2, log=log)
            else:
                self.renameDBColumn(root=schema_root, oldcolumn=fieldname, newcolumn=newfieldname, log=log)
        else:
            if isinstance(fieldname, list):
                for singular in fieldname:
                    self.removeFieldFromSchema(root=schema_root, fieldname=singular, log=log)
            else:
                self.removeFieldFromSchema(root=schema_root, fieldname=fieldname, log=log)
        schema_bytea = etree.tostring(schema_root, pretty_print=True, encoding='UTF-8')
        schema_xml = "".join(map(chr, schema_bytea))
        schema_xml = schema_tuple[0] + schema_xml
        with open(filename, 'w') as h:
            h.write(schema_xml)
            
    def renameDBColumn(self, root, oldcolumn, newcolumn, log):
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            if field.get(Common.FIELD_DB_NAME).find(oldcolumn) >= 0:
                log.debug('Renaming field DB column name: ' + oldcolumn + '   to new column name: ' + newcolumn)
                field.attrib[Common.FIELD_DB_NAME] = newcolumn