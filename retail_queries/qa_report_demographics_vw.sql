alter view [dbo].[qa_report_demographics_vw] as
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
from companies c with (nolock)
inner join stores s with (nolock) on s.company_id = c.company_id
inner join addresses_vw a with (nolock) on a.address_id = s.address_id
left outer join retail_demographic_basic_stats_vw d with (nolock) on d.store_id = s.store_id
left outer join monopolies m with (nolock) on m.store_id = s.store_id
left outer join monopoly_types mt with (nolock) on mt.monopoly_type_id = m.monopoly_type_id

GO


