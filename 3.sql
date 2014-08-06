/****** Object:  View [dbo].[addresses_matching_vw]    Script Date: 11/26/2012 18:14:45 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF NOT EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[addresses_matching_vw]'))
EXEC dbo.sp_executesql @statement = N'CREATE view [dbo].[addresses_matching_vw] as
select *
	, replace(replace(replace(replace(
		replace(replace(replace(replace(street, ''East '', ''E ''), ''West '',''W ''), ''South '',''S ''),''North '',''N '')
		,''E. '',''E ''),''W. '',''W ''),''S. '',''S ''),''N. '',''N '') as street_normalized
	, case when street like ''% %'' then substring(street,1, charindex('' '', street) - 1) else street end as street_first_word
from addresses;


'
GO
/****** Object:  View [dbo].[addresses_vw]    Script Date: 11/26/2012 18:14:45 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF NOT EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[addresses_vw]'))
EXEC dbo.sp_executesql @statement = N'CREATE view [dbo].[addresses_vw] as
select *
	, case when street_number is null then '''' else convert(varchar(100), street_number) + '' '' end
		+ case when street is null then '''' else street + '', '' end
		+ coalesce(municipality,'''') + '', ''
		+ coalesce(governing_district,'''') + '' ''
		+ coalesce(postal_area,'''') as fulladdress
	, case when street_number is null then '''' else convert(varchar(100), street_number) + '' '' end
		+ case when street_normalized is null then '''' else street_normalized + '', '' end
		+ coalesce(municipality,'''') + '', ''
		+ coalesce(governing_district,'''') + '' ''
		+ coalesce(postal_area,'''') as fulladdress_normalized
	, case when street_normalized like ''% %''
		then substring(street_normalized,1, charindex('' '', street_normalized) - 1)
		else street_normalized end as street_normalized_first_word
from addresses_matching_vw;

'
GO
/****** Object:  View [dbo].[stores_vw]    Script Date: 11/26/2012 18:14:45 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF NOT EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[stores_vw]'))
EXEC dbo.sp_executesql @statement = N'
create view [dbo].[stores_vw] as
select *, replace(replace(replace(replace(phone_number,''('',''''),'')'',''''),''-'',''''),'' '','''') as stripped_phone_number
from stores
'
GO
/****** Object:  View [dbo].[retail_demographic_values_vw]    Script Date: 11/26/2012 18:14:45 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF NOT EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[retail_demographic_values_vw]'))
EXEC dbo.sp_executesql @statement = N'
CREATE view [dbo].[retail_demographic_values_vw] as

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


'
GO
/****** Object:  View [dbo].[retail_demographic_basic_stats_vw]    Script Date: 11/26/2012 18:14:45 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF NOT EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[retail_demographic_basic_stats_vw]'))
EXEC dbo.sp_executesql @statement = N'
CREATE view [dbo].[retail_demographic_basic_stats_vw] as

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
	        13,	--TOTPOP_CY
            19,	--FAMHH_CY
            84,	--MEDHINC_CY
            86,	--AVGHINC_CY
            88)	--PCI_CY
) as t
pivot (
	max(value)
	for name in ([TOTPOP_CY], [PCI_CY], [MEDHINC_CY], [AVGHINC_CY], [FAMHH_CY])
) as pvt;

'
GO
/****** Object:  View [dbo].[qa_report_new_vw]    Script Date: 11/26/2012 18:14:45 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF NOT EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[qa_report_new_vw]'))
EXEC dbo.sp_executesql @statement = N'CREATE view [dbo].[qa_report_new_vw] as
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
	, coalesce(mt.name,''Not a Monopoly'') as monopoly_type
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
'
GO
/****** Object:  View [dbo].[qa_report_demographics_vw]    Script Date: 11/26/2012 18:14:45 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF NOT EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[qa_report_demographics_vw]'))
EXEC dbo.sp_executesql @statement = N'CREATE view [dbo].[qa_report_demographics_vw] as
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
	, coalesce(mt.name,''Not a Monopoly'') as monopoly_type
	, m.start_date as monopoly_start_date
	, m.end_date as monopoly_end_date
	, d.trade_area_id
	, th.measurement_type
	, th.measurement
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
left outer join trade_areas t with (nolock) on t.trade_area_id = d.trade_area_id
left outer join thresholds th with (nolock) on th.threshold_id = t.threshold_id
left outer join monopolies m with (nolock) on m.store_id = s.store_id
left outer join monopoly_types mt with (nolock) on mt.monopoly_type_id = m.monopoly_type_id;
'
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF NOT EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[qa_report_zip_census_vw]'))
EXEC dbo.sp_executesql @statement = N'create view [dbo].[qa_report_zip_census_vw] as
select s.company_id
	, c.name as company_name
	, s.store_id
	, a.fulladdress
	, a.latitude
	, a.longitude
	, szp.zip_code as proximity_zip_code
	, z.INTPTLAT as zip_centroid_latitude
	, z.INTPTLONG as zip_centroid_longitude
	, z.ALAND
	, z.ALAND_SQLMI
	, z.AWATER
	, z.AWATER_SQLMI
	, z.HU10
	, z.POP10
	, szp.proximity as proximity_postgis_meters
	, szp.proximity / 1609.34 as proximity_postgis_miles
	, 3963.1*ACOS(SIN(a.latitude/57.29577951)*SIN(z.INTPTLAT/57.29577951)+COS(a.latitude/57.29577951)*COS(z.INTPTLAT/57.29577951)*(COS((a.longitude/57.29577951)-(z.INTPTLONG/57.2957795))))
		as trig_proximity_miles
from store_zip_proximities szp
inner join stores s on s.store_id = szp.store_id
inner join companies c on c.company_id = s.company_id
inner join addresses_vw a on a.address_id = s.address_id
inner join zip_codes z on z.zip_code = szp.zip_code;
'
GO

