from geoprocessing.business_logic.enums import CompetitionType
from geoprocessing.business_logic.business_helpers.monopoly_transitions.absolute_monopoly_transitions import AbsoluteToForeignCompetitorsTransition, AbsoluteToSingleMonopolyTransition
from geoprocessing.business_logic.business_helpers.monopoly_transitions.has_foreign_competitor_transitions import ForeignCompetitorsToSinglePlayerMonopolyTransition, ForeignCompetitorsToAbsoluteMonopolyTransition
from geoprocessing.business_logic.business_helpers.monopoly_transitions.base_monopoly_transition import NoTransition
from geoprocessing.business_logic.business_helpers.monopoly_transitions.new_store_transitions import NewStoreToSinglePlayerMonopolyTransition, NewStoreToAbsoluteMonopolyTransition
from geoprocessing.business_logic.business_helpers.monopoly_transitions.single_player_monopoly_transitions import SinglePlayerToForeignCompetitorsTransition, SinglePlayerToAbsoluteMonopolyTransition
from common.utilities.inversion_of_control import Dependency, HasMethods

__author__ = 'erezrubinstein'


class MonopolyTransitionHelper(object):
    """
    This class helps with transition a monopoly, which can be very complex
    """

    @classmethod
    def transition_monopoly_record(cls, home_store, trade_area_id, new_away_stores, previous_away_stores, data_repository, batch_monopolies_list):
        """
        main transition entry.  previous competitors were updated in the step before the monopoly transition
        """
        # get previous monopoly record to see if this is a new monopoly
        previous_monopoly = data_repository.select_active_monopoly_record(home_store.store_id, trade_area_id, batch_monopolies_list)

        # figure out new and old monopoly types according to new away stores and previous away stores
        new_monopoly_type = cls.__get_competition_type(new_away_stores, home_store)

        # special case for new stores
        if previous_monopoly is None and (previous_away_stores is None or len(previous_away_stores) == 0):
            previous_monopoly_type = None
        else:
            previous_monopoly_type = cls.__get_competition_type(previous_away_stores, home_store)

        # create transition object and initialize its parameters
        transition = cls.__get_monopoly_transition_state(new_monopoly_type, previous_monopoly_type, data_repository)
        transition.transition(home_store, trade_area_id, new_away_stores, previous_away_stores, batch_monopolies_list)

    @classmethod
    def __get_monopoly_transition_state(cls, new_monopoly_type, previous_monopoly_type, data_repository):
        # default transition is do nothing
        transition = NoTransition()

        # for all the possible transitions, create the appropriate object
        # this is somewhat messy and there might be better ways of doing it
        if previous_monopoly_type == CompetitionType.HasForeignCompetitors:
            if new_monopoly_type == CompetitionType.SinglePlayerMonopoly:
                transition = ForeignCompetitorsToSinglePlayerMonopolyTransition()
            elif new_monopoly_type == CompetitionType.AbsoluteMonopoly:
                transition = ForeignCompetitorsToAbsoluteMonopolyTransition()
        elif previous_monopoly_type is None:
            if new_monopoly_type == CompetitionType.SinglePlayerMonopoly:
                transition = NewStoreToSinglePlayerMonopolyTransition()
            elif new_monopoly_type == CompetitionType.AbsoluteMonopoly:
                transition = NewStoreToAbsoluteMonopolyTransition()
        elif previous_monopoly_type == CompetitionType.SinglePlayerMonopoly:
            if new_monopoly_type == CompetitionType.HasForeignCompetitors:
                transition = SinglePlayerToForeignCompetitorsTransition()
            elif new_monopoly_type == CompetitionType.AbsoluteMonopoly:
                transition = SinglePlayerToAbsoluteMonopolyTransition()
        elif previous_monopoly_type == CompetitionType.AbsoluteMonopoly:
            if new_monopoly_type == CompetitionType.HasForeignCompetitors:
                transition = AbsoluteToForeignCompetitorsTransition()
            elif new_monopoly_type == CompetitionType.SinglePlayerMonopoly:
                transition = AbsoluteToSingleMonopolyTransition()

        transition.data_repository = data_repository
        return transition


    @classmethod
    def __get_competition_type(cls, away_stores, home_store):
        # if there are away stores, cycle through and see if any are from another company
        if away_stores and len(away_stores) > 0:
            # get count of foreign competitors
            foreign_competitors_length = len(filter(lambda away_store : away_store.company_id != home_store.company_id, away_stores))

            if foreign_competitors_length > 0:
                return CompetitionType.HasForeignCompetitors
            else:
                return CompetitionType.SinglePlayerMonopoly

        # no away stores, must be an absolute monopoly
        else:
            return CompetitionType.AbsoluteMonopoly

