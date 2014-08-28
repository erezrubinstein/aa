import pprint
from common.service_access.utilities.json_helpers import APIEncoder_New, APIEncoder
from core.common.business_logic.service_entity_logic.weather_helper import upsert_new_weather_data
from core.common.utilities.helpers import ensure_id
from geoprocessing.business_logic.business_objects.geographical_coordinate import GeographicalCoordinate
from core.common.business_logic.service_entity_logic.store_helper import StoreHelper
from core.common.business_logic.service_entity_logic.rir_helper import return_rir_entity_rec
from common.service_access.utilities.rec_helpers import upsert_rec
from common.utilities.inversion_of_control import Dependency
from common.utilities.date_utilities import parse_date, normalize_end_date, normalize_start_date, ANALYTICS_TARGET_YEAR
from common.utilities.misc_utilities import DataAccessNamedRow
from datetime import datetime


# ------------------------------------------------ Insert ------------------------------------------------ #

def insert_test_weather(date="2013-11-07", weather_code="weather_station", temp_metric=10, temp_us=20,
                        precip_metric=1, precip_us=2):

    weather_data = {
        "date": parse_date(date),
        "precip_in": precip_us,
        "precip_mm": precip_metric,
        "temp_c_min": 10.0000,
        "temp_c_max": 20.0000,
        "temp_c_mean": temp_metric,
        "temp_f_min": 50.0000,
        "temp_f_max": 68.0000,
        "temp_f_mean": temp_us
    }

    upsert_new_weather_data([weather_data], weather_code)


def insert_test_weather_station_mongo(code, name, psql_id, lat, lng, state = "NY"):

    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # create data
    data = {
        "code": code,
        "longitude": lng,
        "latitude": lat,
        "psql_id": psql_id,
        "state": state
    }

    # bombaj for
    return core_api_provider.mds.call_add_entity("weather_station", name, data, context)


def insert_test_zip(zip_code, longitude, latitude):

    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # create data
    data = {
        "zip_code": zip_code,
        "longitude": longitude,
        "latitude": latitude
    }

    # bombaj for
    return core_api_provider.mds.call_add_entity("zip_code", zip_code, data, context)


def insert_test_file(name, data, use_new_json_encoder=False):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value
    
    if use_new_json_encoder:
        json_encoder = APIEncoder_New
    else:
        json_encoder = APIEncoder

    return core_api_provider.mds.call_add_entity('file', name=name, data=data, context_rec=context, json_encoder=json_encoder)


def insert_test_company(ticker='', name='UNITTESTCOMPANY', ctype="retail_parent", workflow_status=None, valid_status=None,
                        analytics_status = None, company_status = "operating", use_new_json_encoder=False, **kwargs):

    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # create data
    data = {
        "ticker": ticker,
        "type": ctype,
        "status": company_status
    }

    # only add workflow status if it's  passed in
    if workflow_status:
        data["workflow"] = {
            "current": {
                "status": workflow_status
            }
        }

    # only add analytics status, if it's passed in
    if analytics_status:

        # get the workflow data in a way that deals with new stuff and doesn't override the workflow status, above.
        workflow = data.get("workflow", {})

        # set analytics
        workflow["analytics"] = analytics_status

        # set workflow back
        data["workflow"] = workflow

    # only add valid section if it's there
    if valid_status:
        data["valid"] = valid_status

    data = upsert_rec(data, kwargs)

    # bomboj for
    if use_new_json_encoder:
        return core_api_provider.mds.call_add_entity("company", name, data, context, json_encoder=APIEncoder_New)
    else:
        return core_api_provider.mds.call_add_entity("company", name, data, context)


def insert_test_industry(name='UNITTESTINDUSTRY', data=None):

    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    if not data:
        data = {"chicken": "woot"}

    # bomboj for
    return core_api_provider.mds.call_add_entity("industry", name, data, context)


def insert_test_industry_competition(industry_id1, industry_id2):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_link("industry", industry_id1, "competitor", "industry",
                                               industry_id2, "competitor", "industry_competition", context,
                                               link_data={"home_to_away":{"weight": .9}, "away_to_home": {"weight": .8}})


