select * 
from retaildb_test_june2011.dbo.addresses_vw a
inner join retaildb_test_june2011.dbo.stores s on s.id = a.store_id
where s.id = 126985
order by postal_area;

select * 
from retaildb_test_oct2012.dbo.addresses_vw a
inner join retaildb_test_oct2012.dbo.stores s on s.id = a.store_id
where s.company_id = 8
	and a.governing_district = 'FL'
	--and a.municipality = 'Medina'
order by postal_area;


select ROUND(42.374907,2), ROUND(-85.430175,2)
select ROUND(42.375864,2), ROUND(-85.436696,2)


select count(*)
from retaildb_test_oct2012.dbo.addresses_vw a
where a.postal_area = '' --693


select * from retaildb_test_june2011.dbo.addresses_vw a
where street like 'E %'
select * from retaildb_test_june2011.dbo.addresses_vw a
where street like 'East %'






select * from retaildb_test_june2011.dbo.addresses_vw a
inner join retaildb_test_june2011.dbo.stores s on s.id = a.store_id
where s.id = 122179
order by postal_area;

select * from retaildb_test_oct2012.dbo.addresses_vw a
inner join retaildb_test_oct2012.dbo.stores s on s.id = a.store_id
where s.id = 49138
order by postal_area;




use retaildb_test_june2011

--rtrim, ltrim (see other file)

--LA

begin transaction

update dbo.addresses
set municipality = 'Los Angeles'
where municipality in ('LA','L.A.');

select * from dbo.addresses a
where a.municipality in ('LA','L.A.');

commit


--leading 0s

--select * from retaildb_test_june2011.dbo.addresses_vw a
--inner join retaildb_test_june2011.dbo.stores s on s.id = a.store_id
--where country_id = 840 --US
--	and len(a.postal_area) < 5

--select * from retaildb_test_oct2012.dbo.addresses_vw a
--inner join retaildb_test_oct2012.dbo.stores s on s.id = a.store_id
--where country_id = 840 --US
--	and len(a.postal_area) < 5
--	and postal_area <> '';
	
	
begin transaction

update dbo.addresses
set postal_area = '0' + postal_area
where country_id = 840 --US
	and len(postal_area) = 4;

select * from dbo.addresses a
where a.country_id = 840
	and LEN(postal_area) = 4;

commit