'''
Created on Sep 22, 2017

@author: stevepark
'''
import unittest
from unittest.mock import MagicMock
from metadata.Common import Common

class CommonTest(unittest.TestCase):

    def setUp(self):
        self.common = Common()
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
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()