'''
Created on Aug 10, 2017

@author: stevepark
'''
import unittest
import os
from lxml import etree
from unittest.mock import MagicMock, call
from metadata.AdhocAction import AdhocAction
from metadata.Common import Common

class AdhocActionTest(unittest.TestCase):
    
    common = Common()
    
    DOMAIN_QUERY_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<domainQuery xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema">
  <field id="name1" type="java.lang.String" />
  <field id="name2" type="java.math.BigDecimal" />
  <field id="name3" type="java.util.Date" />
</domainQuery>
    """
    VIEW_STATE_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<unifiedState>
  <chartState>
    <columnGroups>
      <queryDimension fieldName="name1"/>
    </columnGroups>
    <rowGroups>
      <queryDimension fieldName="name3"/>
    </rowGroups>
  </chartState>
  <measures>
    <measure fieldName="name2"/>
  </measures>
  <subFilterList>
    <subFilter id="filter1">
      <expressionString>name1 == 'Some Value'</expressionString>
      <parameterizedExpressionString>name1 == name1_1</parameterizedExpressionString>
    </subFilter>
  </subFilterList>
</unifiedState>"""
    VIEW_CROSSTAB_JRXML_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd">
  <parameter name="name1_1" class="java.lang.String">
    <defaultValueExpression><![CDATA["Some Value"]]></defaultValueExpression>
  </parameter>
  <queryString language="domain"><![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema">
      <queryFields>
        <queryField id="name1"/>
        <queryField id="name2"/>
        <queryField id="name3"/>
      </queryFields>
    </query>
]]></queryString>
  <field name="name1">
    <property name="semantic.tree.sort.order"><![CDATA[{"name2":1,"name1":3,"name3":2}]]></property>
  </field>
  <field name="name2">
    <property name="semantic.tree.sort.order" value="1"/>
  </field>
  <field name="name3">
    <property name="semantic.tree.sort.order" value="2"/>
  </field>
</jasperReport>
"""
    VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd">
  <queryString language="domain"><![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema">
      <queryFields>
        <queryField id="name2"/>
        <queryField id="name3"/>
      </queryFields>
    </query>
]]></queryString>
  <field name="name2">
    <property name="semantic.tree.sort.order"><![CDATA[{"name2":1,"name3":2}]]></property>
  </field>
  <field name="name3">
    <property name="semantic.tree.sort.order" value="2"/>
  </field>
</jasperReport>
"""
    VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME2 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd">
  <parameter name="name1_1" class="java.lang.String">
    <defaultValueExpression><![CDATA["Some Value"]]></defaultValueExpression>
  </parameter>
  <queryString language="domain"><![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema">
      <queryFields>
        <queryField id="name1"/>
        <queryField id="name3"/>
      </queryFields>
    </query>
]]></queryString>
  <field name="name1">
    <property name="semantic.tree.sort.order"><![CDATA[{"name1":2,"name3":1}]]></property>
  </field>
  <field name="name3">
    <property name="semantic.tree.sort.order" value="1"/>
  </field>
</jasperReport>
"""
    VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1_OR_NAME2 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd">
  <queryString language="domain"><![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema">
      <queryFields>
        <queryField id="name3"/>
      </queryFields>
    </query>
]]></queryString>
  <field name="name3">
    <property name="semantic.tree.sort.order"><![CDATA[{"name3":1}]]></property>
  </field>
</jasperReport>
"""
    VIEW_METADATA_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<adhocDataView exportedWithPermissions="true">
    <folder/>
    <name>Adhoc_View_Test</name>
    <dataSource>
        <uri>/Adhoc_Topic_Test</uri>
    </dataSource>
    <inputControl>
        <localResource
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            exportedWithPermissions="false" xsi:type="inputControl">
            <folder>/Adhoc_View_Test_files</folder>
            <name>name1_1</name>
            <query>
                <localResource exportedWithPermissions="false" xsi:type="query">
                    <folder>/Adhoc_View_Test_files/name1_1_files</folder>
                    <name>name1_1</name>
                    <queryString>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema"&gt;
  &lt;groupList&gt;
    &lt;group columnName="name1" /&gt;
  &lt;/groupList&gt;
  &lt;queryFields&gt;
    &lt;queryField id="public_store.name1" /&gt;
    &lt;queryField id="name1" /&gt;
  &lt;/queryFields&gt;
