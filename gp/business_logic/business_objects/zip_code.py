from common.utilities.inversion_of_control import Dependency, HasMethods

__author__ = 'jsternberg'


class ZipCode(object):
    """
    This class represents information about a zip code, as used by the census.
    To be more precise, this class represents Zip Code Tabulation Areas
    http://www.census.gov/geo/reference/zctas.html

    Implements lazy loading for properties and factory methods
    """

    def __init__(self, zip_code):
        """
        The zip code itself is required, and acts like an ID
        """
        self.zip_code = zip_code
        self.centroid = None
        # other demographics will go here next...

    #####################################################  Factory Methods  #######################################################################

    @classmethod
    def standard_init(cls, zip_code, centroid):
        zip = ZipCode(zip_code)
        zip.centroid = centroid
        return zip

    @classmethod
    def select_by_zip_code(cls, zip_code):
        data_repository = Dependency("DataRepository", HasMethods("get_zip_by_zip_code")).value
        return data_repository.get_zip_by_zip_code(zip_code)


    #################################################### Operator Overloads ###########################################################################

    def __eq__(self, other):
        return self.zip_code == other.zip_code and self.centroid == other.centroid