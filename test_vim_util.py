"""
CI tests for VMware API utility module
"""
from oslo.vmware import api 
from oslo.vmware import vim_util
import unittest
import json

class VimUtilCITest(unittest.TestCase):
    """Test class for utility methods in vim_util.py"""
    def setUp(self):
        """Run before each test method to initialize test environment"""
        with open("vim_util_test.json") as template:
            self.spec = json.load(template)
        env = self.spec.get("environment")
        self.session = api.VMwareAPISession(host=env.get("host"), 
                                            port=env.get("port"), 
                                            server_username=env.get("server_username"),
                                            server_password=env.get("server_password"),
                                            api_retry_count=env.get("api_retry_count"), 
                                            task_poll_interval=env.get("task_poll_interval"), 
                                            scheme=env.get("scheme"))
        self.vim = self.session.vim

    def test_get_objects_without_properties(self):
        """Get the host info from rootFolder"""
        test_spec = self.spec.get("test_get_objects")
        expected_type = test_spec.get("_type")
        expected_host_ips = test_spec.get("host_ips")
        
        object_content = self.session.invoke_api(vim_util, 
                                                'get_objects', 
                                                self.vim, 
                                                'HostSystem', 
                                                100)
        host_ip_list = []
        if object_content:
            self.assertIsNotNone(object_content.objects)
            for one_object in object_content.objects:
                self.assertEqual(one_object.obj._type, expected_type)
                if hasattr(one_object, 'propSet'):
                    dynamic_properties = one_object.propSet
                    for prop in dynamic_properties:
                        host_ip_list.append(prop.val)
        for each_ip in expected_host_ips:
            self.assertTrue(each_ip in host_ip_list)
        
    def test_get_objects_with_properties(self):
        """Get the aggregate resource stats of a cluster"""
        expected_result = self.spec.get("test_get_objects_with_properties")
        expected_type = expected_result.get("_type")
        expected_datastore_list = []

        for each_datastore in expected_result.get("datastore_infos"):
            datastore_name = each_datastore["name"]
            expected_datastore_list.append(datastore_name)
        datastore_list = []
        
        object_content = self.session.invoke_api(vim_util, 
                                                'get_objects', 
                                                self.vim, 
                                                'Datastore', 
                                                100,  
                                                ['name'])
        for one_object in object_content.objects:
            self.assertEqual(one_object.obj._type, expected_type)
            if hasattr(one_object, 'propSet'):
                dynamic_properties = one_object.propSet
                prop_dict = {}
                for prop in dynamic_properties:
                    if prop.name == "name":
                        datastore_list.append(prop.val)
        
        for each_ds_name in datastore_list:
            self.assertTrue(each_ds_name in datastore_list)

    def test_get_object_properties(self):
        """Get host properties with properties specified """
        test_spec = self.spec.get("test_get_object_properties")
        host_moref = vim_util.get_moref(test_spec.get("host_id"), 'HostSystem')
        objects = self.session.invoke_api(  vim_util, 
                                            'get_object_properties', 
                                            self.vim, 
                                            host_moref, 
                                            ["summary.hardware.numCpuCores", "summary.hardware.numCpuThreads"])   
        self.assertIsNotNone(objects)
        expected_numCpuCores = test_spec.get("numCpuCores")
        expected_numCpuThreads = test_spec.get("numCpuThreads")
        numCpuCores = 0
        numCpuThreads = 0
        if hasattr(objects[0], 'propSet'):
            dynamic_properties = objects[0].propSet
            for prop in dynamic_properties:
                if prop.name == "summary.hardware.numCpuCores":
                    numCpuCores = prop.val
                else:
                    numCpuThreads = prop.val
        self.assertEqual(expected_numCpuCores, numCpuCores)
        self.assertEqual(expected_numCpuThreads, numCpuThreads)

    def test_cancel_retrievcal(self):
        object_content = self.session.invoke_api(vim_util, 'get_objects', self.vim, 'VirtualMachine', 1)
        token = vim_util._get_token(object_content)
        self.assertIsNotNone(token)
        vim_util.cancel_retrieval(self.vim, object_content)
    
    def test_continue_retrieval(self):
        object_content = self.session.invoke_api(vim_util, 'get_objects', self.vim, 'VirtualMachine', 1)
        token = vim_util._get_token(object_content)
        self.assertIsNotNone(token)
        result = vim_util.continue_retrieval(self.vim, object_content)
        self.assertIsNotNone(result.objects)
    
    def test_register_extension(self):
        """test register extension"""
        test_spec = self.spec.get("test_register_extension")
        key = test_spec.get("key")
        extension_manager = self.vim.service_content.extensionManager
        self.vim.client.service.UnregisterExtension(extension_manager, key)
        extention_object = vim_util.find_extension(self.vim, key)
        self.assertIsNone(extention_object)
        
        vim_util.register_extension(self.vim, key, None)
        extention_object = vim_util.find_extension(self.vim, key)
        self.assertIsNotNone(extention_object)

    def test_get_vc_version(self):
        test_spec = self.spec.get("test_get_vc_version")
        vc_version = vim_util.get_vc_version(self.session)
        expected_version = test_spec.get("vc_version")
        self.assertEqual(vc_version, expected_version)

if __name__ == "__main__":
    unittest.main()
