"""
Created on Oct 22, 2012

@author: erezrubinstein
"""
from common.utilities.signal_math import SignalDecimal

class GeographicalCoordinate(object):
    def __init__(self, longitude, latitude, threshold=SignalDecimal(1)):

        self.longitude = SignalDecimal(longitude)
        self.latitude = SignalDecimal(latitude)
        self.threshold = threshold
        self.__wkt_representation = None

    def wkt_representation(self, longitude = None, latitude = None):

        # regardless of whether it's set before or not, the user expects this point back from the arguments
        if longitude is not None and latitude is not None:
            self.__wkt_representation = ''.join(['POINT(', str(longitude), ' ', str(latitude), ')'])
            return self.__wkt_representation

        elif self.__wkt_representation is not None and longitude is None and latitude is None:
            return self.__wkt_representation

        elif self.__wkt_representation is None:
            if self.longitude is not None and self.latitude is not None:
                self.__wkt_representation = ''.join(['POINT(', str(self.longitude), ' ', str(self.latitude), ')'])
                return self.__wkt_representation
            elif self.longitude is None and self.latitude is None:
                raise NotImplementedError('longitude and latitude for this geocoordinate are both None')



    def __get_latitude(self):
        from_latitude = self.latitude - self.threshold
        to_latitude = self.latitude + self.threshold
        
        #latituded stops at 90/-90 degrees and goes back down
        #if we reach that point, normalize it from the -self.threshold to 90/-90
        if to_latitude > 90:
            to_latitude = 90
        elif from_latitude < -90:
            from_latitude = -90
            
        return Range(from_latitude, to_latitude)
    
    def __get_longitude_list(self):
        longitude_ranges = []
        from_longitude = self.longitude - self.threshold
        to_longitude = self.longitude + self.threshold
        
        #longitude becomes negative after 180 (i.e. 179.5 + 1 = -179.5)
        #we also need two checks given that -179.5 to 179.5 encompasses everything.
        if to_longitude > 180:
            longitude_ranges.append(Range(from_longitude, 180))
            longitude_ranges.append(Range(-180, -180 + (to_longitude - 180)))
        elif from_longitude < -180:
            longitude_ranges.append(Range(-180, to_longitude))
            longitude_ranges.append(Range(180 + (from_longitude + 180), 180))
        else:
            longitude_ranges.append(Range(from_longitude, to_longitude))
            
        return longitude_ranges
        
        
    def get_search_limits(self):
        """
        This method looks at the current coordinate and gives
        us a range of lats and longs that are deemed within
        searching distance.

        This method assumes that we only want to search lat longs
        that are within 1 degree
        """
        return {
            "latitudes": self.__get_latitude(),
            "longitudes": self.__get_longitude_list()
        }

    def __eq__(self, other):
        return self.longitude == other.longitude and self.latitude == other.latitude and self.threshold == other.threshold

class Range(object):
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __eq__(self, other):
        return self.start == other.start and self.stop == other.stop



