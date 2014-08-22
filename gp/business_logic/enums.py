__author__ = 'erezrubinstein'

from common.utilities.enum import Enum

class CompetitionType(Enum):
    """
    This represents competition types.  In the db, these are called monopoly_types
    """
    HasForeignCompetitors = 0
    SinglePlayerMonopoly = 1
    AbsoluteMonopoly = 2


class EntityTypeRef(Enum):
    """
    This represents several entities in our database.  It is mostly used for data checks.
    """
    Address = 1
    Store = 2
    Company = 3
    TradeArea = 4
    CompetitiveStore = 5
    Period = 6
    SourceFile = 7
    SourceFileRecord = 8

class FailThreshold(Enum):
    ReverseGeoCodeESRI = 2
    ReverseGeoCodeGoogle = 2

class GridTargetDatabase(Enum):
    MongoDb = 1
    SQL = 2

class TradeAreaThreshold(Enum):
    DistanceMiles10 = 1
    DriveTimeMinutes10 = 2
    LatitudeLongitudeDecimal = 3
    DistanceMiles1 = 4
    DistanceMiles5 = 5
    GridDistanceMiles6 = 6
    GridDistanceMiles10 = 7
    DistanceMiles3 = 8
    DistanceMiles6 = 9
    GridDistanceMiles20 = 10
    GridDistanceMiles4 = 11
    DistanceMiles2 = 12
    DistanceMiles40 = 13
    DistanceMiles20 = 14
    DistanceMilesPoint5 = 15
    DistanceMiles7 = 16
    DistanceMilesPoint25 = 17

class DistanceImpedance(Enum):
    distance_impedance = {
        TradeAreaThreshold.DriveTimeMinutes10: 10,
        TradeAreaThreshold.DistanceMiles10: 10,
        TradeAreaThreshold.DistanceMiles1: 1,
        TradeAreaThreshold.DistanceMiles5: 5,
        TradeAreaThreshold.DistanceMiles3: 3,
        TradeAreaThreshold.DistanceMiles6: 6,
        TradeAreaThreshold.DistanceMiles2: 2,
        TradeAreaThreshold.DistanceMiles20: 20,
        TradeAreaThreshold.DistanceMiles40: 40,
        TradeAreaThreshold.GridDistanceMiles6: 6,
        TradeAreaThreshold.GridDistanceMiles10: 10,
        TradeAreaThreshold.GridDistanceMiles20: 20,
        TradeAreaThreshold.DistanceMilesPoint5: 0.5,
        TradeAreaThreshold.DistanceMiles7: 7,
        TradeAreaThreshold.DistanceMilesPoint25: 0.25
    }

class DataCheckTypeRef(Enum):
    ReverseGeocodeESRI = 1
    ReverseGeocodeGoogle = 22

class HashMatcherFuzziness(Enum):
    Fuzzy = 1
    NotFuzzy = 2

class StoreChangeType(Enum):
    """
    This represents the status of a store that was sent to be inserted into the db
    """
    StoreOpened = 1
    StoreConfirmed = 2
    StoreUpdated = 3
    StoreClosed = 4
    StoreDeleted = 5

class AddressChangeType(Enum):
    """
    This represents the types of changes we can do to address records in the db
    """
    AddressCreated = 1
    AddressChanged = 2
    MismatchAddressIgnored = 3


class FileModes(Enum):
    ReadOnly = 'r'
    Write = 'w'
    Append = 'a'
    ReadAndWrite = 'r+'

class DurationTypes(Enum):
    Year = 1
    HalfYear = 2
    Quarter = 3
    Month = 4
    Day = 5
    PointInTime = 6
    ArbitraryLength = 7

class MasterCompetitionFileColumns(Enum):
    HomeCompany = 0
    AwayCompany = 1
    HomeAwayCompetitionStrength = 2
    AwayHomeCompetitionStrength = 3
    StartDate = 4
    EndDate = 5