def insert_test_competitor(home_company_id, away_company_id, strength = 1, assumed_start_date = None, assumed_end_date = None):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # create data
    data = { "competition_strength": strength }

    # bomboj for
    return core_api_provider.mds.call_add_link("company", home_company_id, "competitor", "company", away_company_id, "competitor", "company_competition", context)


def insert_test_company_competition_instance(from_company_id, to_company_id, pair_data_from_to=None, pair_data_to_from=None, to_industry_id=None):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    pairs_to_create = [{
        "from_id": from_company_id,
        "to_id": to_company_id,
        "pair_data_from_to": pair_data_from_to,
        "pair_data_to_from": pair_data_to_from,
        "pair_interval_from_to": [None, None],
        "pair_interval_to_from": [None, None],
        "to_industry_id": to_industry_id
    }]

    return core_api_provider.mds.call_create_pair_entities(pairs_to_create, "company", "competitor", "company",
                                                           "competitor", "company_competition", context,
                                                           timeout=1000)

def insert_test_cci(from_company_id, to_company_id, **kwargs):
    """
    Insert barebones cci.  If you want to update any parts, just send in through kwargs.
    Don't use this function for new code... use insert_test_company_competition_instance above instead
    """
    data = {
        "from": {
            "interval": [],
            "data": {
                "status": "operating",
                "type": "retail_banner",
                "ticker": ""
            },
            "name": "Company"
        },
        "to": {
            "interval": [],
            "data": {
                "status": "operating",
                "type": "retail_banner",
                "ticker": ""
            },
            "name": "Company"
        },
        "sync": {
            "last_synced": None
        },
        "to_links": {
            "industry": {},
            "company": {}
        },
        "pair": {
            "entity_type_from": "company",
            "entity_id_from": from_company_id,
            "entity_type_to": "company",
            "entity_role_to": "competitor",
            "entity_role_from": "competitor",
            "entity_id_to": to_company_id,
            "interval": [None, None],
            "data": {
                "competition_strength": 1
            },
            "relation_type": "company_competition"
        },
        "from_links": {
            "industry": {},
            "company": {}
        }
    }

    # Add any additional kwargs
    upsert_rec(data, kwargs)

    # insert
    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("company_competition_instance", "test_cci", data, context)


def create_store_with_rir(company_id, latitude = 1, longitude = -1, as_of_date = None, as_of_date_is_opened_date = False, phone = '555-867-5309'):

    # create rir first
    rir_id = insert_test_rir(context, company_id, latitude = latitude, longitude = longitude, as_of_date = as_of_date, as_of_date_is_opened_date = as_of_date_is_opened_date,
                             phone = phone)

    # create store helper and insert store
    store_helper = StoreHelper()
    return store_helper.create_new_store(context, rir_id, async=False)

def insert_test_store(company_id, interval, use_new_json_encoder=False, **kwargs):

    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value
    data = {'company_id': company_id}

    # Add any additional kwargs
    upsert_rec(data, kwargs)

    if use_new_json_encoder:
        json_encoder = APIEncoder_New
    else:
        json_encoder = APIEncoder

    # bomboj for
    return core_api_provider.mds.call_add_entity('store', 'store', data, context, interval=interval, json_encoder=json_encoder)


def insert_test_address(longitude, latitude, street_number = 0, street = 'UNITTEST', city = 'UNITTEST', state = 'NY', zip_code = 11111,
                        suite = "woot", shopping_center = "chicken", company_id = 1):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # create data
    data = {
        "street_number": street_number,
        "street": street,
        "city": city,
        "state": state,
        "zip": zip_code,
        "suite": suite,
        "shopping_center": shopping_center,
        "longitude": longitude,
        "latitude": latitude,
        "country": "USA",
        "company_ids": [company_id]
    }

    # bomboj for
    return core_api_provider.mds.call_add_entity("address", "address", data, context)


