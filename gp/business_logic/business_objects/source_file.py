from common.utilities.inversion_of_control import Dependency, HasMethods

__author__ = 'jsternberg'

class SourceFile(object):
    """
    A source data file, usually Excel or other delimited format, stored in the filesystem.
    """
    def __init__(self):
        self.source_file_id = None
        self.full_path = None
        self.file_created_date = None
        self.file_modified_date = None
        self.file_size_in_bytes = None

    @classmethod
    def select_by_id(cls, source_file_id):
        data_repository = Dependency("DataRepository", HasMethods("select_source_file_by_source_file_id")).value
        return data_repository.select_source_file_by_source_file_id(source_file_id)

    @classmethod
    def standard_init(cls, source_file_id, full_path, file_created_date, file_modified_date, file_size_in_bytes):
        source_file = SourceFile()
        source_file.source_file_id = source_file_id
        source_file.full_path = full_path
        source_file.file_created_date = file_created_date
        source_file.file_modified_date = file_modified_date
        source_file.file_size_in_bytes = file_size_in_bytes
        return source_file