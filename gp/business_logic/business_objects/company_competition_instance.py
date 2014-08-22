__author__ = 'erezrubinstein'

class CompanyCompetitionInstance(object):
    """
    This class is for defining an away store instance.
    It is not a pure representation of a store object, but rather a "view" representation that combines other properties
    """
    def __init__(self):
        self.competitive_company_id = None
        self.home_company_id = None
        self.away_company_id = None
        self.competition_strength = None
        self.created_at = None
        self.updated_at = None
        self.assumed_start_date = None
        self.assumed_end_date = None


    #################################################### Factory Methods ##################################################################

    @classmethod
    def standard_init(cls, competitive_company_id, home_company_id, away_company_id, competition_strength, created_at, updated_at, assumed_start_date, assumed_end_date):
        cc = CompanyCompetitionInstance()
        cc.competitive_company_id = competitive_company_id
        cc.home_company_id = home_company_id
        cc.away_company_id = away_company_id
        cc.competition_strength = competition_strength
        cc.created_at = created_at
        cc.updated_at = updated_at
        cc.assumed_start_date = assumed_start_date
        cc.assumed_end_date = assumed_end_date
        return cc

    @classmethod
    def master_competition_init(cls, home_company_id, away_company_id, competition_strength, assumed_start_date, assumed_end_date):
        cc = CompanyCompetitionInstance()
        cc.home_company_id = home_company_id
        cc.away_company_id = away_company_id
        cc.competition_strength = competition_strength
        cc.assumed_start_date = assumed_start_date
        cc.assumed_end_date = assumed_end_date
        return cc