def insert_test_store_deprecated(company_id = None, address_id = None, opened_date = None, closed_date = None, assumed_opened_date = None, assumed_closed_date = None, phone_number = '(000) 000-0000',
                      store_format = "", company_generated_store_number = "", note = ""):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # normalize dates
    opened_date = normalize_start_date(opened_date)
    assumed_opened_date = normalize_start_date(assumed_opened_date)
    assumed_closed_date = normalize_end_date(assumed_closed_date)
    assumed_closed_date = normalize_end_date(assumed_closed_date)

    # create data
    data = {
        "phone_number": phone_number,
        "store_format": store_format,
        "store_number": company_generated_store_number,
        "note": note,
        "opened_date": __clean_up_date_for_api(opened_date),
        "closed_date": __clean_up_date_for_api(closed_date),
        "assumed_opened_date": __clean_up_date_for_api(assumed_opened_date),
        "assumed_closed_date": __clean_up_date_for_api(assumed_closed_date),
    }

    # bomboj for
    store_id = core_api_provider.mds.call_add_entity("store", "store", data, context)

    if company_id:
        # create company to store link
        core_api_provider.mds.call_add_link("company", company_id, "retail_parent", "store", store_id, "store", "store_ownership", context)

    if address_id:
        # create store to address
        core_api_provider.mds.call_add_link("store", store_id, "subject", "address", address_id, "location", "address_assignment", context)

    return store_id


def insert_test_problem_address(address_id, longitude, latitude):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # create value
    value = {
        "longitude": longitude,
        "latitude": latitude
    }

    # bomboj for
    core_api_provider.mds.call_update_entity("address", address_id, context, "data.problem_address_coordinates", value)


def insert_test_rir(context, company_id, id_incrementer='', as_of_date=None, company_name='UNITTEST_COMPANY',
                    address='123 Main St', city='UNIT_TEST_VILLE', state='UT', zip_code='12345',
                    phone='555-867-5309', longitude=-80.1, latitude=40.0, as_of_date_is_opened_date=False, **kwargs):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    if not as_of_date:
        as_of_date = datetime.utcnow()

    rir_rec = return_rir_entity_rec(
        company_id=company_id,
        company_name=company_name,
        as_of_date=as_of_date,
        address=address + id_incrementer,
        city=city + id_incrementer,
        state=state,
        zip_code=zip_code,
        phone=phone,
        longitude=longitude,
        latitude=latitude,
        country='',
        mall_name='UNIT_TEST_MALL' + id_incrementer,
        suite='',
        store_number='UNIT_TEST_STORE_NUM' + id_incrementer,
        store_format='UNIT_TEST_STORE_FORMAT',
        note='IM A UNIT TEST',
        store_url='',
        reason='',
        reason_source='',
        flagged_for_review=False,
        review_comments='',
        source_type='UNIT_TEST',
        source_name='UNIT_TEST' + id_incrementer,
        source_id='UNIT_TEST' + id_incrementer,
        as_of_date_is_opened_date=as_of_date_is_opened_date)
    rir_rec['name'] = 'UNIT_TEST_RIR'
    rir_rec['data']['auto_parsed_address'] = {
        'city': rir_rec['data']['city'],
        'zip': rir_rec['data']['zip'],
        'street_number': '123',
        'longitude': rir_rec['data']['geo'][0],
        'state': rir_rec['data']['state'],
        'street': 'Main St',
        'latitude': rir_rec['data']['geo'][1],
        'suite': rir_rec['data']['suite'],
        'geo': [rir_rec['data']['geo'][0], rir_rec['data']['geo'][1]],
        'country': rir_rec['data']['country'],
        'shopping_center': rir_rec['data']['mall_name'],
    }

    upsert_rec(rir_rec["data"], kwargs)

    # bomboj for
    return core_api_provider.mds.call_add_entity_rec(rir_rec, context)


