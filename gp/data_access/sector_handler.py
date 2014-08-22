from common.utilities.sql import sql_execute_with_parameters, sql_execute

__author__ = 'spacecowboy'

def save_sector_name_get_id(sector_name):
    statement = '''
                    IF NOT EXISTS
                    (
                        SELECT id FROM sectors WHERE name = ?
                    )
                    BEGIN
                        INSERT INTO sectors (name, created_at, updated_at)
                        VALUES (?, GETUTCDATE(), GETUTCDATE())
                    END

                    SELECT id FROM sectors WHERE name = ?'''

    parameters = [sector_name, sector_name, sector_name]
    row = sql_execute_with_parameters(parameters, statement)[0]

    return row.id