from common.utilities.inversion_of_control import Dependency, HasMethods

__author__ = 'jsternberg'

class SourceFileRecord(object):
    """
    A source data file record, typically a row in an Excel file or other delimited format.
    Currently this class is oriented towards the 'loader file' format, but it may be extended over time to other formats.
    """
    def __init__(self):
        self.source_file_record_id = None
        self.source_file_id = None
        self.row_number = None
        self.record = None
        self.loader_record_id = None
        self.street_number = None
        self.street = None
        self.city = None
        self.state = None
        self.zip = None
        self.phone = None
        self.country_id = None
        self.latitude = None
        self.longitude = None
        self.suite = None
        self.note = None
        self.company_generated_store_number = None
        self.store_format = None
        self.opened_date = None
        self.source_date = None
        self.shopping_center_name = None


    @classmethod
    def select_by_id(cls, source_file_record_id):
        data_repository = Dependency("DataRepository", HasMethods("select_source_file_record_by_source_file_record_id")).value
        return data_repository.select_source_file_record_by_source_file_record_id(source_file_record_id)

    @classmethod
    def standard_init(cls, source_file_record_id, source_file_id, row_number, record, loader_record_id, street_number, street,
                            city, state, zip, phone, country_id, latitude, longitude, suite, note, company_generated_store_number,
                            store_format, opened_date, source_date, shopping_center_name):
        source_file_record = SourceFileRecord()
        source_file_record.source_file_record_id = source_file_record_id
        source_file_record.source_file_id = source_file_id
        source_file_record.row_number = row_number
        source_file_record.record = record
        source_file_record.loader_record_id = loader_record_id
        source_file_record.street_number = street_number
        source_file_record.street = street
        source_file_record.city = city
        source_file_record.state = state
        source_file_record.zip = zip
        source_file_record.phone = phone
        source_file_record.country_id = country_id
        source_file_record.latitude = latitude
        source_file_record.longitude = longitude
        source_file_record.suite = suite
        source_file_record.note = note
        source_file_record.company_generated_store_number = company_generated_store_number
        source_file_record.store_format = store_format
        source_file_record.opened_date = opened_date
        source_file_record.source_date = source_date
        source_file_record.shopping_center_name = shopping_center_name
        return source_file_record