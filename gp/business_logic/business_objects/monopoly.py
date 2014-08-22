import datetime

__author__ = 'erezrubinstein'

class Monopoly(object):
    def __init__(self, store_id, monopoly_type_id, trade_area_id, start_date, end_date):
        self.store_id = store_id
        self.monopoly_type_id = monopoly_type_id
        self.trade_area_id = trade_area_id
        self.start_date = start_date
        self.end_date = end_date

    def __eq__(self, other):

        # sometimes mongo selects the start date slightly off.  so this just makes sure they're within one seconds
        return self.store_id == other.store_id and self.monopoly_type_id == other.monopoly_type_id and self.trade_area_id == other.trade_area_id and \
               (other.start_date - self.start_date) < datetime.timedelta(seconds = 1) and \
               (other.end_date - self.end_date) < datetime.timedelta(seconds = 1)