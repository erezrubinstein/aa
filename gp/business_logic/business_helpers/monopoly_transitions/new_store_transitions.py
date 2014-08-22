from geoprocessing.business_logic.enums import CompetitionType
from geoprocessing.business_logic.business_helpers.monopoly_transitions.base_monopoly_transition import BaseMonopolyTransition

__author__ = 'erezrubinstein'


class NewStoreToSinglePlayerMonopolyTransition(BaseMonopolyTransition):
    """
    Add a new single player monopoly
    """
    def __init__(self):
        super(NewStoreToSinglePlayerMonopolyTransition, self).__init__()

    def _get_transition_date(self):
        # if there are previous away stores, then get the max close date of all foreign competitors
        return self._home_store.opened_date

    def _create_new_monopoly(self):
        self.data_repository.insert_monopoly(self._home_store.store_id, CompetitionType.SinglePlayerMonopoly, self._trade_area_id, self._transition_date, self._batch_monopolies_list)



class NewStoreToAbsoluteMonopolyTransition(BaseMonopolyTransition):
    """
    Add a new absolute monopoly
    """
    def __init__(self):
        super(NewStoreToAbsoluteMonopolyTransition, self).__init__()

    def _get_transition_date(self):
        # if there are previous away stores, then get the max close date of all competitors
        return self._home_store.opened_date

    def _create_new_monopoly(self):
        self.data_repository.insert_monopoly(self._home_store.store_id, CompetitionType.AbsoluteMonopoly, self._trade_area_id, self._transition_date, self._batch_monopolies_list)