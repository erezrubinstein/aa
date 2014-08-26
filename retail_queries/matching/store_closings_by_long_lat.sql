--store closing by long/lat

--matching full scale

select s0.company_id, c.name, count(distinct s0.id) cntClosedStores
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
where not exists (
	select 1 from retaildb_test_server.dbo.stores s1 with (nolock)
	inner join retaildb_test_server.dbo.addresses a1 with (nolock) on a1.store_id = s1.id
	where s1.company_id = s0.company_id
		and a1.longitude = a0.longitude
		and a1.latitude = a0.latitude
)
group by s0.company_id, c.name
with rollup
order by s0.company_id, c.name

--17007 total


--by long/lat
select s0.company_id
	, c.name
	, s0.id as store_id
	, a0.street_number
	, a0.street
	, a0.municipality
	, a0.governing_district
	, a0.postal_area
	, s0.opened_on
	, s0.phone_number
	, a0.longitude
	, a0.latitude
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
where not exists (
	select 1 from retaildb_test_server.dbo.stores s1 with (nolock)
	inner join retaildb_test_server.dbo.addresses a1 with (nolock) on a1.store_id = s1.id
	where s1.company_id = s0.company_id
		and a1.longitude = a0.longitude
		and a1.latitude = a0.latitude
)
--17007 total



--round to 4 decimal places

--by long/lat rounded to 4 decimal places
select s0.company_id
	, c.name
	, s0.id as store_id
	, a0.street_number
	, a0.street
	, a0.municipality
	, a0.governing_district
	, a0.postal_area
	, s0.opened_on
	, s0.phone_number
	, a0.longitude
	, a0.latitude
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
where not exists (
	select 1 from retaildb_test_server.dbo.stores s1 with (nolock)
	inner join retaildb_test_server.dbo.addresses a1 with (nolock) on a1.store_id = s1.id
	where s1.company_id = s0.company_id
		and round(a1.longitude,4) = round(a0.longitude,4)
		and round(a1.latitude,4) = round(a0.latitude,4)
)
--7853 total



select s0.company_id
	, c.name
	, s0.id as store_id
	, a0.street_number
	, a0.street
	, a0.municipality
	, a0.governing_district
	, a0.postal_area
	, s0.opened_on
	, s0.phone_number
	, a0.longitude
	, a0.latitude
	, a0.fulladdress
	, a1.longitude
	, a1.latitude
	, a1.fulladdress
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_server.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_server.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.postal_area = a0.postal_area
	and round(a1.longitude,4) <> round(a0.longitude,4)
	and round(a1.latitude,4) <> round(a0.latitude,4)




