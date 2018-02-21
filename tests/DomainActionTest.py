'''
Created on Sep 25, 2017

@author: stevepark
'''
import unittest
import os
from unittest.mock import MagicMock
from metadata.DomainAction import DomainAction
from metadata.Common import Common

class DomainActionTest(unittest.TestCase):
    
    common=Common()
    
    DOMAIN_SCHEMA = """<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema" version="1.0">
  <dataSources>
  </dataSources>
  <items>
    <item description="name1" descriptionId="" id="name1" label="name1" labelId="" resourceId="JoinTree_1.table1.name1" />
    <item description="name2" descriptionId="" id="name2" label="name2" labelId="" resourceId="JoinTree_1.table2.name2" />
    <item description="name3" descriptionId="" id="name3" label="name3" labelId="" resourceId="JoinTree_1.table3.name3" />
  </items>
  <resources>
    <jdbcTable id="table1" datasourceId="SomeDataSourceJNDI" tableName="schema1.table1">
      <fieldList>
        <field id="table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
        <field id="name1" fieldDBName="name1" type="java.lang.String" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table2" datasourceId="SomeDataSourceJNDI" tableName="schema1.table2">
      <fieldList>
        <field id="table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="name2" fieldDBName="name2" type="java.math.BigDecimal" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table3" datasourceId="SomeDataSourceJNDI" tableName="schema1.table3">
      <fieldList>
        <field id="table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="JoinTree_1" datasourceId="SomeDataSourceJNDI" tableName="schema1.fact_table1">
      <fieldList>
        <field id="public_table1.table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
        <field id="public_table1.name1" fieldDBName="name1" type="java.lang.String" />
        <field id="public_table2.table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="public_table2.name2" fieldDBName="name2" type="java.math.BigDecimal" />
        <field id="public_table3.table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="public_table3.name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
      <joinInfo alias="public_fact_table1" referenceId="public_fact_table1" />
      <joinedDataSetList>
        <joinedDataSetRef>
          <joinString>join public_table1 public_table1 on (public_fact_table1.table1_id == public_table1.table1_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table2 public_table2 on (public_fact_table1.table2_id == public_table2.table2_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table3 public_table3 on (public_fact_table1.table3_id == public_table3.table3_id)</joinString>
        </joinedDataSetRef>
      </joinedDataSetList>
    </jdbcTable>
  </resources>
</schema>
"""
    DOMAIN_SCHEMA_WITHOUT_NAME1 = """<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema" version="1.0">
  <dataSources>
  </dataSources>
  <items>
    <item description="name2" descriptionId="" id="name2" label="name2" labelId="" resourceId="JoinTree_1.table2.name2" />
    <item description="name3" descriptionId="" id="name3" label="name3" labelId="" resourceId="JoinTree_1.table3.name3" />
  </items>
  <resources>
    <jdbcTable id="table1" datasourceId="SomeDataSourceJNDI" tableName="schema1.table1">
      <fieldList>
        <field id="table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table2" datasourceId="SomeDataSourceJNDI" tableName="schema1.table2">
      <fieldList>
        <field id="table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="name2" fieldDBName="name2" type="java.math.BigDecimal" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table3" datasourceId="SomeDataSourceJNDI" tableName="schema1.table3">
      <fieldList>
        <field id="table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="JoinTree_1" datasourceId="SomeDataSourceJNDI" tableName="schema1.fact_table1">
      <fieldList>
        <field id="public_table1.table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
        <field id="public_table2.table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="public_table2.name2" fieldDBName="name2" type="java.math.BigDecimal" />
        <field id="public_table3.table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="public_table3.name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
      <joinInfo alias="public_fact_table1" referenceId="public_fact_table1" />
      <joinedDataSetList>
        <joinedDataSetRef>
          <joinString>join public_table1 public_table1 on (public_fact_table1.table1_id == public_table1.table1_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table2 public_table2 on (public_fact_table1.table2_id == public_table2.table2_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table3 public_table3 on (public_fact_table1.table3_id == public_table3.table3_id)</joinString>
        </joinedDataSetRef>
      </joinedDataSetList>
    </jdbcTable>
  </resources>
</schema>
"""
    DOMAIN_SCHEMA_WITHOUT_NAME1_OR_NAME2 = """<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema" version="1.0">
  <dataSources>
  </dataSources>
  <items>
    <item description="name3" descriptionId="" id="name3" label="name3" labelId="" resourceId="JoinTree_1.table3.name3" />
  </items>
  <resources>
    <jdbcTable id="table1" datasourceId="SomeDataSourceJNDI" tableName="schema1.table1">
      <fieldList>
        <field id="table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table2" datasourceId="SomeDataSourceJNDI" tableName="schema1.table2">
      <fieldList>
        <field id="table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table3" datasourceId="SomeDataSourceJNDI" tableName="schema1.table3">
      <fieldList>
        <field id="table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="JoinTree_1" datasourceId="SomeDataSourceJNDI" tableName="schema1.fact_table1">
      <fieldList>
        <field id="public_table1.table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
        <field id="public_table2.table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="public_table3.table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="public_table3.name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
      <joinInfo alias="public_fact_table1" referenceId="public_fact_table1" />
      <joinedDataSetList>
        <joinedDataSetRef>
          <joinString>join public_table1 public_table1 on (public_fact_table1.table1_id == public_table1.table1_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table2 public_table2 on (public_fact_table1.table2_id == public_table2.table2_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table3 public_table3 on (public_fact_table1.table3_id == public_table3.table3_id)</joinString>
        </joinedDataSetRef>
      </joinedDataSetList>
    </jdbcTable>
  </resources>
</schema>
"""
    DOMAIN_SCHEMA_RENAME_NAME1_TO_NAME4 = """<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema" version="1.0">
  <dataSources>
  </dataSources>
  <items>
    <item description="name1" descriptionId="" id="name1" label="name1" labelId="" resourceId="JoinTree_1.table1.name1" />
    <item description="name2" descriptionId="" id="name2" label="name2" labelId="" resourceId="JoinTree_1.table2.name2" />
    <item description="name3" descriptionId="" id="name3" label="name3" labelId="" resourceId="JoinTree_1.table3.name3" />
  </items>
  <resources>
    <jdbcTable id="table1" datasourceId="SomeDataSourceJNDI" tableName="schema1.table1">
      <fieldList>
        <field id="table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
        <field id="name1" fieldDBName="name4" type="java.lang.String" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table2" datasourceId="SomeDataSourceJNDI" tableName="schema1.table2">
      <fieldList>
        <field id="table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="name2" fieldDBName="name2" type="java.math.BigDecimal" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table3" datasourceId="SomeDataSourceJNDI" tableName="schema1.table3">
      <fieldList>
        <field id="table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="JoinTree_1" datasourceId="SomeDataSourceJNDI" tableName="schema1.fact_table1">
      <fieldList>
        <field id="public_table1.table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
        <field id="public_table1.name1" fieldDBName="name4" type="java.lang.String" />
        <field id="public_table2.table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="public_table2.name2" fieldDBName="name2" type="java.math.BigDecimal" />
        <field id="public_table3.table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="public_table3.name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
      <joinInfo alias="public_fact_table1" referenceId="public_fact_table1" />
      <joinedDataSetList>
        <joinedDataSetRef>
          <joinString>join public_table1 public_table1 on (public_fact_table1.table1_id == public_table1.table1_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table2 public_table2 on (public_fact_table1.table2_id == public_table2.table2_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table3 public_table3 on (public_fact_table1.table3_id == public_table3.table3_id)</joinString>
        </joinedDataSetRef>
      </joinedDataSetList>
    </jdbcTable>
  </resources>
</schema>
"""
    DOMAIN_SCHEMA_RENAME_NAME1_TO_NAME4_AND_NAME2_TO_NAME5 = """<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema" version="1.0">
  <dataSources>
  </dataSources>
  <items>
    <item description="name1" descriptionId="" id="name1" label="name1" labelId="" resourceId="JoinTree_1.table1.name1" />
    <item description="name2" descriptionId="" id="name2" label="name2" labelId="" resourceId="JoinTree_1.table2.name2" />
    <item description="name3" descriptionId="" id="name3" label="name3" labelId="" resourceId="JoinTree_1.table3.name3" />
  </items>
  <resources>
    <jdbcTable id="table1" datasourceId="SomeDataSourceJNDI" tableName="schema1.table1">
      <fieldList>
        <field id="table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
        <field id="name1" fieldDBName="name4" type="java.lang.String" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table2" datasourceId="SomeDataSourceJNDI" tableName="schema1.table2">
      <fieldList>
        <field id="table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="name2" fieldDBName="name5" type="java.math.BigDecimal" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="table3" datasourceId="SomeDataSourceJNDI" tableName="schema1.table3">
      <fieldList>
        <field id="table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
    </jdbcTable>
    <jdbcTable id="JoinTree_1" datasourceId="SomeDataSourceJNDI" tableName="schema1.fact_table1">
      <fieldList>
        <field id="public_table1.table1_id" fieldDBName="table1_id" type="java.lang.Integer" />
        <field id="public_table1.name1" fieldDBName="name4" type="java.lang.String" />
        <field id="public_table2.table2_id" fieldDBName="table2_id" type="java.lang.Integer" />
        <field id="public_table2.name2" fieldDBName="name5" type="java.math.BigDecimal" />
        <field id="public_table3.table3_id" fieldDBName="table3_id" type="java.lang.Integer" />
        <field id="public_table3.name3" fieldDBName="name3" type="java.util.Date" />
      </fieldList>
      <joinInfo alias="public_fact_table1" referenceId="public_fact_table1" />
      <joinedDataSetList>
        <joinedDataSetRef>
          <joinString>join public_table1 public_table1 on (public_fact_table1.table1_id == public_table1.table1_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table2 public_table2 on (public_fact_table1.table2_id == public_table2.table2_id)</joinString>
        </joinedDataSetRef>
        <joinedDataSetRef>
          <joinString>join public_table3 public_table3 on (public_fact_table1.table3_id == public_table3.table3_id)</joinString>
        </joinedDataSetRef>
      </joinedDataSetList>
    </jdbcTable>
  </resources>
</schema>
"""
    fieldDBName = 'fieldDBName'
    
    def setUp(self):
        self.domain_action = DomainAction()
        self.log = self.common.configureLogging()
        self.curr_folder = '/tmp'
        self.test_domain_name = 'test_domain'
        files_path = Common.REPO_PATH_SEPARATOR + self.test_domain_name + '_files'
        self.schema_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'schema.data'
        directory = os.path.dirname(self.schema_filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(self.schema_filepath, 'w') as h1:
            h1.write(self.DOMAIN_SCHEMA)

    def tearDown(self):
        try:
            os.remove(self.schema_filepath)
        except OSError:
            pass
            
    def testRemoveFieldFromSchemaIsFK(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.text.find.return_value = -1
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.text.find.return_value = 14
        node_list = [mock_node1, mock_node2]
        mock_root.xpath = MagicMock(side_effect = [node_list, '', ''])
        try:
            self.domain_action.removeFieldFromSchema(root=mock_root, fieldname='name2', log=self.log)
            raise ValueError('This method call should not have worked')
        except ValueError as e:
            self.assertEqual('We will probably be able to handle removing key fields in the future, but for now it is not allowed', e.args[0], 'incorrect error message')
        
    def testRemoveFieldFromSchemaIsItem(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.text.find.return_value = -1
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.text.find.return_value = -1
        mock_node2.get.return_value = 'name2'
        mock_node2.getparent.return_value=mock_root
        node_list = [mock_node1, mock_node2]
        mock_root.xpath = MagicMock(side_effect = ['', node_list, ''])
        self.domain_action.removeFieldFromSchema(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node2)
        
    def testRemoveFieldFromSchemaIsField(self):
        mock_root=MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.text.find.return_value=-1
        mock_node1.get.return_value='name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.text.find.return_value=-1
        mock_node2.get.return_value='name2'
        mock_node2.getparent.return_value=mock_root
        node_list = [mock_node1, mock_node2]
        mock_root.xpath = MagicMock(side_effect = ['', '', node_list])
        self.domain_action.removeFieldFromSchema(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node2)
        
    def testRenameDBName(self):
        mock_root=MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2'
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'myschema.name1'
        node_list = [mock_node1, mock_node2, mock_node3]
        mock_root.xpath = MagicMock(side_effect=[node_list])
        self.domain_action.renameDBColumn(root=mock_root, oldcolumn='name1', newcolumn='name4', log=self.log)
        mock_node1.attrib.__setitem__.assert_called_once_with(Common.FIELD_DB_NAME, 'name4')
        mock_node3.attrib.__setitem__.assert_called_once_with(Common.FIELD_DB_NAME, 'name4')
        mock_node2.attrib.__setitem__.assert_not_called()
        
    def testRemoveField(self):
        field_name = 'name1'
        self.domain_action.removeOrRenameField(filename=self.schema_filepath, fieldname=field_name, newfieldname=None, is_rename=False, log=self.log)
        with open(self.schema_filepath) as h:
            schema_xml = h.read()
            self.assertEqual(self.DOMAIN_SCHEMA_WITHOUT_NAME1.replace(' ', ''), schema_xml.replace(' ', ''), 'Domain schema file does not match expected')
        
    def testRemoveFieldIsKey(self):
        field_name = 'table1_id'
        try:
            self.domain_action.removeOrRenameField(filename=self.schema_filepath, fieldname=field_name, newfieldname=None, is_rename=False, log=self.log)
            raise ValueError('This method call should not have worked')
        except ValueError as e:
            self.assertEqual('We will probably be able to handle removing key fields in the future, but for now it is not allowed', e.args[0], 'incorrect error message')
            
    def testRenameDBField(self):
        olddbname = 'name1'
        newdbname = 'name4'
        self.domain_action.removeOrRenameField(filename=self.schema_filepath, fieldname=olddbname, newfieldname=newdbname, is_rename=True, log=self.log)
        with open(self.schema_filepath) as h:
            schema_xml = h.read()
            self.assertEqual(self.DOMAIN_SCHEMA_RENAME_NAME1_TO_NAME4.replace(' ', ''), schema_xml.replace(' ', ''), 'Domain schema file does not match expected')
        
    def testRemoveMultipleFields(self):
        field_name = ['name1','name2']
        self.domain_action.removeOrRenameField(filename=self.schema_filepath, fieldname=field_name, newfieldname=None, is_rename=False, log=self.log)
        with open(self.schema_filepath) as h:
            schema_xml = h.read()
            self.assertEqual(self.DOMAIN_SCHEMA_WITHOUT_NAME1_OR_NAME2.replace(' ', ''), schema_xml.replace(' ', ''), 'Domain schema file does not match expected')
            
    def testRenameMultipleDBFields(self):
        olddbname = ['name1','name2']
        newdbname = ['name4','name5']
        self.domain_action.removeOrRenameField(filename=self.schema_filepath, fieldname=olddbname, newfieldname=newdbname, is_rename=True, log=self.log)
        with open(self.schema_filepath) as h:
            schema_xml = h.read()
            self.assertEqual(self.DOMAIN_SCHEMA_RENAME_NAME1_TO_NAME4_AND_NAME2_TO_NAME5.replace(' ', ''), schema_xml.replace(' ', ''), 'Domain schema file does not match expected')
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()