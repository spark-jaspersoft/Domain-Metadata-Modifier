'''
Created on Feb 15, 2018

@author: stevepark
'''
import unittest
from metadata.Common import Common
from metadata.DomainMetadataModHelper import DomainMetadataModHelper

class DomainMetadataModHelperTest(unittest.TestCase):
    
    TEST_URL = 'http://localhost:8080/jasperserver-pro/'
    TEST_PASSWORD = 'superuser'

    def setUp(self):
        self.domainMetadataModHelper = DomainMetadataModHelper()
        self.inputs = ['executable', self.TEST_URL, self.TEST_PASSWORD, 'Domain_Test', 'name1']

    def tearDown(self):
        pass

    def testConnectToServer(self):
        pass

    def testDownloadExport(self):
        pass
        
    def testUploadImport(self):
        pass
        
    def testProcessInputsIsSingle(self):
        self.domainMetadataModHelper.processInputs(self.inputs)
        self.assertIsNone(self.domainMetadataModHelper.newfieldname, 'newfieldname should not be set')
        
    def testProcessInputsIsMultiple(self):
        self.inputs[4] = 'name1,name2'
        self.domainMetadataModHelper.processInputs(self.inputs)
        self.assertEqual(self.domainMetadataModHelper.fieldname, ['name1','name2'])
        self.assertIsNone(self.domainMetadataModHelper.newfieldname, 'newfieldname should not be set')
        
    def testProcessInputsIsDBRename(self):
        new_field = 'name4'
        self.inputs.append(new_field)
        self.domainMetadataModHelper.processInputs(self.inputs)
        self.assertEqual(new_field, self.domainMetadataModHelper.newfieldname, 'newfieldname should be set')
        
    def testProcessInputsIsDBRenameMultiple(self):
        self.inputs[4] = 'name1,name2'
        self.inputs.append('name4,name5')
        self.domainMetadataModHelper.processInputs(self.inputs)
        self.assertEqual(['name4','name5'], self.domainMetadataModHelper.newfieldname, 'newfieldname not set correctly')
        
    def testProcessInputsNotEnoughParams(self):
        del self.inputs[3]
        try:
            self.domainMetadataModHelper.processInputs(self.inputs)
            self.fail('test should have thrown a ValueError')
        except ValueError as e:
            self.assertEqual(Common.NOT_ENOUGH_VALUES, str(e))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDownloadExport']
    unittest.main()