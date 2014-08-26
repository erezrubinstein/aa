ALTER view [dbo].[qa_report_new_vw] as
select c.company_id
	, c.name as company_name
	, s.store_id
	, a.street_number
	, a.street
	, a.municipality
	, a.governing_district
	, a.postal_area
	, a.fulladdress
	, a.fulladdress_normalized
	, a.longitude
	, a.latitude
	, s.opened_date
	, s.closed_date
	, s.assumed_opened_date
	, s.assumed_closed_date
	, coalesce(mt.name,'Not a Monopoly') as monopoly_type
	, m.start_date as monopoly_start_date
	, m.end_date as monopoly_end_date
	, d.[population] as home_population
	, d.per_capita_income as home_per_capita_income
	, d.aggregate_income as home_aggregate_income
	, d.average_household_income as home_average_household_income
	, d.median_household_income as home_median_household_income
	, d.total_family_households as home_total_family_households
	
	, cs.away_store_id
	, c2.company_id as away_company_id
	, c2.name as away_company_name
	, a2.street_number as away_street_number
	, a2.street as away_street
	, a2.municipality as away_municipality
	, a2.governing_district as away_governing_district
	, a2.postal_area as away_postal_area
	, a2.fulladdress as away_fulladdress
	, a2.fulladdress_normalized as away_fulladdress_normalized
	, a2.longitude as away_longitude
	, a2.latitude as away_latitude
	, s2.opened_date as away_opened_date
	, s2.closed_date as away_closed_date
	, s2.assumed_opened_date as away_assumed_opened_date
	, s2.assumed_closed_date as away_assumed_closed_date
	
	, cs.competitive_store_id
	, cs.start_date as competition_start_date
	, cs.end_date as competition_end_date
	, cs.travel_time as competition_travel_time
	
	, d2.[population] as away_population
	, d2.per_capita_income as away_per_capita_income
	, d2.aggregate_income as away_aggregate_income
	, d2.average_household_income as away_average_household_income
	, d2.median_household_income as away_median_household_income
	, d2.total_family_households as away_total_family_households
	
	, 3963.1*ACOS(SIN(a.latitude/57.29577951)*SIN(a2.latitude/57.29577951)+COS(a.latitude/57.29577951)*COS(a2.latitude/57.29577951)*(COS((a.longitude/57.29577951)-(a2.longitude/57.2957795)))) as trig_distance_miles
from companies c with (nolock)
inner join stores s with (nolock) on s.company_id = c.company_id
inner join addresses_vw a with (nolock) on a.address_id = s.address_id
left outer join retail_demographic_basic_stats_vw d with (nolock) on d.store_id = s.store_id
left outer join competitive_stores cs with (nolock) on cs.home_store_id = s.store_id
left outer join stores s2 with (nolock) on s2.store_id = cs.away_store_id
left outer join monopolies m on m.store_id = s.store_id
left outer join monopoly_types mt on mt.monopoly_type_id = m.monopoly_type_id
left outer join companies c2 with (nolock) on c2.company_id = s2.company_id
left outer join addresses_vw a2 with (nolock) on a2.address_id = s2.address_id
left outer join retail_demographic_basic_stats_vw d2 with (nolock) on d2.store_id = s2.store_id;


GO


