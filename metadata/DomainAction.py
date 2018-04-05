'''
Created on Sep 25, 2017

@author: stevepark
'''
from lxml import etree
from metadata.Common import Common

class DomainAction():
    
    common = Common()
    
    def renameOrRemoveFieldFromSchema(self, root, fieldname, newfieldname, newdbcolname, log):
        # if field is foreign key
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.JOIN_STRING, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            if field.text.find(fieldname) >= 0:
                raise ValueError('We will probably be able to handle removing key fields in the future, but for now it is not allowed')
        # if field is an item
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.ITEM, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            idValue = field.get(Common.ID)
            if idValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming item ' + idValue + ' to ' + idValue.replace(fieldname, newfieldname))
                    field.attrib[Common.ID] = idValue.replace(fieldname, newfieldname)
                    field.attrib[Common.RESOURCE_ID] = field.get(Common.RESOURCE_ID).replace(fieldname, newfieldname)
                    # change the label only if the label ID property isn't set (ignore if using I18N)
                    if len(field.get(Common.LABEL_ID)) == 0:
                        field.attrib[Common.LABEL] = field.get(Common.LABEL).replace(fieldname, newfieldname)
                else:
                    log.debug('removing item: ' + idValue)
                    field.getparent().remove(field)
        # if field is a field
        for field in root.xpath(Common.REPO_PATH_SEPARATOR + Common.REPO_PATH_SEPARATOR + Common.FIELD, namespaces=Common.DOMAIN_QUERY_NAMESPACE):
            idValue = field.get(Common.ID)
            if idValue.find(fieldname) >= 0:
                if newfieldname is not None and newfieldname != '_':
                    log.debug('renaming field ' + idValue + ' to ' + idValue.replace(fieldname, newfieldname))
                    field.attrib[Common.ID] = idValue.replace(fieldname, newfieldname)
                    if newdbcolname is not None and newdbcolname != '_':
                        log.debug('Renaming field DB column name to: ' + newdbcolname)
                        field.attrib[Common.FIELD_DB_NAME] = newdbcolname
                else:
                    log.debug('removing field: ' + idValue)
                    field.getparent().remove(field)
    
    def removeOrRenameField(self, filename, fieldname, newfieldname, newdbcolname, log):
        log.debug('Preparing to remove field(s) from domain schema file: ' + filename[filename.rfind(Common.REPO_PATH_SEPARATOR) + 1:])
        with open(filename, 'r', encoding='utf-8') as h:
            schema_xml = h.read()
        schema_tuple = self.common.removeDeclarationNode(xml_string=schema_xml)
        schema_root = etree.fromstring(schema_tuple[1])
        if isinstance(fieldname, list):
            if newfieldname is None:
                newfieldname = []
                for _ in fieldname:
                    newfieldname.append('_')
            if newdbcolname is None:
                newdbcolname = []
                for _ in fieldname:
                    newdbcolname.append('_')
            for s1, s2, s3 in zip(fieldname, newfieldname, newdbcolname):
                self.renameOrRemoveFieldFromSchema(root=schema_root, fieldname=s1, newfieldname=s2, newdbcolname=s3, log=log)
        else:
            self.renameOrRemoveFieldFromSchema(root=schema_root, fieldname=fieldname, newfieldname=newfieldname, newdbcolname=newdbcolname, log=log)
        schema_bytea = etree.tostring(schema_root, pretty_print=True, encoding='UTF-8')
        schema_xml = "".join(map(chr, schema_bytea))
        schema_xml = schema_tuple[0] + schema_xml
        with open(filename, 'w', encoding='utf-8') as h:
            h.write(schema_xml)