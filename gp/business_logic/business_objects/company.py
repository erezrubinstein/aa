from common.utilities.inversion_of_control import Dependency, HasMethods


class Company(object):
    """
    This class is a company as represented by the database
    """
    def __init__(self):
        self.company_id = None
        self.ticker = None
        self.name = None
        self.created_at = None
        self.updated_at = None


##################################################### Factory Methods ##################################################
    @classmethod
    def standard_init(cls, company_id, ticker, name, created_at, updated_at):
        company = Company()
        company.company_id = company_id
        company.ticker = ticker
        company.name = name
        company.created_at = created_at
        company.updated_at = updated_at
        return company

    @classmethod
    def select_by_id(cls, company_id):
    # query the address
        data_repository = Dependency("DataRepository", HasMethods("get_company_by_id")).value
        return data_repository.get_company_by_id(company_id)