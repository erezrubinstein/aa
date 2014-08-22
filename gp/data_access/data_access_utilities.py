__author__ = 'erezrubinstein'


"""
This module contains various data access utility functions
"""

def comma_delimit_items(items):
    if items and isinstance(items, list):
        return ','.join(str(item) for item in items)

def select_clean_up(item):
    if item is None:
        item = 'IS NULL'
    else:
        item = ''.join(['= ', str(item)])
    return item

def select_clean_up_string(item):
    if item is None:
        item = 'IS NULL'
    else:
        item = ''.join(["= '", escape_string(str(item)), "'"])

    return item

def insert_clean_up(item):
    if item is None:
        item = 'NULL'
    return item

def insert_clean_up_string(item):
    if item is None:
        return 'NULL'
    else:
        return "'%s'" % escape_string(item)

def insert_clean_up_time(item):
    return item[:-3]

def escape_string(item):
    if item and isinstance(item, basestring):
        return item.replace("'", "''")
    else:
        return item


def escape_date_clean_up(date):

    if date:
        return escape_string_clean_up(date.isoformat())
    else:
        return escape_string_clean_up(date)


def escape_string_clean_up(item):

    if item and (type(item) == unicode or type(item) == str):
        item = item.replace("'", "''")
        return "'%s'" % item
    elif item and (type(item) != unicode or type(item) != str):
        return "'%s'" % item
    elif not item:
        return 'NULL'