&lt;/query&gt;
                        </queryString>
                    <dataSource>
                        <uri>/Domain_Test</uri>
                    </dataSource>
                </localResource>
            </query>
            <queryVisibleColumn>name1</queryVisibleColumn>
            <queryValueColumn>name1</queryValueColumn>
        </localResource>
    </inputControl>
    <inputControl>
        <localResource
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            exportedWithPermissions="false" xsi:type="inputControl">
            <folder>/Adhoc_View_Test_files</folder>
            <name>name2_1</name>
            <query>
                <localResource exportedWithPermissions="false" xsi:type="query">
                    <folder>/Adhoc_View_Test_files/name2_1_files</folder>
                    <name>name2_1</name>
                    <queryString>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema"&gt;
  &lt;groupList&gt;
    &lt;group columnName="name2" /&gt;
  &lt;/groupList&gt;
  &lt;queryFields&gt;
    &lt;queryField id="public_store.name2" /&gt;
    &lt;queryField id="name2" /&gt;
  &lt;/queryFields&gt;
&lt;/query&gt;
                        </queryString>
                    <dataSource>
                        <uri>/Domain_Test</uri>
                    </dataSource>
                </localResource>
            </query>
            <queryVisibleColumn>name2</queryVisibleColumn>
            <queryValueColumn>name2</queryValueColumn>
        </localResource>
    </inputControl>
    <resource>
        <uri>/domainQuery.xml</uri>
    </resource>
    <resource>
        <localResource
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            exportedWithPermissions="false" dataFile="topicJRXML.data" xsi:type="fileResource">
            <folder></folder>
            <name>topicJRXML</name>
        </localResource>
    </resource>
    <resource>
        <localResource
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            exportedWithPermissions="false" dataFile="stateXML.data" xsi:type="fileResource">
            <folder></folder>
            <name>stateXML</name>
        </localResource>
    </resource>
</adhocDataView>
"""
    VIEW_METADATA_FILE_WITHOUT_NAME1 = """<?xml version="1.0" encoding="UTF-8"?>
<adhocDataView exportedWithPermissions="true">
    <folder/>
    <name>Adhoc_View_Test</name>
    <dataSource>
        <uri>/Adhoc_Topic_Test</uri>
    </dataSource>
    <inputControl>
        </inputControl>
    <inputControl>
        <localResource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exportedWithPermissions="false" xsi:type="inputControl">
            <folder>/Adhoc_View_Test_files</folder>
            <name>name2_1</name>
            <query>
                <localResource exportedWithPermissions="false" xsi:type="query">
                    <folder>/Adhoc_View_Test_files/name2_1_files</folder>
                    <name>name2_1</name>
                    <queryString>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema"&gt;
  &lt;groupList&gt;
    &lt;group columnName="name2" /&gt;
  &lt;/groupList&gt;
  &lt;queryFields&gt;
    &lt;queryField id="public_store.name2" /&gt;
    &lt;queryField id="name2" /&gt;
  &lt;/queryFields&gt;
&lt;/query&gt;
                        </queryString>
                    <dataSource>
                        <uri>/Domain_Test</uri>
                    </dataSource>
                </localResource>
            </query>
            <queryVisibleColumn>name2</queryVisibleColumn>
            <queryValueColumn>name2</queryValueColumn>
        </localResource>
    </inputControl>
    <resource>
        <uri>/domainQuery.xml</uri>
    </resource>
    <resource>
        <localResource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exportedWithPermissions="false" dataFile="topicJRXML.data" xsi:type="fileResource">
            <folder/>
            <name>topicJRXML</name>
        </localResource>
    </resource>
    <resource>
        <localResource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exportedWithPermissions="false" dataFile="stateXML.data" xsi:type="fileResource">
            <folder/>
            <name>stateXML</name>
        </localResource>
    </resource>
