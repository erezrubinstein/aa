from common.utilities.date_utilities import get_datetime_months_ago, LAST_ECONOMICS_DATE, ECONOMICS_START_DATE, get_start_date_of_next_month


def create_trade_area(ta_id, cid, unemployment=0, employment=0, labor_force=0, unemployment_rate=0,
                      state="NY", store_opened_date=None, store_closed_date=None, override_length=None,
                      timeseries_offset=0):
    start_date = store_opened_date or ECONOMICS_START_DATE
    end_date = store_closed_date or get_start_date_of_next_month(LAST_ECONOMICS_DATE)

    return {
        "_id": ta_id,
        "interval": [None, None],
        "data": {
            "company_id": str(cid),
            "store_opened_date": store_opened_date,
            "store_closed_date": store_closed_date,
            "state": state,
            "zip": "11111",
            "analytics": {
                "economics": {
                    "area_text": "blah blah blah NY",
                    "monthly": {
                        # Last value should be for the month before end_date
                        "unemployment": create_time_series(get_datetime_months_ago(1, start=end_date), start_date,
                                                           unemployment, timeseries_offset, override_length),
                        "employment": create_time_series(get_datetime_months_ago(1, start=end_date), start_date,
                                                         employment, timeseries_offset, override_length),
                        "labor force": create_time_series(get_datetime_months_ago(1, start=end_date), start_date,
                                                          labor_force, timeseries_offset, override_length),
                        "unemployment rate": create_time_series(get_datetime_months_ago(1, start=end_date), start_date,
                                                                unemployment_rate, timeseries_offset, override_length)
                    }
                }
            }
        }
    }


def create_time_series(newest_date, oldest_date, value, timeseries_offset=0, override_length=None):
    series = []
    current_date = newest_date
    i = 0
    a = 0

    while current_date >= oldest_date:
        if a >= timeseries_offset:
            series.append({
                "date": current_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "value": value
            })

        a += 1
        i += 1
        current_date = get_datetime_months_ago(1, start=current_date)

        if override_length is not None and i == override_length:
            break

    return series
