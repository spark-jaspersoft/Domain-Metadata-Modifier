'''
Created on Sep 22, 2017

@author: stevepark
'''
import unittest
from unittest.mock import MagicMock, PropertyMock
from metadata.Common import Common

class CommonTest(unittest.TestCase):

    def setUp(self):
        self.common = Common()
        self.log = self.common.configureLogging()
        self.test_datasource_name = 'test_domain'

    def tearDown(self):
        pass
            
    def testRemoveDeclarationNode(self):
        some_tag_xml = '<someTag/>'
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
        report_xml = xml_declaration + '\n' + some_tag_xml
        report_tuple = self.common.removeDeclarationNode(report_xml)
        self.assertEqual(xml_declaration + '\n', report_tuple[0], 'xml declaration does not match')
        self.assertEqual(some_tag_xml, report_tuple[1], 'xml body does not match')
            
    def testRemoveDeclarationNodeNoDeclarationNode(self):
        some_tag_xml = '<someTag/>'
        report_xml = some_tag_xml
        report_tuple = self.common.removeDeclarationNode(report_xml)
        self.assertEqual('', report_tuple[0], 'xml declaration should be empty')
        self.assertEqual(some_tag_xml, report_tuple[1], 'xml body does not match')
        
    def testFixVisibleLevels(self):
        fieldname = 'name1'
        newfieldname = 'name2'
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1_text = PropertyMock(return_value=fieldname)
        type(mock_node1).text = mock_node1_text
        mock_root.xpath = MagicMock(side_effect=[[mock_node1]])
        self.common.fixVisibleLevels(root=mock_root, fieldname=fieldname, newfieldname=newfieldname, log=self.log)
        mock_node1_text.assert_called_with(newfieldname)
        
    def testFixVisibleLevelsDoesNotMatch(self):
        fieldname = 'name1'
        newfieldname = 'name2'
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1_text = PropertyMock(return_value='something else')
        type(mock_node1).text = mock_node1_text
        mock_root.xpath = MagicMock(side_effect=[[mock_node1]])
        self.common.fixVisibleLevels(root=mock_root, fieldname=fieldname, newfieldname=newfieldname, log=self.log)
        mock_node1_text.assert_called_once_with()
        
    def testFixVisibleLevelsIsRemove(self):
        fieldname = 'name1'
        mock_root = MagicMock(name='mock_root')
        self.common.fixVisibleLevels(root=mock_root, fieldname=fieldname, newfieldname=None, log=self.log)
        mock_root.assert_not_called()
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()