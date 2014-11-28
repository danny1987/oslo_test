from oslo.vmware import api
from oslo.vmware import vim_util
from oslo.vmware import pbm
import unittest
import json
        
class PbmCITest(unittest.TestCase):
    """Test class for utility methods in vim_util.py"""
    def setUp(self):
        pbm_wsdl=pbm.get_pbm_wsdl_location("5.5")
        with open("pbm_test.json") as template:
            self.spec = json.load(template)
        env = self.spec.get("environment")
        self.session = api.VMwareAPISession(host = env.get("host"), 
                                            port = env.get("port"),
                                            server_username = env.get("server_username"),
                                            server_password = env.get("server_password"), 
                                            api_retry_count = env.get("api_retry_count"), 
                                            task_poll_interval = env.get("task_poll_interval"), 
                                            scheme = env.get("scheme"),
                                            pbm_wsdl_loc = pbm_wsdl)
        self.vim = self.session.vim
        self.pbm = self.session.pbm
    
    def test_get_all_profiles(self):
        objects = pbm.get_all_profiles(self.session)
        test_spec = self.spec.get("test_get_all_profiles")
        expected_profile_names = test_spec.get("profile_names")
        profile_name_list = []
        for one_object in objects:
            profile_name_list.append(one_object.name)
        for one_profile in expected_profile_names:
            self.assertTrue(one_profile in profile_name_list)
        
    def test_get_profile_id_by_name(self):
        test_spec = self.spec.get("test_get_profile_id_by_name")
        profile_name = test_spec.get("profile_name")
        profile_id = pbm.get_profile_id_by_name(self.session, profile_name)
        expected_profile_id = test_spec.get("profile_id")
        self.assertEqual(profile_id.uniqueId, expected_profile_id)
    
    def test_get_profile_id_by_name_with_invalid_profile(self):
        profile_name = "THISISATEST"
        profile_id = pbm.get_profile_id_by_name(self.session, profile_name)
        self.assertFalse(profile_id)
    
    def test_filter_hubs_by_profile(self):
        pbm_client_factory = self.pbm.client.factory
        profile_id = pbm_client_factory.create('ns0:PbmProfileId')
        hub = pbm_client_factory.create('ns0:PbmPlacementHub')
        test_spec = self.spec.get("test_filter_hubs_by_profile")
        profile_id.uniqueId = test_spec.get("unique_id")
        datastore_list = test_spec.get("datastores")
        hubs = []
        for each_ds in datastore_list:
            hub.hubId = each_ds
            hub.hubType = "Datastore"
            hubs.append(hub)
        
        filtered_hubs = pbm.filter_hubs_by_profile(self.session, hubs, profile_id)
        self.assertIsNotNone(filtered_hubs)

if __name__ == '__main__':
   unittest.main()
