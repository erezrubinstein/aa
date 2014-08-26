USE [matching]
GO

/****** Object:  View [dbo].[stores_matched_analysis_vw]    Script Date: 12/04/2012 13:56:11 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

ALTER view [dbo].[stores_matched_analysis_vw] as
select c.name 
	, m.match_type
	, s0.id as june2011_store_id
	, a0.fulladdress as june2011_fulladdress
	, a0.fulladdress_normalized as june2011_fulladdress_normalized
	, a0.street_number as june2011_street_number
	, a0.street as june2011_street
	, a0.municipality as june2011_city
	, a0.governing_district as june2011_state
	, a0.postal_area as june2011_zip
	, s0.phone_number as june2011_phone_number
	, s0.complex as june2011_shopping_center
	, case when s0.opened_on = '1900-01-01' then '' else convert(varchar(100),s0.opened_on,120) end as june2011_opened_on
	, s0.note as june2011_note
	, a0.longitude as june2011_longitude
	, a0.latitude as june2011_latitude
	, s1.id as oct2012_store_id
	, a1.fulladdress as oct2012_fulladdress
	, a1.fulladdress_normalized as oct2012_fulladdress_normalized
	, a1.street_number as oct2012_street_number
	, a1.street as oct2012_street
	, a1.municipality as oct2012_city
	, a1.governing_district as oct2012_state
	, a1.postal_area as oct2012_zip
	, s1.phone_number as oct2012_phone_number
	,	s1.complex as oct2012_shopping_center
	, case when s1.opened_on = '1900-01-01' then '' else convert(varchar(100),s1.opened_on,120) end as oct2012_opened_on
	, s1.note as oct2012_note
	, a1.longitude as oct2012_longitude
	, a1.latitude as oct2012_latitude
	, abs(a0.longitude - a1.longitude) as diff_longitude
	, abs(a0.latitude - a1.latitude) as diff_latitude
	, abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude) as diff_combined
	, (abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude)) * 70 as diff_miles  
from stores_matched m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.june2011_store_id
inner join retaildb_test_june2011.dbo.companies c on c.id = s0.company_id
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.id = m.june2011_address_id
inner join retaildb_test_oct2012.dbo.stores s1 on s1.id = m.oct2012_store_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 on a1.id = m.oct2012_address_id
where not exists (
	select 1 from stores_oct2012_dupes dupes
	where dupes.bad_store_id = s1.id
	)

union

select c.name 
	, 'manual' as match_type
	, s0.id as june2011_store_id
	, a0.fulladdress as june2011_fulladdress
	, a0.fulladdress_normalized as june2011_fulladdress_normalized
	, a0.street_number as june2011_street_number
	, a0.street as june2011_street
	, a0.municipality as june2011_city
	, a0.governing_district as june2011_state
	, a0.postal_area as june2011_zip
	, s0.phone_number as june2011_phone_number
	, s0.complex as june2011_shopping_center
	, case when s0.opened_on = '1900-01-01' then '' else convert(varchar(100),s0.opened_on,120) end as june2011_opened_on
	, s0.note as june2011_note
	, a0.longitude as june2011_longitude
	, a0.latitude as june2011_latitude
	, s1.id as oct2012_store_id
	, a1.fulladdress as oct2012_fulladdress
	, a1.fulladdress_normalized as oct2012_fulladdress_normalized
	, a1.street_number as oct2012_street_number
	, a1.street as oct2012_street
	, a1.municipality as oct2012_city
	, a1.governing_district as oct2012_state
	, a1.postal_area as oct2012_zip
	, s1.phone_number as oct2012_phone_number
	, s1.complex as oct2012_shopping_center
	, case when s1.opened_on = '1900-01-01' then '' else convert(varchar(100),s1.opened_on,120) end as oct2012_opened_on
	, s1.note as oct2012_note
	, a1.longitude as oct2012_longitude
	, a1.latitude as oct2012_latitude
	, abs(a0.longitude - a1.longitude) as diff_longitude
	, abs(a0.latitude - a1.latitude) as diff_latitude
	, abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude) as diff_combined
	, (abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude)) * 70 as diff_miles  
from stores_matched_by_manila m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.june_id
inner join retaildb_test_june2011.dbo.companies c on c.id = s0.company_id
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
inner join retaildb_test_oct2012.dbo.stores s1 on s1.id = m.oct_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 on a1.store_id = s1.id
where not exists (
	select 1 from stores_matched automatches
	where automatches.june2011_store_id = m.june_id
)

union

select c.name 
	, 'closed' as match_type
	, s0.id as june2011_store_id
	, a0.fulladdress as june2011_fulladdress
	, a0.fulladdress_normalized as june2011_fulladdress_normalized
	, a0.street_number as june2011_street_number
	, a0.street as june2011_street
	, a0.municipality as june2011_city
	, a0.governing_district as june2011_state
	, a0.postal_area as june2011_zip
	, s0.phone_number as june2011_phone_number
	, s0.complex as june2011_shopping_center
	, case when s0.opened_on = '1900-01-01' then '' else convert(varchar(100),s0.opened_on,120) end as june2011_opened_on
	, s0.note as june2011_note
	, a0.longitude as june2011_longitude
	, a0.latitude as june2011_latitude
	, NULL as oct2012_store_id
	, NULL as oct2012_fulladdress
	, NULL as oct2012_fulladdress_normalized
	, NULL as oct2012_street_number
	, NULL as oct2012_street
	, NULL as oct2012_city
	, NULL as oct2012_state
	, NULL as oct2012_zip
	, NULL as oct2012_phone_number
	, NULL as oct2012_shopping_center
	, NULL as oct2012_opened_on
	, NULL as oct2012_note
	, NULL as oct2012_longitude
	, NULL as oct2012_latitude
	, NULL as diff_longitude
	, NULL as diff_latitude
	, NULL as diff_combined
	, NULL as diff_miles  
from retaildb_test_june2011.dbo.stores s0 
inner join retaildb_test_june2011.dbo.companies c on c.id = s0.company_id
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
where not exists (
	select 1 from stores_matched_by_manila m
	where m.june_id = s0.id
	)
	and not exists (
	select 1 from stores_matched m
	where m.june2011_store_id = s0.id
	)
;


GO


