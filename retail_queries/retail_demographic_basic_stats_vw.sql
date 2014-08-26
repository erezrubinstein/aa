
alter view [dbo].[retail_demographic_basic_stats_vw] as

select trade_area_id
	, store_id
	, census_year
	, [TOTPOP_CY] as [population]
	, [PCI_CY] as per_capita_income
	, [TOTPOP_CY] * [PCI_CY] as aggregate_income
	, [MEDHINC_CY] as [median_household_income]
	, [AVGHINC_CY] as [average_household_income]
	, [FAMHH_CY] as [total_family_households]
	
from (	
	select t.trade_area_id, t.store_id, di.name, d.value, year(p.period_start_date) as census_year
	from demographic_numvalues d with (nolock)
	inner join data_items di with (nolock) on di.data_item_id = d.data_item_id
	inner join trade_areas t with (nolock) on t.trade_area_id = d.trade_area_id
	inner join periods p with (nolock) on p.period_id = d.period_id
	where d.data_item_id in (
			621, --TOTPOP_CY
			696, --PCI_CY
			692, --MEDHINC_CY
			694, --AVGHINC_CY
			627) --FAMHH_CY
) as t
pivot (
	max(value)
	for name in ([TOTPOP_CY], [PCI_CY], [MEDHINC_CY], [AVGHINC_CY], [FAMHH_CY])
) as pvt;

GO



--select trade_area_id, count(*) cnt from [retail_demographic_basic_stats_vw] group by trade_area_id having count(*) > 1;
--select * from [retail_demographic_basic_stats_vw];