def insert_test_trade_area(store_id=1, company_id=1, company_name="woot", opened_date=None, closed_date=None,
                           longitude=1, latitude=1, competitive_stores=None, monopolies=None,
                           dem_total_population=142695, dem_total_households=5000, per_capita_income=5000,
                           aggregate_income=999999999, city="city", state="state", **kwargs):
    data = {
        "sql_store_id": "",
        "sql_trade_area_id": "",
        "sql_database": "",

        # core
        "store_id": store_id,
        "company_name": company_name,
        "store_opened_date": opened_date,
        "store_closed_date": closed_date,
        "company_id": company_id,

        # trade area stuff
        "trade_area_threshold": "DistanceMiles10",
        "period_duration": "year",
        "period_start_date": datetime(2011, 1, 1),
        "period_end_date": datetime(2012, 1, 1),

        # store/address details
        "phone": "phone",
        "street_number": "street_number",
        "street": "street",
        "city": city,
        "state": state,
        "suite": "suite",
        "shopping_center": "shopping_center",
        "zip": "zip",
        "longitude": longitude,
        "latitude": latitude,
        "phone_number": 111,

        # demographics
        "demographics": {
            "TOTPOP_CY": {
                "description": "test",
                "value": dem_total_population,
                "target_year": ANALYTICS_TARGET_YEAR
            },
            "PCI_CY": {
                "description": "test",
                "value": per_capita_income,
                "target_year": ANALYTICS_TARGET_YEAR
            },
            "TOTHH_CY": {
                "description" : "test",
                "value" : dem_total_households,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC0_CY": {
                "description" : "test",
                "value" : 6000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC15_CY": {
                "description" : "test",
                "value" : 7000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC25_CY": {
                "description" : "test",
                "value" : 8000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC35_CY": {
                "description" : "test",
                "value" : 9000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC50_CY": {
                "description" : "test",
                "value" : 10000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC75_CY": {
                "description" : "test",
                "value" : 11000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC100_CY": {
                "description" : "test",
                "value" : 12000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC150_CY": {
                "description" : "test",
                "value" : 13000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC200_CY":{
                "description" : "test",
                "value" : 14000,
                "target_year" : ANALYTICS_TARGET_YEAR
            }
        },

        # analytics
        "analytics": {
            "AGG_INCOME_CY": {
                "description": "test",
                "value": aggregate_income,
                "target_year": ANALYTICS_TARGET_YEAR
            }
        }
    }

    interval = None
    if opened_date or closed_date:
        interval = [opened_date, closed_date]

    # add competitive stores, if included
    if competitive_stores:
        data["competitive_stores"] = competitive_stores

    # add monopolies, if included
    if type(monopolies) is list:
        data["monopolies"] = monopolies

    # Add any additional kwargs
    upsert_rec(data, kwargs)

    # bomboj for
    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("trade_area", "trade_area", data, context, interval = interval)


