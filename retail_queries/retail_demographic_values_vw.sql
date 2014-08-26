alter view [dbo].[retail_demographic_values_vw] as

select s.company_id
	, a.fulladdress
	, t.store_id
	, v.trade_area_id
	, v.data_item_id
	, di.name
	, di.description
	, year(p.period_start_date) as census_year
	, year(pt.period_start_date) as target_year
	, convert(varchar(100), v.value) as value
from stores s 
inner join addresses_vw a on a.address_id = s.address_id
inner join trade_areas t on t.store_id = s.store_id
inner join demographic_numvalues v on v.trade_area_id = t.trade_area_id
inner join data_items di on di.data_item_id = v.data_item_id
inner join periods p on p.period_id = v.period_id
left outer join periods pt on pt.period_id = v.target_period_id

union all

select s.company_id
	, a.fulladdress
	, t.store_id
	, v.trade_area_id
	, v.data_item_id
	, di.name
	, di.description
	, year(p.period_start_date) as census_year
	, year(pt.period_start_date) as target_year
	, v.value
from stores s 
inner join addresses_vw a on a.address_id = s.address_id
inner join trade_areas t on t.store_id = s.store_id
inner join demographic_strvalues v on v.trade_area_id = t.trade_area_id
inner join data_items di on di.data_item_id = v.data_item_id
inner join periods p on p.period_id = v.period_id
left outer join periods pt on pt.period_id = v.target_period_id;

go