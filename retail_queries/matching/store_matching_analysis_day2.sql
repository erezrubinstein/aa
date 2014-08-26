with mismatches as (
	select s0.id
	, abs(a0.longitude - a1.longitude) as diff_longitude
	, abs(a0.latitude - a1.latitude) as diff_latitude
	, abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude) as diff_combined
	, (abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude)) * 70 as diff_miles 
	from retaildb_test_june2011.dbo.stores s0 with (nolock)
	inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
	inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
	inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
	inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
	where a1.fulladdress = a0.fulladdress --25414 of 30337
), bins as (
	select *, NTILE(200) over (order by diff_miles desc) as halfpercentile 
	from mismatches
)
select bins.halfpercentile
	, count(*) as cnt
	, min(diff_combined) as min_diff_degrees
	, max(diff_combined) as max_diff_degrees
	, min(diff_miles) as min_diff_miles
	, max(diff_miles) as max_diff_miles
from bins
group by bins.halfpercentile
order by bins.halfpercentile;