def insert_test_geoprocessed_trade_area(home_store_id, away_store_id, company_id = 1, company_name = "woot", opened_date = None,
                                      closed_date = None,longitude = 1, latitude = 1, competitive_stores = None,
                                      monopolies = None,dem_total_population = 142695, dem_total_income = 5000, shape_array = None, **kwargs):

    if not shape_array:
        shape_array = [
            [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
            [[0.25, 0.25], [0.25, 0.5], [0.5, 0.5], [0.5, 0.25], [0.25, 0.25]]
        ]

    data = {
        "sql_store_id": "",
        "sql_trade_area_id": "",
        "sql_database": "",

        # core
        "store_id": home_store_id,
        "company_name": company_name,
        "store_opened_date": opened_date,
        "store_closed_date": closed_date,
        "company_id": company_id,

        # trade area stuff
        "trade_area_threshold": "DistanceMiles10",

        # store/address details
        "phone": "phone",
        "street_number": "street_number",
        "street": "street",
        "city": "city",
        "state": "state",
        "suite": "suite",
        "shopping_center": "shopping_center",
        "zip": "zip",
        "longitude": longitude,
        "latitude": latitude,
        "phone_number": 111,
        "competitive_stores": [
            { "away_company_id" : company_id, "end_date" : "3000-01-01T00:00:00" ,
              "start_date" : "1900-01-01T00:00:00" , "weight" : 1.0, "away_store_id" : away_store_id
            }
        ],
        "geo": [ longitude, latitude],
        # demographics
        "demographics": {
            "TOTPOP_CY": {
                "description": "test",
                "value": dem_total_population,
                "target_year": ANALYTICS_TARGET_YEAR
            },
            "PCI_CY": {
                "description": "test",
                "value": 25644,
                "target_year": ANALYTICS_TARGET_YEAR
            },
            "TOTHH_CY": {
                "description" : "test",
                "value" : dem_total_income,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC0_CY": {
                "description" : "test",
                "value" : 6000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC15_CY": {
                "description" : "test",
                "value" : 7000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC25_CY": {
                "description" : "test",
                "value" : 8000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC35_CY": {
                "description" : "test",
                "value" : 9000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC50_CY": {
                "description" : "test",
                "value" : 10000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC75_CY": {
                "description" : "test",
                "value" : 11000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC100_CY": {
                "description" : "test",
                "value" : 12000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC150_CY": {
                "description" : "test",
                "value" : 13000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
            "HINC200_CY":{
                "description" : "test",
                "value" : 14000,
                "target_year" : ANALYTICS_TARGET_YEAR
            },
        },

        # analytics
        "analytics": {
            "shape": {
                "UTM_Zone": "12N",
                "surface_area": 123456789,
                "centroid": {
                    "latitude": 11,
                    "longitude": 22
                },
                "shape_array": shape_array
            }
        }
    }

    interval = None
    if opened_date or closed_date:
        interval = [opened_date, closed_date]

    # add competitive stores, if included
    if competitive_stores:
        data["competitive_stores"] = competitive_stores

    # add monopolies, if included
    if monopolies:
        data["monopolies"] = monopolies

    # Add any additional kwargs
    upsert_rec(data, kwargs)

    # bomboj for
    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("trade_area", "trade_area", data, context, interval = interval)


def insert_test_white_space_cell_match(company_id, store_count, cell_id = "cell_id", grid_id = "grid_id", grid_name = "grid_name", threshold = "threshold", has_openings = False):

    name = "Vanilla Ice"
    data = {
		"company_id" : company_id,
		"store_count" : store_count,
        "cell_id" : cell_id,
		"grid_id" : grid_id,
		"grid_name" : grid_name,
		"has_openings" : has_openings,
		"threshold" : threshold
    }

    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("white_space_grid_cell_match", name, data, context)


def insert_test_company_analytics(company_id, date, engine="demographics", threshold="DistanceMiles10",
                                  target_year=ANALYTICS_TARGET_YEAR, analytics=None):

    name = "Analytics Data for Company ID %s" % company_id
    data = {
        "company_id": str(company_id),
        "engine": engine,
        "threshold": threshold,
        "target_year": target_year,
        "date": date,
        "analytics": {}
    }

    if analytics:
        data["analytics"] = analytics

    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("company_analytics", name, data, context)


def insert_test_white_space_grid(threshold = "GridDistanceMiles10", name = "10 Mile Squares"):

    # create grid document
    grid_data = {
        "threshold": threshold
    }

    # bomboj for!
    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("white_space_grid", name, grid_data, context)


def insert_test_white_space_grid_cell(grid_id, polygon_coordinates, threshold = "GridDistanceMiles10", grid_name = "10 Mile Squares",
                                      centroid_longitude = -1, centroid_latitude = 1, total_population = 12, agg_income = 13):

    # create cell document
    cell_data = {
        "grid_id": grid_id,
        "grid_name": grid_name,
        "threshold": threshold,
        "analytics": {
            "shape": {
                "shape_array": {
                    "type": "Polygon",
                    "coordinates": polygon_coordinates
                },
                "centroid": {
                    "type": "Point",
                    "coordinates": [centroid_longitude, centroid_latitude]
                }
            },
			"AGG_INCOME_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "AGG_INCOME_CY",
				"value" : agg_income
			}
        },
        "demographics" : {
			"HINC0_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC0_CY",
				"value" : 1
			},
			"HINC100_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC100_CY",
				"value" : 2
			},
			"HINC150_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC150_CY",
				"value" : 3
			},
			"HINC15_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC15_CY",
				"value" : 4
			},
			"HINC200_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC200_CY",
				"value" : 5
			},
			"HINC25_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC25_CY",
				"value" : 6
			},
			"HINC35_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC35_CY",
				"value" : 7
			},
			"HINC50_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC50_CY",
				"value" : 8
			},
			"HINC75_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "HINC75_CY",
				"value" : 9
			},
			"PCI_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "PCI_CY",
				"value" : 10
			},
			"TOTHH_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "TOTHH_CY",
				"value" : 11
			},
			"TOTPOP_CY" : {
				"target_year" : ANALYTICS_TARGET_YEAR,
				"description" : "TOTPOP_CY",
				"value" : total_population
			},
            "FEMALES_CY" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "FEMALES_CY",
                "value" : 13
            },
            "FEMALE_15PLUS" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "FEMALE_15PLUS",
                "value" : 14
            },
            "HINC_100KPLUS" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "HINC_100KPLUS",
                "value" : 15
            },
            "HINC_35KTO75K" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "HINC_35KTO75K",
                "value" : 16
            },
            "HINC_50KPLUS_CY" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "HINC_50KPLUS_CY",
                "value" : 17
            },
            "HINC_LESSTHAN35K" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "HINC_LESSTHAN35K",
                "value" : 18
            },
            "HINC_LESSTHAN50K" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "HINC_LESSTHAN50K",
                "value" : 19
            },
            "MALES_CY" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "MALES_CY",
                "value" : 20
            },
            "MEDHINC_CY" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "MEDHINC_CY",
                "value" : 21
            },
            "TOTHH_FY" : {
                "target_year" : ANALYTICS_TARGET_YEAR,
                "description" : "TOTHH_FY",
                "value" : 23
            }

            # !!! this is commented out on purpose.  To make sure plan B is backwards compatible.
            # !!! In other words, it doesn't fail when a cell is missing a demographic
            #"TOTPOP_FY" : {
            #    "target_year" : ANALYTICS_TARGET_YEAR,
            #    "description" : "TOTPOP_FY",
            #    "value" : 24
            #},

		}
    }

    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("white_space_grid_cell", "test_grid_cell", cell_data, context)