</adhocDataView>"""
    VIEW_METADATA_FILE_WITHOUT_NAME1_OR_NAME2 = """<?xml version="1.0" encoding="UTF-8"?>
<adhocDataView exportedWithPermissions="true">
    <folder/>
    <name>Adhoc_View_Test</name>
    <dataSource>
        <uri>/Adhoc_Topic_Test</uri>
    </dataSource>
    <inputControl>
        </inputControl>
    <inputControl>
        </inputControl>
    <resource>
        <uri>/domainQuery.xml</uri>
    </resource>
    <resource>
        <localResource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exportedWithPermissions="false" dataFile="topicJRXML.data" xsi:type="fileResource">
            <folder/>
            <name>topicJRXML</name>
        </localResource>
    </resource>
    <resource>
        <localResource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exportedWithPermissions="false" dataFile="stateXML.data" xsi:type="fileResource">
            <folder/>
            <name>stateXML</name>
        </localResource>
    </resource>
</adhocDataView>"""
    QUERY_STRING = '<query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema"><queryFields><queryField id="name2"/></queryFields></query>'
    MOD_QUERY_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<query xmlns="http://www.jaspersoft.com/2007/SL/XMLSchema"><queryFields><queryField id="name2"/></queryFields></query>"""
    SORT_ORDER_STRING = '"name2":5,"name1":3,"name3":4'

    def setUp(self):
        self.adhoc_action = AdhocAction()
        self.log = self.common.configureLogging()
        self.curr_folder = '/tmp'
        self.adhocViewName = 'test_adhoc_view'
        self.adhoc_action.sort_order_map = dict(item.split(':') for item in self.SORT_ORDER_STRING.split(','))
        files_path = Common.REPO_PATH_SEPARATOR + self.adhocViewName + '_files'
        self.state_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'stateXML.data'
        self.jrxml_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'topicJRXML.data'
        self.domain_query_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'domainQuery.xml.data'
        self.view_metadata_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'Adhoc_View_Test.xml'
        directory = os.path.dirname(self.state_filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(self.state_filepath, 'w') as h1:
            h1.write(self.VIEW_STATE_FILE)
        with open(self.jrxml_filepath, 'w') as h2:
            h2.write(self.VIEW_CROSSTAB_JRXML_FILE)
        with open(self.domain_query_filepath, 'w') as h3:
            h3.write(self.DOMAIN_QUERY_FILE)
        with open(self.view_metadata_filepath, 'w') as h4:
            h4.write(self.VIEW_METADATA_FILE)

    def tearDown(self):
        try:
            os.remove(self.view_metadata_filepath)
            os.remove(self.domain_query_filepath)
            os.remove(self.jrxml_filepath)
            os.remove(self.state_filepath)
        except OSError:
            pass
            
    def testRemoveFieldFromAdhocView(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2a'
        mock_node2.getparent.return_value = mock_root
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'name2b'
        mock_node3.getparent.return_value = mock_root
        mock_node4 = MagicMock(name='mock_node4')
        mock_node4.get.return_value = 'name3'
        node_list = [mock_node1, mock_node2, mock_node3, mock_node4]
        mock_root.xpath = MagicMock(side_effect=[node_list, node_list] )
        self.adhoc_action.removeFieldFromJRXML(root=mock_root, fieldname='name2', log=self.log)
        mock_root.xpath.assert_called_with('//n:field', namespaces={'n':'http://jasperreports.sourceforge.net/jasperreports'})
        calls = [call(mock_node2), call(mock_node3)]
        mock_root.remove.assert_has_calls(calls)
            
    def testRemoveFieldFromAdhocViewFieldnameContainsDots(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2a'
        mock_node2.getparent.return_value = mock_root
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'name2b'
        mock_node3.getparent.return_value = mock_root
        mock_node4 = MagicMock(name='mock_node4')
        mock_node4.get.return_value = 'setname.name3'
        mock_node5 = MagicMock(name='mock_node5')
        mock_node5.get.return_value = Common.SORT_ORDER
        node_list = [mock_node1, mock_node2, mock_node3, mock_node4]
        mock_root.xpath = MagicMock(side_effect=[node_list, node_list])
        mock_node1.__iter__ = MagicMock(return_value = iter([mock_node5]))
        mock_node4.__iter__ = MagicMock(return_value = iter([mock_node5]))
        self.adhoc_action.removeFieldFromJRXML(root=mock_root, fieldname='name2', log=self.log)
        mock_root.xpath.assert_called_with('//n:field', namespaces={'n':'http://jasperreports.sourceforge.net/jasperreports'})
        calls = [call(mock_node2), call(mock_node3)]
        mock_root.remove.assert_has_calls(calls)
            
    def testRemoveQueryFieldFromAdhocQuery(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2a'
        mock_node2.getparent.return_value = mock_root
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'name2b'
        mock_node3.getparent.return_value = mock_root
        mock_node4 = MagicMock(name='mock_node4')
        mock_node4.get.return_value = 'name3'
        node_list = [mock_node1, mock_node2, mock_node3, mock_node4]
        mock_root.xpath = MagicMock(side_effect=[node_list, node_list])
        self.adhoc_action.removeQueryFieldFromAdhocQuery(root=mock_root, fieldname='name2', log=self.log)
        mock_root.xpath.assert_called_with('//n:queryField', namespaces=Common.DOMAIN_QUERY_NAMESPACE)
        calls = [call(mock_node2), call(mock_node3)]
        mock_root.remove.assert_has_calls(calls)
            
    def testReinsertQueryIntoAdhocTopic(self):
        mock_root = MagicMock(name='mock_root')
        mock_node = MagicMock(name='mock_node1')
        node_list = [mock_node]
        mock_root.xpath = MagicMock(side_effect=node_list)
        mod_query_str = self.adhoc_action.reinsertQueryIntoAdhocTopic(root=mock_root, query_str=self.QUERY_STRING)
        self.assertTrue(mod_query_str.find(self.MOD_QUERY_STRING) >= 0)
            
    def testRemoveFieldFromStateIsMeasure(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2'
        mock_node2.getparent.return_value = mock_root
        node_list = [mock_node1, mock_node2]
        mock_root.xpath = MagicMock(side_effect=[node_list, '', '', ''] )
        self.adhoc_action.removeFieldFromState(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node2)
            
    def testRemoveFieldFromStateIsDimension(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.text = None
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2'
        mock_node2.getparent.return_value = mock_root
        node_list = [mock_node1, mock_node2]
        mock_root.xpath = MagicMock(side_effect=['', node_list, '', ''])
        self.adhoc_action.removeFieldFromState(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node2)
            
    def testRemoveFieldFromStateIsField(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.text = None
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2'
        mock_node2.getparent.return_value = mock_root
        node_list = [mock_node1, mock_node2]
        mock_root.xpath = MagicMock(side_effect=['', '', node_list, ''])
        self.adhoc_action.removeFieldFromState(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node2)
            
    def testRemoveFieldFromStateIsParameter(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.getparent.return_value = mock_root
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.text.find.return_value = 0
        mock_node2.getparent.return_value = mock_node1
        mock_root.xpath = MagicMock(side_effect=['', '', '', [mock_node2]])
        self.adhoc_action.removeFieldFromState(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node1)
            
    def testFixSortOrderIsNone(self):
        result = self.adhoc_action.fixSortOrder(fieldname='fieldname', semantic_tree_sort_order=None)
        self.assertIsNone(result, 'result was not None')
        
    def testFixSortOrder(self):
        fixed_sort_order = '{"name1":1,"name3":2}'
        semantic_tree_sort_order = self.adhoc_action.fixSortOrder('name2', semantic_tree_sort_order='{' + self.SORT_ORDER_STRING + '}')
        self.assertEqual(fixed_sort_order, semantic_tree_sort_order, 'semantic_tree_sort_order not fixed')
            
    def testFixSortingValues(self):
        fixed_sort_order = '"name2":3,"name1":1,"name3":2'
        fixed_sort_order = dict(item.split(':') for item in fixed_sort_order.split(','))
        self.adhoc_action.fixSortingValues()
        self.assertEqual(fixed_sort_order, self.adhoc_action.sort_order_map, 'semantic_tree_sort_order not fixed')
        
    def testViewRemoveFieldNoMatches(self):
        field_name = 'name4'
        self.adhoc_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            self.assertEqual(self.VIEW_STATE_FILE, state_xml, 'state file changed')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE, jrxml_xml, 'jrxml file changed')
            
    def testViewRemoveFieldMatchesIsMeasure(self):
        field_name = 'name2'
        self.adhoc_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            self.assertTrue(state_xml.find(field_name) == -1, 'Measure ' + field_name + ' not removed from state file')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME2, jrxml_xml, 'Measure ' + field_name + ' not removed from jrxml file or file corrupted')
            
    def testViewRemoveFieldMatchesIsDimension(self):
        field_name = 'name1'
        self.adhoc_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            self.assertTrue(state_xml.find(field_name) == -1, 'Dimension ' + field_name + ' not removed from state file')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1, jrxml_xml, 'Dimension ' + field_name + ' not removed from jrxml file or file corrupted')
            
    def testViewRemoveMultipleFields(self):
        field_name = ['name1','name2']
        self.adhoc_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            for singular in field_name:
                self.assertTrue(state_xml.find(singular) == -1, 'Field ' + singular + ' not removed from state file')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1_OR_NAME2, jrxml_xml, 'One or more of list ' + str(field_name) + ' not removed from jrxml file or file corrupted')
            
    def testTopicRemoveField(self):
        field_name = 'name1'
        self.adhoc_action.removeField(state_filename=self.domain_query_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.domain_query_filepath) as h:
            domain_query_xml = h.read()
            self.assertTrue(domain_query_xml.find(field_name) == -1, 'Field ' + field_name + ' not removed from domain query file')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1, jrxml_xml, 'Dimension ' + field_name + ' not removed from jrxml file or file corrupted')
    
    def testViewRemoveInputControlFromMetadataFiles(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.text.find.return_value = 0
        mock_node2 = MagicMock(name='mock_node2')
        mock_node1.getparent.return_value = mock_node2
        mock_node3 = etree.Element('mock_node3')
        mock_node3.text = 'Deleted Node'
        mock_node2.__getitem__.return_value = mock_node3
        mock_node4 = MagicMock(name='mock_node4')
        mock_node2.getparent.return_value = mock_node4
        node_list = [mock_node1]
        mock_root.xpath = MagicMock(side_effect=[node_list])
        self.adhoc_action.removeInputControlFromMetadataFiles(root=mock_root, fieldname='name2', log=self.log)
        mock_node4.remove.assert_called_with(mock_node2)
        
    def testViewRemoveInputControlFromMetadata(self):
        field_name = 'name1'
        self.adhoc_action.removeInputControlFromMetadata(metadata_filename=self.view_metadata_filepath, fieldname=field_name, log=self.log)
        with open(self.view_metadata_filepath) as h:
            view_metadata_xml = h.read()
            self.assertEqual(self.VIEW_METADATA_FILE_WITHOUT_NAME1, view_metadata_xml, 'Input control ' + field_name + ' not removed from metadata file or file corrupted')
        
    def testViewRemoveMultipleInputControlsFromMetadata(self):
        field_name = ['name1','name2']
        self.adhoc_action.removeInputControlFromMetadata(metadata_filename=self.view_metadata_filepath, fieldname=field_name, log=self.log)
        with open(self.view_metadata_filepath) as h:
            view_metadata_xml = h.read()
            self.assertEqual(self.VIEW_METADATA_FILE_WITHOUT_NAME1_OR_NAME2, view_metadata_xml, 'One or more input controls from list ' + str(field_name) + ' not removed from metadata file or file corrupted')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()