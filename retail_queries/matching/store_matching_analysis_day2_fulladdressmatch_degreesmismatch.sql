select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress = a0.fulladdress --25414 of 30337
	and (
		a1.longitude <> a0.longitude
		or a1.latitude <> a0.latitude
	) --13266