def insert_test_retailer_customer(retailer_client_id, customer_id, age=None, gender="F"):
    # keeping this minimal now, we can add data fields later when the need arises
    data = {
        "retailer_client_id": retailer_client_id,
        "customer_id": customer_id,
        "age": age,
        "gender": gender
    }

    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("retailer_customer", "test_retailer_customer",
                                                 data, context, json_encoder=APIEncoder_New)


def insert_test_retailer_transaction(retailer_client_id, customer_id, sales, transaction_date,
                                     store_id="sid", transaction_id="trx_id", mds_file_id="mds_file_id"):
    # keeping this minimal now, we can add data fields later when the need arises
    data = {
        "retailer_client_id": retailer_client_id,
        "customer_id": customer_id,
        "sales": sales,
        "transaction_date": transaction_date,
        "store_id": store_id,
        "transaction_id": transaction_id,
        "mds_file_id": mds_file_id
    }

    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("retailer_transaction", "test_retailer_transaction",
                                                 data, context, json_encoder=APIEncoder_New)


def insert_test_retailer_store(retailer_client_id, store_id):
    # keeping this minimal now, we can add data fields later when the need arises
    data = {
        "retailer_client_id": retailer_client_id,
        "store_id": store_id
    }

    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("retailer_store", "test_retailer_store",
                                                 data, context, json_encoder=APIEncoder_New)


def insert_test_retailer_file(retailer_client_id, as_of_date=None):
    # keeping this minimal now, we can add data fields later when the need arises
    if not as_of_date:
        as_of_date = datetime.utcnow()
    data = {
        "retailer_client_id": retailer_client_id,
        "as_of_date": as_of_date
    }

    core_api_provider = Dependency("CoreAPIProvider").value
    return core_api_provider.mds.call_add_entity("retailer_file", "test_retailer_file",
                                                 data, context, json_encoder=APIEncoder_New)

# ------------------------------------------------ Select ------------------------------------------------ #


