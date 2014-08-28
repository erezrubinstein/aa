# coding=utf-8
from __future__ import division
import cStringIO as StringIO
import hashlib
import codecs

from tests.integration_tests.framework.svc_test_collection import ServiceTestCollection
from core.common.utilities.include import *


###################################################################################################

class FileObj(object):
    def __init__(self, filename, local_path, remote_path):
        self.filename = filename
        self.local_path = local_path
        self.remote_path = remote_path
        self.local_full_filename = os.path.join(local_path, filename)
        self.remote_full_filename = os.path.join(remote_path, filename)


class RDSTestCollection(ServiceTestCollection):

    def initialize(self):

        self.user_id = 'test@nexusri.com'
        self.source = "rds_test_collection.py"
        self.context = {"user_id": self.user_id, "source": self.source}

    def setUp(self):

        self.remote_dirs = ['integration_test_files/', u'integration_test_files/pbf’s/']

        self.local_dir = os.path.join(os.path.dirname(__file__), 'data/')

        # create file objects to represent the test files. The paths are baked into the expected file info
        # so the constructor paths should not be modified below:
        self.test_files = [
            FileObj('rds_test_file.letters', self.local_dir, self.remote_dirs[0]),
            FileObj('DavidHasselhoff.png', self.local_dir, self.remote_dirs[0]),
            FileObj('PBF193-Fun_Bot.gif', self.local_dir, self.remote_dirs[1]),
            FileObj('PBF210-Wishing_Well.gif', self.local_dir, self.remote_dirs[1]),
            FileObj(u'rds_test_unicode’s_¢oolio.whatev', self.local_dir, self.remote_dirs[0])
        ]

        self.expected_file_info = {
            "rds_test_file.letters":
                {
                    "contentType": "application/octet-stream",
                    "chunkSize": 262144,
                    "filename": self.remote_dirs[0] + "rds_test_file.letters",
                    "length": 36,

                    "md5": "d11d6bf735f63fc57b29c0c10532387b",

                    "metadata":
                        {
                            "dl_history": [],
                            "num_dls": 0,
                            "path": self.remote_dirs[0],
                            "permissions": [],
                            "context": self.context,
                            "short_filename": "rds_test_file.letters"
                        }
                },
            "DavidHasselhoff.png": {
                "contentType": "image/png",
                "chunkSize": 262144,
                "filename": self.remote_dirs[0] + "DavidHasselhoff.png",
                "length": 398957,
                "md5": "ccfcb786e9c4cb39a5bafc3e2f11b6c8",
                "metadata": {
                    "dl_history": [],
                    "num_dls": 0,
                    "path": self.remote_dirs[0],
                    "permissions": [],
                    "context": self.context,
                    "short_filename": "DavidHasselhoff.png"
                }
            },
            "PBF193-Fun_Bot.gif": {
                "contentType": "image/gif",
                "chunkSize": 262144,
                "filename": self.remote_dirs[1] + "PBF193-Fun_Bot.gif",
                "length": 99437,
                "md5": "2cde064f9686f16403145353c1c02e33",
                "metadata": {
                    "num_dls": 0,
                    "path": self.remote_dirs[1],
                    "dl_history": [],
                    "permissions": [],
                    "context": self.context,
                    "short_filename": "PBF193-Fun_Bot.gif"
                }
            },
            "PBF210-Wishing_Well.gif": {
                "contentType": "image/gif",
                "chunkSize": 262144,
                "filename": self.remote_dirs[1] + "PBF210-Wishing_Well.gif",
                "length": 75943,
                "md5": "0fa6d1797e58a384aa8ba7b64523ed68",
                "metadata": {
                    "num_dls": 0,
                    "path": self.remote_dirs[1],
                    "dl_history": [],
                    "context": self.context,
                    "permissions": [],
                    "short_filename": "PBF210-Wishing_Well.gif"
                }
            },
            u'rds_test_unicode’s_¢oolio.whatev':{
                "contentType": "application/octet-stream",
                "chunkSize": 262144,
                "filename": self.remote_dirs[0] + u'rds_test_unicode’s_¢oolio.whatev',
                "length": 64,
                "md5": "eecbe95f5bc13eb371c4fc6d45a18ec2",
                "metadata": {
                    "num_dls": 0,
                    "path": self.remote_dirs[0],
                    "dl_history": [],
                    "context": self.context,
                    "permissions": [],
                    "short_filename": u'rds_test_unicode’s_¢oolio.whatev'
                }
            }
        }

        self.expected_post_download_file_metadata = {
            "metadata":
                {
                    "num_dls": 1
                }
        }

        self.expected_file_contents = {
            "integration_test_files/rds_test_file.letters": """This is an integration test for RDS."""
        }

    def tearDown(self):

        self.__delete_folder(self.remote_dirs[0])

        # second folder for updating files
        self.__delete_folder('integration_test_files_updated/')

    ## private methods ##

    def __upload_files(self, file_objs):
        """
        Upload files to RDS.  If any files are going to the same path, batch upload those.
        """
        remote_paths = set([file_obj.remote_path for file_obj in file_objs])
        file_ids = {}

        for remote_path in remote_paths:
            files = {}
            for file_obj in file_objs:
                if file_obj.remote_path != remote_path:
                    continue
                with open(file_obj.local_full_filename, 'rb') as f:
                    files[file_obj.filename] = StringIO.StringIO(f.read())

            file_names_ids = self.rds_access.call_post_file(remote_path,
                                                     files,
                                                     self.context,
                                                     metadata = None)

            for file_obj in files:
                expected_key = remote_path + file_obj
                self.test_case.assertIn(expected_key, file_names_ids)

            file_ids.update(file_names_ids)

        return file_ids

    def __download_file(self, lookup_type, lookup):

        possible_lookup_types = {
            "id": self.rds_access.call_get_file_by_id,
            "name": self.rds_access.call_get_file_by_name
        }

        response = possible_lookup_types[lookup_type](lookup, self.context)

        self.test_case.assert200(response)
        return response

    def __get_file_info(self, filename):

        response = self.rds_access.call_get_file_info_by_name(filename, self.context)
        return response

    def __compare_dict(self, expected, candidate):
        """
        Recursively compare the file info dictionary returned by RDS to an expected dictionary.
        Here we are only comparing a subset of the file info because we can't compare
        upload time and _id to a predefined value.
        """
        same = True
        bad_keys = []
        mismatched_keys = []
        for key in expected.keys():
            if isinstance(expected[key], dict):
                if key not in candidate or not isinstance(candidate[key], dict):
                    bad_keys.append(key)
                    same = False
                else:
                    if not self.__compare_dict(expected[key], candidate[key]):
                        mismatched_keys.append({"expected:": {key: expected[key]},
                                                "candidate": {key: candidate[key]}})
                        same = False
            elif key not in candidate:
                bad_keys.append(key)
                same = False
            elif candidate[key] != expected[key]:
                mismatched_keys.append({"expected:": {key: expected[key]},
                                        "candidate": {key: candidate[key]}})
                same = False


        if not same:
            self.logger.error("__compare_dict() found that expected doesn't match candidate:")
            self.logger.error({"bad_keys": bad_keys, "mismatched_keys": mismatched_keys})
            self.logger.error({"expected": expected, "candidate": candidate})


        return same

    def __get_file_listing(self, files_path):
        if files_path == '/':
            files_path = ''
        return self.rds_access.call_get_files(files_path).json()

    def __remove_linux_BOM(self, data):
        """
        Linux has a BOM (byte order mark) at the beginning of a file describing its UTF encoding.
        Remove this if it exists.
        """
        if data.startswith(codecs.BOM_UTF8):
            return data.lstrip(codecs.BOM_UTF8)
        else:
            return data

    def __delete_file_by_name(self, filename):
        """
        Delete a specific filename
        """
        message = self.rds_access.call_delete_file_by_name(filename)
        self.test_case.assertIn('Deleted file by name: %s' % filename, message)

    def __delete_folder(self, path_to_delete):
        """
        Delete a folder and recursively delete subfolders if recursive flag == True
        """
        message = self.rds_access.call_delete_folder_by_name(path_to_delete)
        self.test_case.assertIn("Recursively deleted folder: " + path_to_delete, message)

    def __generate_md5_checksum(self, contents):
        m = hashlib.md5()
        m.update(contents)
        return m.hexdigest()

    ##---------------------------## test methods ##---------------------------##

    def rds_test_upload_files(self):
        """
        Test that 2 files can upload and that all the expected file attributes and metadata are
        exactly as expected.
        """
        upload_list = [f for f in self.test_files if f.remote_path == 'integration_test_files/']
        file_ids = self.__upload_files(upload_list)

        # test file_ids length == 3
        self.test_case.assertEqual(3, len(file_ids))

        # test file info
        for file_to_upload in upload_list:
            #remote_file_path = self.remote_dirs[0] + file_to_upload[1]
            rds_file_info = self.__get_file_info(file_to_upload.remote_full_filename)
            
            self.test_case.assertDictContainsSubset(self.expected_file_info[file_to_upload.filename], rds_file_info)
            self.test_case.assertEqual(file_ids[file_to_upload.remote_full_filename], rds_file_info['_id'])

    def test_rds_test_update_path(self):
        """
        Test that you can change the path of a file.
        """
        file_obj = FileObj('DavidHasselhoff.png', self.local_dir, self.remote_dirs[0])
        file_ids = self.__upload_files([file_obj])

        # make sure when file was uploaded
        self.test_case.assertEqual(1, len(file_ids))

        # query the file and make sure it's path is correct
        rds_file_info = self.__get_file_info(file_obj.remote_full_filename)
        self.test_case.assertEqual(rds_file_info["metadata"]["path"], self.remote_dirs[0])
        self.test_case.assertEqual(rds_file_info["filename"], self.remote_dirs[0] + 'DavidHasselhoff.png')

        # update the file's path and verify that it's correct
        rds_id = file_ids[rds_file_info["filename"]]
        response = self.rds_access.call_update_file_path(rds_id, "integration_test_files_updated/", self.context)

        # make sure response was success
        self.test_case.assertEqual(response, "success")

        # query object again and make sure its name changed
        rds_file_info = self.__get_file_info("integration_test_files_updated/DavidHasselhoff.png")
        self.test_case.assertEqual(rds_file_info["metadata"]["path"], "integration_test_files_updated/")
        self.test_case.assertEqual(rds_file_info["filename"], 'integration_test_files_updated/DavidHasselhoff.png')


    def rds_test_download_file_by_name(self):
        """
        Test that a file can be downloaded by name and that its metadata is updated.
        """
        upload_list = [self.test_files[2], self.test_files[4]]
        file_ids = self.__upload_files(upload_list)

        # test file_ids length == 2
        self.test_case.assertEqual(2, len(file_ids))

        for upload_file in upload_list:
            filename_to_download = upload_file.remote_full_filename
            short_filename = upload_file.filename
            downloaded_file = self.__download_file('name', filename_to_download)

            decoded_file_contents = self.__remove_linux_BOM(downloaded_file.content)
            downloaded_md5 = self.__generate_md5_checksum(decoded_file_contents)

            # check file name
            self.test_case.assertEqual(self.expected_file_info[upload_file.filename]["metadata"]["short_filename"],
                                       downloaded_file.headers['content-disposition'].split('filename=')[1])

            # check file contents are what we expect
            self.test_case.assertEqual(downloaded_md5, self.expected_file_info[upload_file.filename]['md5'])

            # check file type
            self.test_case.assertEqual(self.expected_file_info[upload_file.filename]['contentType'],
                                       downloaded_file.headers['content-type'].split(";")[0])

            # check file metadata reflects one download
            updated_file_info = self.__get_file_info(filename_to_download)

            self.test_case.assertTrue(self.__compare_dict(self.expected_post_download_file_metadata,
                                                          updated_file_info))


    def rds_test_download_file_by_id(self):
        """
        Test that a file can be downloaded by id and that its metadata is updated.
        """
        upload_list = [self.test_files[1]]
        file_ids = self.__upload_files(upload_list)
        filename_to_download = upload_list[0].remote_full_filename
        short_filename = upload_list[0].filename
        file_id_to_download = file_ids[filename_to_download]
        downloaded_file = self.__download_file('id', file_id_to_download)

        decoded_file_contents = self.__remove_linux_BOM(downloaded_file.content)

        downloaded_md5 = self.__generate_md5_checksum(decoded_file_contents)

        # check file name
        self.test_case.assertEqual(short_filename,
                                   downloaded_file.headers['content-disposition'].split('filename=')[1])

        # check file contents are what we expect
        self.test_case.assertEqual(downloaded_md5, self.expected_file_info[upload_list[0].filename]['md5'])

        # check file type
        self.test_case.assertEqual(self.expected_file_info[upload_list[0].filename]['contentType'],
                                   downloaded_file.headers['content-type'].split(";")[0])

        # check file metadata reflects one download
        updated_file_info = self.__get_file_info(filename_to_download)

        self.test_case.assertTrue(self.__compare_dict(self.expected_post_download_file_metadata,
                                                      updated_file_info))

    def rds_test_file_manager_listing(self):
        """
        Test that the file manager properly displays files and directories
        """
        #upload_list = self.__create_upload_list(self.test_files, self.local_dir, self.remote_dirs[0])
        file_ids = self.__upload_files(self.test_files)
        listing_root = self.__get_file_listing('/')

        # check that self.remote_dir[0] is the directory listing
        self.test_case.assertEqual([self.remote_dirs[0]], listing_root['dirs'])

        # check the first remote dir, should be one sub-dir and only the 2 files in the first remote dir
        listing_remote_dir = self.__get_file_listing(self.remote_dirs[0])
        self.test_case.assertEqual([u'pbf’s/'], listing_remote_dir['dirs'])
        self.test_case.assertEqual(3, len(listing_remote_dir['files']))
        self.test_case.assertIn('DavidHasselhoff.png', listing_remote_dir['files'])
        self.test_case.assertIn('rds_test_file.letters', listing_remote_dir['files'])

        # check the second remote dir, should be no sub-dir and only the 2 files in the second remote dir
        listing_remote_dir = self.__get_file_listing(self.remote_dirs[1])
        self.test_case.assertEqual([], listing_remote_dir['dirs'])
        self.test_case.assertEqual(2, len(listing_remote_dir['files']))
        self.test_case.assertIn('PBF193-Fun_Bot.gif', listing_remote_dir['files'])
        self.test_case.assertIn('PBF210-Wishing_Well.gif', listing_remote_dir['files'])

    def rds_test_get_file_info(self):
        """
        Test getting file info
        """
        upload_list = [self.test_files[2]]
        self.__upload_files(upload_list)

        filename_to_download = upload_list[0].remote_full_filename

        rds_file_info = self.__get_file_info(filename_to_download)

        self.test_case.assertTrue(self.__compare_dict(self.expected_file_info[self.test_files[2].filename],
                                                      rds_file_info))

    def rds_test_delete_file(self):
        """
        Test deleting a file
        """
        upload_list = [self.test_files[0], self.test_files[2]]
        self.__upload_files(upload_list)

        filename_to_delete = upload_list[0].remote_full_filename

        # delete the file
        self.__delete_file_by_name(filename_to_delete)

        # test the root dir listing, should have integration_test_files/ as a folder
        listing_root = self.__get_file_listing('/')

        self.test_case.assertIn(self.remote_dirs[0], listing_root['dirs'])

        # test the integration_test_files/ dir listing
        listing_remote_dir_0 = self.__get_file_listing(self.remote_dirs[0])
        self.test_case.assertEqual([], listing_remote_dir_0['files'])
        self.test_case.assertEqual([self.remote_dirs[1].split('/')[1] + '/'], listing_remote_dir_0['dirs'])

        # test the chuck_norris/ dir listing
        listing_remote_dir_1 = self.__get_file_listing(self.remote_dirs[1])
        self.test_case.assertEqual([self.test_files[2].filename], listing_remote_dir_1['files'])
        self.test_case.assertEqual([], listing_remote_dir_1['dirs'])

    def rds_test_delete_folder_recursive(self):
        """
        Test recursively deleting a folder
        """
        upload_list = self.test_files
        self.__upload_files(upload_list)

        self.__delete_folder(self.remote_dirs[0])

        listing_root = self.__get_file_listing('/')

        # test that all remote doesn't contain top dir or any files
        self.test_case.assertNotIn(self.remote_dirs[0], listing_root['dirs'])
        self.test_case.assertTrue(self.__compare_dict({'files': [], 'dirs': []},
                                                      listing_root))

    def rds_test_delete_file_that_does_not_exist_fails(self):
        """
        Test deleting a file that doesn't exist.  Should throw an InputError
        """
        raised_error = False
        try:
            self.__delete_file_by_name('some_fake_file.txt')
        except Exception as e:
            if 'Can not delete some_fake_file.txt because it does not exist' in e.message:
                raised_error = True

        self.test_case.assertTrue(raised_error)

    def rds_test_upload_duplicate_file_md5_fails(self):
        """
        Test that uploading the same file contents results in a unique md5 checksum failure
        """
        raised_error = False

        test_file = self.test_files[0]
        upload_list = [test_file]
        self.__upload_files(upload_list)
        # now try to upload it again, with a different path/filename for kicks
        test_file.remote_path = 'test/'
        test_file.remote_full_filename = test_file.remote_path + test_file.filename
        try:
            self.__upload_files(upload_list)
        except Exception as e:
            if 'already exists' in e.message:
                raised_error = True

        self.test_case.assertTrue(raised_error)

    def rds_test_upload_duplicate_filename_fails(self):
        """
        Test that uploading the same filename results in a failure
        """
        raised_error = False
        test_file = self.test_files[0]
        self.__upload_files([test_file])
        # now try to upload it again, with the same filename but different file contents
        test_file_same_filename = FileObj('rds_test_file.letters', self.local_dir, self.remote_dirs[0])
        test_file_same_filename.local_full_filename = os.path.join(self.local_dir, 'DavidHasselhoff.png')
        try:
            self.__upload_files([test_file_same_filename])
        except Exception as e:
            if 'already exists' in e.message:
                raised_error = True

        self.test_case.assertTrue(raised_error)


###################################################################################################
