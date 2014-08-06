from datetime import datetime
from common.utilities.inversion_of_control import Dependency, HasMethods

__author__ = 'erezrubinstein'

class BaseMonopolyTransition(object):
    """
    This is the base monopoly transition object.
    Every type of monopoly transition will inherit from this and define the following:
        1) how it gets a transition date
        2) should it close a previous monopoly record
        3) should it insert a new monopoly record
    """
    def __init__(self):
        self.data_repository = None

    def transition(self, home_store, trade_area_id, new_away_stores, previous_away_stores, batch_monopolies_list):
        """
        This is the main entry point of a monopoly transition
        """
        # initialize class variables
        self._home_store = home_store
        self._trade_area_id = trade_area_id
        self._new_away_stores = new_away_stores
        self._previous_away_stores = previous_away_stores
        self._batch_monopolies_list = batch_monopolies_list

        # get the transition date
        self._transition_date = self.__convert_string_datetime(self._get_transition_date())

        # refresh the monopolies (i.e. close/open) in db
        self._close_previous_monopoly()

        # do not create the monopoly if this transition represents the store's closing date
        if self._home_store._assumed_closed_date is None or  self._transition_date != self._home_store._assumed_closed_date:
            self._create_new_monopoly()

    def __convert_string_datetime(self, date):
        """
        This is a cloud_provider so that this object can deal with dates and string representations of dates
        """
        if isinstance(date, basestring):
            return datetime.strptime(date, '%Y-%m-%d')
        return date

    ######################################################## Template Methods ########################################################

    def _get_transition_date(self):
        """
        This is the template method for getting a transition date
        """
        pass

    def _close_previous_monopoly(self):
        """
        This is the template method for closing a monopoly.  default is do not close.
        """
        pass

    def _create_new_monopoly(self):
        """
        This is the template method for insert a monopoly.  default is do not insert.
        """
        pass



class NoTransition(BaseMonopolyTransition):
    """
    This is "No" transition object.  It's used for objects that do not need a transition
    """
    def __init__(self):
        super(NoTransition, self).__init__()