def select_surface_area_by_trade_area_id(trade_area_id, period):
    # run query
    core_api_provider = Dependency("CoreAPIProvider").value
    analytics = core_api_provider.mds.call_get_entity("trade_area", trade_area_id)["data"]["analytics"]

    # find the matching analytics
    period_json = period.json()
    matching_analytics = None
    for analytics_set in analytics:
        if analytics_set["start_date"] == period_json["start_date"] and analytics_set["end_date"] == period_json["end_date"] and analytics_set["duration_type"] == period_json["duration_type"]:
            matching_analytics = analytics_set
            break

    return matching_analytics["items"]["no_target_year"]["surface_area"]["value"]


def select_count_trade_area_by_store(store_id):
    # get dependencies
    core_api_provider = Dependency("CoreAPIProvider").value
    param_builder = Dependency("CoreAPIParamsBuilder").value

    # create params
    filters = { "link.relation_type": "store_trade_area" }
    params = param_builder.create_get_data_entities_params(field_filters = filters)["params"]

    # run query and return first id
    return len(core_api_provider.call_get_data_entities_linked_from("trade_area", "store", store_id, params)["rows"])


def select_monopolies(trade_area_id):
    # run query
    core_api_provider = Dependency("CoreAPIProvider").value
    monopolies = core_api_provider.mds.call_get_entity("trade_area", trade_area_id)["data"]["monopolies"]

    # parse date strings into dates
    for monopoly in monopolies:
        monopoly["start_date"] = parse_date(monopoly["start_date"])
        monopoly["end_date"] = parse_date(monopoly["end_date"])

    return monopolies


def select_competitive_stores(trade_area_id):
    # select the entire trade area entity.
    # this is a work around because the existing link queries don't select the "data" section of the link with them
    core_api_provider = Dependency("CoreAPIProvider").value
    links = core_api_provider.mds.call_get_entity("trade_area", trade_area_id)["links"]

    # create objects that you can reference by name (i.e. obj.away_store_id)
    away_stores = []
    if "store" in links and "store_trade_area_competition" in links["store"]:
        for link in links["store"]["store_trade_area_competition"]:
            # make sure to account for no interval (i.e. none - none)
            start_date = None
            end_date = None
            if link["interval"]:
                start_date = parse_date(link["interval"][0])
                end_date = parse_date(link["interval"][1])

            # add named row object
            away_stores.append(DataAccessNamedRow(trade_area_id = link["entity_id_from"], away_store_id = link["entity_id_to"], travel_time = link["data"]["travel_time"],
                                                  start_date = start_date, end_date = end_date))

    return away_stores


def select_test_problem_long_lat(problem_address_id):
    # get address
    core_api_provider = Dependency("CoreAPIProvider").value
    data = core_api_provider.mds.call_get_entity("address", problem_address_id)["data"]

    return GeographicalCoordinate(data["problem_address_coordinates"]["longitude"], data["problem_address_coordinates"]["latitude"])


def select_trade_area_overlap(home_trade_area_id, away_trade_area_id):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # query and return fits overlap
    overlap_link = core_api_provider.mds.call_get_links("trade_area", home_trade_area_id, "home_trade_area", "trade_area", away_trade_area_id, "away_trade_area", "trade_area_competition")[0]
    return overlap_link["data"]["overlap_surface_area"]


def select_trade_area(trade_area_id):

    # get dependency
    main_access = Dependency("CoreAPIProvider").value
    main_params = Dependency("CoreAPIParamsBuilder").value

    # create params
    query = { '_id': ensure_id(trade_area_id) }
    entity_fields = ["_id", "data"]
    params = main_params.mds.create_params(resource='find_entities_raw', query=query, entity_fields=entity_fields)['params']

    # run query and return
    return main_access.mds.call_find_entities_raw('trade_area', params, context, encode_and_decode_results=False)[0]


def select_test_store(store_id):

    # get dependency
    main_access = Dependency("CoreAPIProvider").value
    main_params = Dependency("CoreAPIParamsBuilder").value

    # create params
    query = { '_id': ensure_id(store_id) }
    entity_fields = ["_id", "data"]
    params = main_params.mds.create_params(resource='find_entities_raw', query=query, entity_fields=entity_fields)['params']

    # run query nad return
    return main_access.mds.call_find_entities_raw('store', params, context, encode_and_decode_results=False)[0]


