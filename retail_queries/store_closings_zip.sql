select s0.company_id, c.name, count(distinct s0.id) cntClosedStores
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
where not exists (
	select 1 from retaildb_test_server.dbo.stores s1 with (nolock)
	inner join retaildb_test_server.dbo.addresses a1 with (nolock) on a1.store_id = s1.id
	where s1.company_id = s0.company_id
		and a1.postal_area = a0.postal_area
)
group by s0.company_id, c.name
order by s0.company_id, c.name
--2021 total


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
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
where not exists (
	select 1 from retaildb_test_server.dbo.stores s1 with (nolock)
	inner join retaildb_test_server.dbo.addresses a1 with (nolock) on a1.store_id = s1.id
	where s1.company_id = s0.company_id
		and a1.postal_area = a0.postal_area
)
--2021 total
