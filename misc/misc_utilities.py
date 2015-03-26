from core.common.utilities.errors import InputError
from core.common.utilities.helpers import ensure_id


__author__ = 'erezrubinstein'


def convert_entity_list_to_dictionary(items, key="_id", to_str=False):
    """
    Take a list and convert it to a dictionary
    """
    if isinstance(key, basestring) or isinstance(key, int):
        if to_str:
            return { str(item[key]): item for item in items}
        else:
            return { item[key]: item for item in items}

    # assume it's a function
    elif items:
        if to_str:
            return { str(key(item)): item for item in items }
        else:
            return { key(item): item for item in items }

    else:
        return {}

def convert_entity_list_to_dictionary_of_lists(items, key = "_id"):
    """
    Take a list that has duplicate keys and convert it into a dictionary of lists
    """

    dictionary = {}

    if items:
        for item in items:

            # get dict key
            if isinstance(key, basestring) or isinstance(key, int):
                dict_key = item[key]
            else:
                # if key is not a string, assume it's a function
                dict_key = key(item)

            # add key to dict as an array
            if dict_key not in dictionary:
                dictionary[dict_key] = []

            # add item to list
            dictionary[dict_key].append(item)

    return dictionary


def convert_entity_list_to_dictionary__array_format(items, column_index = 0):
    """
    This is very helpful when comparing items that could potentially return in different order
    """
    return { item[column_index]: item for item in items}


def split_up_list_into_smaller_partitions(items, partition_size):
    """
    break up a large list into a list of lists each containing the partition size number of items
    """
    current_index = 0
    parsed_records_list = []
    while current_index < len(items):
        # figure out end index of the range
        if len(items) - current_index >= partition_size:
            end_index = current_index + partition_size
        else:
            end_index = len(items)

        # add range to list and move the current index
        parsed_records_list.append(items[current_index:end_index])
        current_index = end_index

    return parsed_records_list


def process_input_query(input_query):

   return process_input_query_with_keys(input_query, ["_id"])

def process_input_query_with_keys(input_query, query_keys):

    # make sure to transform ids to ObjectIds
    for query_key in query_keys:
        if query_key in input_query:

            # Dict in key query_key
            if isinstance(input_query[query_key], dict):
                key = input_query[query_key].keys()[0]

                if isinstance(input_query[query_key][key], list):
                    input_query[query_key][key] = [ensure_id(oid) for oid in input_query[query_key][key]]

                elif isinstance(input_query[query_key][key], dict):
                    key2 = input_query[query_key][key].keys()[0]

                    if isinstance(input_query[query_key][key][key2], list):
                        input_query[query_key][key][key2] = [ensure_id(oid) for oid in input_query[query_key][key][key2]]

                    elif isinstance(input_query[query_key][key][key2], dict):
                        raise InputError("MDS queries do not support double-nested dicts for '_id' key in query %s" % input_query)

                    else:
                        input_query[query_key][key][key2] = ensure_id(input_query[query_key][key][key2])

                else:
                    input_query[query_key][key] = ensure_id(input_query[query_key][key])

            else:
                input_query[query_key] = ensure_id(input_query[query_key])

    return input_query



def multi_key_sort(items, columns):
    """
    Sorts a list of dicts by multiple keys
    http://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys
    Usage:
    results = multi_key_sort(list_of_dicts, ['col1', '-col2']
        where col1 is sorted in ascending and then col2 in descending
    """
    from operator import itemgetter
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)


class DataAccessNamedRow(object):
    """
    Class that can be initialized with dynamic members
    """
    def __init__(self, **args):
        self.__dict__.update(args)


def safe_len(items, default=0):
    """
    Return len(items) if possible, else return default
    """
    try:
        if hasattr(items, "__len__"):
            return len(items)
        else:
            return default
    except:
        return default


def get_splits(ids, n):
    """
    given a list of items, return a generator of tuples corresponding to the start and end items, when split into n chunks.
    example: ids=[1,2,3,4,5,6], n=2 --> (1,3) (4,6)
    """

    ids = sorted(list(ids))
    split_size = int(len(ids) / n)

    for s in xrange(0, n - 1):
        start = s * split_size
        end = s * split_size + split_size - 1
        yield (ids[start], ids[end])

    # get the last split
    yield (ids[(n - 1) * split_size], ids[-1])