def select_all_white_space_grid_cell_matches():

    # get dependency
    main_access = Dependency("CoreAPIProvider").value
    main_params = Dependency("CoreAPIParamsBuilder").value

    # create params
    entity_fields = ["_id", "data"]
    params = main_params.mds.create_params(resource = 'find_entities_raw', entity_fields = entity_fields)['params']

    # run query nad return
    return main_access.mds.call_find_entities_raw('white_space_grid_cell_match', params, context)

# ------------------------------------------------ Delete ------------------------------------------------ #


def delete_test_competitors(company_id):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value
    param_builder = Dependency("CoreAPIParamsBuilder").value

    # create params
    filters = {
        "link.relation_type": "company_competition"
    }
    params = param_builder.create_get_data_entities_params(field_filters = filters)["params"]

    # get links
    links = core_api_provider.call_get_data_entities_linked_from("company", "company", company_id, params)["rows"]

    # delete links
    for link in links:

        # bomboj for
        core_api_provider.mds.call_del_link_without_id("company", company_id, "competitor", "company", link["to._id"], "competitor", "company_competition")


def delete_test_address(address_id):
    # bomboj for
    core_api_provider = Dependency("CoreAPIProvider").value
    core_api_provider.mds.call_del_entity("address", address_id)


def delete_test_trade_area(trade_area_id):
    # bomboj for
    core_api_provider = Dependency("CoreAPIProvider").value
    core_api_provider.mds.call_del_entity("trade_area", trade_area_id, error_if_absent=False)


def delete_test_store(store_id):
    # sending in a fake context, creating it here for backwards compatibility
    context = {
        "source": "INTEGRATION_TEST",
        "user_id": "INTEGRATION_TEST"
    }
    StoreHelper().delete_store_by_id(context, store_id)


def delete_test_company(company_id):
    # bomboj for
    core_api_provider = Dependency("CoreAPIProvider").value
    core_api_provider.mds.call_del_entity("company", company_id)


def delete_competitive_stores(trade_area_id):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value
    param_builder = Dependency("CoreAPIParamsBuilder").value

    # create params
    filters = { "link.relation_type": "store_trade_area_competition" }
    params = param_builder.create_get_data_entities_params(field_filters = filters)["params"]

    # get links and store_ids
    links = core_api_provider.call_get_data_entities_linked_from("store", "trade_area", trade_area_id, params)["rows"]

    # for each store, delete link
    for link in links:

        # bomboj for
        core_api_provider.mds.call_del_link_without_id("store", link["to._id"], "away_store", "trade_area", trade_area_id, "trade_area", "store_trade_area_competition")


def delete_monopolies(trade_area_id):
    # get dependency
    core_api_provider = Dependency("CoreAPIProvider").value

    # create context
    context = {
        "source": "Geoprocessing integration test",
        "user_id": None
    }

    # bomboj for
    core_api_provider.mds.call_update_entity("trade_area", trade_area_id, context, "data.monopolies", [])


def delete_test_sector(sector_id):
    # bomboj for
    core_api_provider = Dependency("CoreAPIProvider").value
    core_api_provider.mds.call_del_entity("industry", sector_id)


def delete_test_zip(zip_code_id):
    # bomboj for
    core_api_provider = Dependency("CoreAPIProvider").value
    core_api_provider.mds.call_del_entity("zip_code", zip_code_id)


def delete_test_rir(rir_id):
    # bomboj for
    core_api_provider = Dependency("CoreAPIProvider").value
    core_api_provider.mds.call_del_entity("retail_input_record", rir_id)


# ------------------------------------------------ Helpers ------------------------------------------------ #


# puts dates into strings (if not null)
def __clean_up_date_for_api(date):
    if date:
        date = str(date)
    return date


# unit test helpers
context = {
    "source": "Geoprocessing integration test",
    "user_id": None
}
