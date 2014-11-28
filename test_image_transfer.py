"""
CI tests for Image Transfer module
"""
from oslo.vmware import api 
from oslo.vmware import vim_util
from oslo.vmware import image_transfer
from oslo.vmware import rw_handles
import urllib2
import six.moves.urllib.parse as urlparse
import exceptions
import unittest
import json
import test_connection_to_file

def create_spec(cf, name, size_kb, disk_type, ds_name):
    controller_device = cf.create('ns0:VirtualLsiLogicController')
    controller_device.key = -100
    controller_device.busNumber = 0
    controller_device.sharedBus = 'noSharing'
    controller_spec = cf.create('ns0:VirtualDeviceConfigSpec')
    controller_spec.operation = 'add'
    controller_spec.device = controller_device

    disk_device = cf.create('ns0:VirtualDisk')
    disk_device.capacityInKB = int(size_kb)
    # for very small disks allocate at least 1KB
    disk_device.capacityInKB = max(1, int(size_kb))
    disk_device.key = -101
    disk_device.unitNumber = 0
    disk_device.controllerKey = -100
    disk_device_bkng = cf.create('ns0:VirtualDiskFlatVer2BackingInfo')
    disk_device_bkng.thinProvisioned = True
    disk_device_bkng.fileName = '[%s]' % ds_name
    disk_device_bkng.diskMode = 'persistent'
    disk_device.backing = disk_device_bkng
    disk_spec = cf.create('ns0:VirtualDeviceConfigSpec')
    disk_spec.operation = 'add'
    disk_spec.fileOperation = 'create'
    disk_spec.device = disk_device

    vm_file_info = cf.create('ns0:VirtualMachineFileInfo')
    vm_file_info.vmPathName = '[%s]' % ds_name

    create_spec = cf.create('ns0:VirtualMachineConfigSpec')
    create_spec.name = name
    create_spec.guestId = 'otherGuest'
    create_spec.numCPUs = 1
    create_spec.memoryMB = 128
    create_spec.deviceChange = [controller_spec, disk_spec]
    create_spec.extraConfig = None
    create_spec.files = vm_file_info

    return create_spec

class ImageTransferCITest(unittest.TestCase):
    """Test class for utility methods in image_transfer.py"""
    def setUp(self):
        """Run before each test method to initialize test environment"""
        self.session = api.VMwareAPISession(host="10.117.168.113", port=443, server_username="root", server_password="vmware", api_retry_count=5, task_poll_interval=1, scheme="https")
        self.vim = self.session.vim
        #with open("vim_util_test.json") as template:
        #    self.spec = json.load(template)

    def tearDown(self):
        pass
        #self.session.logout(
#    def test_12(self):
#        res_pool_ref = vim_util.get_moref("resgroup-27", "ResourcePool")
#        vm_folder_ref = vim_util.get_moref("group-v22", "Folder")
#        vm_name = "%s_%s" % ("OSTACK_IMG", "10006")
#        client_factory = self.vim.client.factory
#        vm_import_spec = client_factory.create('ns0:VirtualMachineImportSpec')
#        vm_import_spec.configSpec = create_spec(client_factory, vm_name, 0, "thin", "datastore1") 
#        write_handle = rw_handles.VmdkWriteHandle(self.session, self.session._host, self.session._port, res_pool_ref, vm_folder_ref, vm_import_spec, 1000) 
#        print write_handle
    def test_download_stream_optimized_data_1(self):
        context = None

        vm_ref = vim_util.get_moref("vm-232", "VirtualMachine")
        read_handle = rw_handles.VmdkReadHandle(self.session,
                                                self.session._host,
                                                self.session._port,
                                                vm_ref,
                                                None,
                                                3356672*1024)
        res_pool_ref = vim_util.get_moref("resgroup-27", "ResourcePool")
        vm_folder_ref = vim_util.get_moref("group-v22", "Folder")
        vm_name = "%s_%s" % ("OSTACK_IMG", "10003")
        client_factory = self.vim.client.factory
        vm_import_spec = client_factory.create('ns0:VirtualMachineImportSpec')
        vm_import_spec.configSpec = create_spec(client_factory, vm_name, 0, "thin", "datastore1") 
        #print vm_import_spec
        imported_vm_ref = image_transfer.download_stream_optimized_data(
                context,
                600,
                read_handle,
                session = self.session,
                host = self.session._host,
                port = self.session._port,
                image_size = 3356672*1024,
                resource_pool = res_pool_ref,
                vm_folder = vm_folder_ref,
                vm_import_spec = vm_import_spec
                )
        print imported_vm_ref
        #unregister the vm
        self.session.invoke_api(self.vim, "UnregisterVM", imported_vm_ref)

    def test_download_stream_optimized_data(self):
        return
        context = None
        store = test_connection_to_file.store()
        fp = store._query()
        res_pool_ref = vim_util.get_moref("resgroup-27", "ResourcePool")
        vm_folder_ref = vim_util.get_moref("group-v22", "Folder")
        vm_name = "%s_%s" % ("OSTACK_IMG", "10013")
        client_factory = self.vim.client.factory
        vm_import_spec = client_factory.create('ns0:VirtualMachineImportSpec')
        vm_import_spec.configSpec = create_spec(client_factory, vm_name, 0, "thin", "datastore1") 
        #print vm_import_spec
        imported_vm_ref = image_transfer.download_stream_optimized_data(
                context,
                500,
                fp,
                session = self.session,
                host = self.session._host,
                port = self.session._port,
                image_size = 1000000,
                resource_pool = res_pool_ref,
                vm_folder = vm_folder_ref,
                vm_import_spec = vm_import_spec
                )
        print imported_vm_ref
        #unregister the vm
        self.session.invoke_api(self.vim, "UnregisterVM", imported_vm_ref)
        #TODO future needs to delete the datastore file
    def test_copy_stream_optimized_disk(self):
        return
        vm_ref = vim_util.get_moref("vm-232", "VirtualMachine")
        fo = open("res.txt", "w")
        context = None
        image_transfer.copy_stream_optimized_disk(context, 2000, fo,
                session = self.session,
                host = self.session._host,
                port = self.session._port,
                vm = vm_ref,
                vmdk_size = 3335168,#TODO 
                vmdk_file_path = None
                )
#    def test_more(self):
#        vm_ref = vim_util.get_moref("vm-232", "VirtualMachine")
#        print rw_handles.VmdkReadHandle(self.session, self.session._host, self.session._port, vm_ref, None, 1000)
if __name__ == "__main__":
    #a = VimUtilCITest()
    unittest.main()
