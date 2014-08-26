select manila.*, a.fulladdress as june2011_fulladdress, a2.fulladdress as oct2012_fulladress
FROM [matching].[dbo].[stores_matched_by_manila] manila
inner join retaildb_test_june2011.dbo.addresses_vw a with (nolock) on a.store_id = manila.june_id
inner join retaildb_test_oct2012.dbo.addresses_vw a2 with (nolock) on a2.store_id = manila.oct_id
where not exists (
	select 1 from matching.dbo.stores_matched automatches with (nolock)
	where automatches.june2011_store_id = manila.june_id
		and automatches.oct2012_store_id = manila.oct_id
)
--1548 records manual matched by manila (that were not automatched by Jeff's initial logics)

