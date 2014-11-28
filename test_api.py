"""
CI tests for VMware API utility module
"""
from oslo.vmware import api 
from oslo.vmware import vim_util
import unittest
import json

class ApiCITest(unittest.TestCase):
    """Test class for utility methods in vim_util.py"""
    def setUp(self):
        """Run before each test method to initialize test environment"""
        with open("api_test.json") as template:
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

    def test_poweron_instance(self):
        vm_name = self.spec.get("test_poweron_instance").get("vm_name")
        vm_ref = vim_util.get_moref(vm_name, "VirtualMachine")
        poweron_task = self.session.invoke_api(self.vim, "PowerOnVM_Task", vm_ref)
        task_info = self.session.wait_for_task(poweron_task)
        self.assertEqual(task_info.state, "success")
    
    def test_poweroff_instance(self):
        vm_name = self.spec.get("test_poweroff_instance").get("vm_name")
        vm_ref = vim_util.get_moref(vm_name, "VirtualMachine")
        poweroff_task = self.session.invoke_api(self.vim, "PowerOffVM_Task", vm_ref)
        task_info = self.session.wait_for_task(poweroff_task)
        self.assertEqual(task_info.state, "success")


if __name__ == "__main__":
    unittest.main()
