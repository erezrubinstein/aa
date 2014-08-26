--select distinct s0.id as june2011_store_id
--		, abs(a0.longitude - a1.longitude) as diff_longitude
--		, abs(a0.latitude - a1.latitude) as diff_latitude
--		, abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude) as diff_combined
--		, (abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude)) * 70 as diff_miles 
--into stores_2digit_degrees_matches
--from retaildb_test_june2011.dbo.stores s0 with (nolock)
--inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
--inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
--inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
--inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
--where not exists (
--		select 1 from stores_3digit_degrees_matches e
--		where e.june2011_store_id = s0.id
--	)
--	and not exists (
--		select 1 from stores_4digit_degrees_matches e
--		where e.june2011_store_id = s0.id
--	)
--	and not exists (
--		select 1 from stores_exact_address_matches e
--		where e.june2011_store_id = s0.id
--	)
--	and round(a1.longitude,2) = round(a0.longitude,2)
--	and round(a1.latitude,2) = round(a0.latitude,2);

select COUNT(*) from stores_2digit_degrees_matches;

with mismatches as (
	select distinct s0.id
			, abs(a0.longitude - a1.longitude) as diff_longitude
			, abs(a0.latitude - a1.latitude) as diff_latitude
			, abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude) as diff_combined
			, (abs(a0.longitude - a1.longitude) + abs(a0.latitude - a1.latitude)) * 70 as diff_miles 
	from retaildb_test_june2011.dbo.stores s0 with (nolock)
	inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
	inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
	inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
	inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
	where not exists (
			select 1 from stores_3digit_degrees_matches e
			where e.june2011_store_id = s0.id
		)
		and not exists (
			select 1 from stores_4digit_degrees_matches e
			where e.june2011_store_id = s0.id
		)
		and not exists (
			select 1 from stores_exact_address_matches e
			where e.june2011_store_id = s0.id
		)
		and round(a1.longitude,2) = round(a0.longitude,2)
		and round(a1.latitude,2) = round(a0.latitude,2) 
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
group by bins.halfpercentile with rollup
order by bins.halfpercentile;