
--exact match by full address
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress = a0.fulladdress --24293 of 30337


--exact match by 4 digit long lat
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where round(a1.longitude,4) = round(a0.longitude,4)
		and round(a1.latitude,4) = round(a0.latitude,4) --22484 of 30337

select 30337 - 22484 --7853 mismatch


--exact match by 3 digit long lat
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where round(a1.longitude,3) = round(a0.longitude,3)
		and round(a1.latitude,3) = round(a0.latitude,3) --23953 of 30337

select 30337 - 23953 --6384 mismatch


--exact match by 2 digit long lat
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where round(a1.longitude,2) = round(a0.longitude,2)
		and round(a1.latitude,2) = round(a0.latitude,2) --27864 of 30337

select 30337 - 27864 --2473 mismatch



--exact match by 2 digit long lat
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where round(a1.longitude,2) = round(a0.longitude,2)
		and round(a1.latitude,2) = round(a0.latitude,2) --27864 of 30337
		


--exact match by phone number
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where s0.phone_number = s1.phone_number --13031 of 303377



--2 digit long lat OR phone number
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id --30337
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where (
	round(a1.longitude,2) = round(a0.longitude,2)
		and round(a1.latitude,2) = round(a0.latitude,2) --27864 of 30337
	)
	or s0.phone_number = s1.phone_number --13031 of 303377



--full address matches + 4 digits of long/lat matches (i.e. precise to 11.1m at the equator)
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
where exists (
	select 1 from retaildb_test_oct2012.dbo.stores s1 with (nolock)
	inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
	where s1.company_id = s0.company_id
		and a1.fulladdress = a0.fulladdress
		and round(a1.longitude,4) = round(a0.longitude,4)
		and round(a1.latitude,4) = round(a0.latitude,4)
)
--18959 total




--full address matches + full long/lat matches (i.e. very precise)
select count(distinct s0.id)
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
where exists (
	select 1 from retaildb_test_oct2012.dbo.stores s1 with (nolock)
	inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
	where s1.company_id = s0.company_id
		and a1.fulladdress = a0.fulladdress
		and a1.longitude = a0.longitude
		and a1.latitude = a0.latitude
)
--11236 total