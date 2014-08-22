from geoprocessing.business_logic.enums import CompetitionType
from geoprocessing.business_logic.business_helpers.monopoly_transitions.base_monopoly_transition import BaseMonopolyTransition

__author__ = 'erezrubinstein'


class AbsoluteToForeignCompetitorsTransition(BaseMonopolyTransition):
    """
    Close the previous monopoly.  NO INSERT
    """
    def __init__(self):
        super(AbsoluteToForeignCompetitorsTransition, self).__init__()

    def _get_transition_date(self):
        # get min open date for current foreign_competitors only
        foreign_competitors = filter(lambda store : store.company_id != self._home_store.company_id, self._new_away_stores)
        return min(store.opened_date for store in foreign_competitors)

    def _close_previous_monopoly(self):
        self.data_repository.close_monopoly_record(self._home_store.store_id, self._trade_area_id, self._transition_date, self._batch_monopolies_list)


class AbsoluteToSingleMonopolyTransition(BaseMonopolyTransition):
    """
    Close the previous monopoly.  NO INSERT
    """
    def __init__(self):
        super(AbsoluteToSingleMonopolyTransition, self).__init__()

    def _get_transition_date(self):
        # get min open date for all current away stores
        return min(store.opened_date for store in self._new_away_stores)

    def _close_previous_monopoly(self):
        self.data_repository.close_monopoly_record(self._home_store.store_id, self._trade_area_id, self._transition_date, self._batch_monopolies_list)

    def _create_new_monopoly(self):
        self.data_repository.insert_monopoly(self._home_store.store_id, CompetitionType.SinglePlayerMonopoly, self._trade_area_id, self._transition_date, self._batch_monopolies_list)




