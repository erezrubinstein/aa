import unittest
from geoprocessing.business_logic.business_objects.address import Address

__author__ = 'jsternberg'


class AddressTests(unittest.TestCase):

    def setUp(self):
        # nothing to do here, for now
        pass

    def tearDown(self):
        # nothing to do here, for now
        pass

    def test_address_zip_validation(self):
        good_zips = ['12345','12345-1234']
        correctable_zips = [('1234','01234'),('123','00123'),(12345,'12345')]
        bad_zips = ['12345-123','12345-12','abcde', 'abcd', 'abcde-abcd', 'abcde-1234', 12345.1]

        # make sure good zips work
        for good_zip in good_zips:
            test_address = Address().standard_init(None, 123, 'Fake St', 'Anytown', 'ZZ', good_zip, None, 1, 2, None, None)
            self.assertIsInstance(test_address, Address)

        #make sure correctable zips get corrected
        for correctable_zip in correctable_zips:
            test_address = Address().standard_init(None, 123, 'Fake St', 'Anytown', 'ZZ', correctable_zip[0], None, 1, 2, None, None)
            self.assertEqual(test_address.zip_code, correctable_zip[1])

        # make sure bad zips fail with the right kind of exception
        for bad_zip in bad_zips:
            try:
                address = Address().standard_init(None, 123, 'Fake St', 'Anytown', 'ZZ', bad_zip, None, 1, 2, None, None)

            except ValueError:
                pass
            except Exception as err:
                self.fail('Unexpected exception thrown:', err)
            else:

                self.fail('Expected exception not thrown')


if __name__ == '__main__':
    unittest.main()