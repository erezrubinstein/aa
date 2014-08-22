from common.utilities.inversion_of_control import Dependency, HasMethods

class TradeArea(object):
    def __init__(self):

        self.trade_area_id = None
        self.store_id = None
        self.threshold_id = None
        self.period_id = None
        self.area = None
        self.__wkt_representation = None
        self.__data_repository = Dependency("DataRepository", HasMethods("insert_trade_area_shape")).value


    @classmethod
    def select_by_id(cls, trade_area_id):
        data_repository = Dependency("DataRepository", HasMethods("get_trade_area_by_id")).value
        return data_repository.get_trade_area_by_id(trade_area_id)


    @classmethod
    def standard_init(cls, trade_area_id, store_id, created_at, updated_at, threshold_id):
        trade_area = TradeArea()
        trade_area.trade_area_id = trade_area_id
        trade_area.store_id = store_id
        trade_area.created_at = created_at
        trade_area.updated_at = updated_at
        trade_area.threshold_id = threshold_id
        return trade_area


    def wkt_representation(self, wkt_representation = None):

        # regardless if the reprentation is set or not, the user is expecting the argument linestring back
        if wkt_representation is not None:
            self.__wkt_representation = wkt_representation
            return self.__wkt_representation

        if self.__wkt_representation is not None:
            return self.__wkt_representation

        elif self.__wkt_representation is None:
            if self.trade_area_id is None:
                raise NotImplementedError('There is no trade area id or preloaded wkt_representation')
            else:

                self.__wkt_representation = self.__data_repository.select_trade_area_shape_by_id(self.trade_area_id)
                return self.__wkt_representation

class TradeAreaOverlap(object):
    def __init__(self):
        self.home_trade_area_id = None
        self.away_trade_area_id = None
        self.overlap_area = None


