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
inner join retaildb_test_oct2012.dbo.addresses_vw a1 on a1.id = m.oct2012_address_id;
go


with bins as (
	select *, NTILE(10) over (partition by match_type order by diff_miles desc) as decile
	from stores_matched_analysis_vw
)
select bins.match_type
	, bins.decile
	, count(*) as cnt
	, min(diff_combined) as min_diff_degrees
	, max(diff_combined) as max_diff_degrees
	, min(diff_miles) as min_diff_miles
	, max(diff_miles) as max_diff_miles
from bins
group by bins.match_type, bins.decile
order by bins.match_type, bins.decile;


select june2011_store_id as Store_ID
	, convert(varchar(100), oct2012_street_number) + ' ' + oct2012_street as Address
	, oct2012_city as City
	, oct2012_state as State
	, oct2012_zip as Zip
	, oct2012_phone_number as Phone
from [stores_matched_analysis_vw]
where diff_miles > 0.1