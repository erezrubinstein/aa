
use matching;

if OBJECT_ID('stores_matched') is not null
begin
	drop table stores_matched;
end

create table stores_matched (
	stores_matched_id int identity(1,1) not null constraint PK_stores_matched primary key clustered,
	june2011_store_id int not null,
	june2011_address_id int not null,
	oct2012_store_id int not null,
	oct2012_address_id int not null,
	match_type varchar(1000) not null
	);
	
insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '010 - full address + full long/lat (i.e. very precise)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress = a0.fulladdress
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
--12066 total

create unique nonclustered index UK_stores_matched on stores_matched (june2011_store_id, oct2012_store_id);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '011 - normalized full address + full long/lat (i.e. very precise)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress_normalized = a0.fulladdress_normalized
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);

insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '020 - city + state + zip + full long/lat (i.e. very precise)' as match_type
	--, a0.fulladdress
	--, a1.fulladdress
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);



insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '021 - street_number + street + state + zip + full long/lat (allows variations in city names)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street = a0.street
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '022 - street_number + normalized_street + state + zip + full long/lat (allows variations in city names)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized = a0.street_normalized
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '023 - street_number + city + state + zip + full long/lat (allows variations in street names)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '024 - street_number + street + city + state + full long/lat (allows variations in zip)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street = a0.street
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '025 - street_number + street_normalized + city + state + full long/lat (allows variations in zip)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized = a0.street_normalized
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);



insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '026 - street_number + street + state + full long/lat (allows variations in city and zip)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street = a0.street
	and a1.governing_district = a0.governing_district
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct2011_store_id
	, a1.id as oct2012_address_id
	, '030 - full address + 4 digit long/lat (i.e. precise to 11.1m at the equator)' as match_type
	--, a0.fulladdress
	--, a0.latitude, a0.longitude
	--, a1.fulladdress
	--, a1.latitude, a1.longitude
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress = a0.fulladdress
	and round(a1.longitude,4) = round(a0.longitude,4)
	and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
--7733 rows


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct2011_store_id
	, a1.id as oct2012_address_id
	, '031 - full normalized address + 4 digit long/lat (i.e. precise to 11.1m at the equator)' as match_type
	--, a0.fulladdress
	--, a0.latitude, a0.longitude
	--, a1.fulladdress
	--, a1.latitude, a1.longitude
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress_normalized = a0.fulladdress_normalized
	and round(a1.longitude,4) = round(a0.longitude,4)
	and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '032 - street_number + street + state + zip + 4-digit long/lat (allows variations in city names)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street = a0.street
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and round(a1.longitude,4) = round(a0.longitude,4)
	and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	
	
insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '033 - street_number + street_normalized + state + zip + 4-digit long/lat (allows variations in city names)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized = a0.street_normalized
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and round(a1.longitude,4) = round(a0.longitude,4)
	and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);



insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '034 - street_number + city + state + zip + 4-digit long/lat (allows variations in street names)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and round(a1.longitude,4) = round(a0.longitude,4)
	and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);



insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '040 - full address + 3 digit long/lat (i.e. accurate to 111m at the equator' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress = a0.fulladdress
	and round(a1.longitude,3) = round(a0.longitude,3)
	and round(a1.latitude,3) = round(a0.latitude,3)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	
insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '041 - normalized address + 3 digit long/lat (i.e. accurate to 111m at the equator' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress_normalized = a0.fulladdress_normalized
	and round(a1.longitude,3) = round(a0.longitude,3)
	and round(a1.latitude,3) = round(a0.latitude,3)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '042 - full address + 2 digit long/lat (i.e. accurate to 1.11km at the equator' as match_type
	--, a0.fulladdress
	--, a1.fulladdress
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress = a0.fulladdress
	and round(a1.longitude,2) = round(a0.longitude,2)
	and round(a1.latitude,2) = round(a0.latitude,2)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	
insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '043 - full normalized address + 2 digit long/lat (i.e. accurate to 1.11km at the equator' as match_type
	--, a0.fulladdress
	--, a1.fulladdress
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress_normalized = a0.fulladdress_normalized
	and round(a1.longitude,2) = round(a0.longitude,2)
	and round(a1.latitude,2) = round(a0.latitude,2)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	
	

insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '044 - full address + 1 digit long/lat (i.e. accurate to 11.1km at the equator' as match_type
	--, a0.fulladdress
	--, a1.fulladdress
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress = a0.fulladdress
	and round(a1.longitude,1) = round(a0.longitude,1)
	and round(a1.latitude,1) = round(a0.latitude,1)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	
insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '045 - full normalized address + 1 digit long/lat (i.e. accurate to 11.1km at the equator' as match_type
	--, a0.fulladdress
	--, a1.fulladdress
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.fulladdress_normalized = a0.fulladdress_normalized
	and round(a1.longitude,1) = round(a0.longitude,1)
	and round(a1.latitude,1) = round(a0.latitude,1)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '050 - street_number + street_normalized_first_word + city + state + zip + 3-digit long/lat (allows some variation in street names )' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized_first_word = a0.street_normalized_first_word
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and round(a1.longitude,3) = round(a0.longitude,3)
	and round(a1.latitude,3) = round(a0.latitude,3)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	

insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '051 - street_number + street_normalized_first_word + city + state + 3-digit long/lat (allows some variation in street names and zip)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized_first_word = a0.street_normalized_first_word
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and round(a1.longitude,3) = round(a0.longitude,3)
	and round(a1.latitude,3) = round(a0.latitude,3)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);



insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '052 - street_number + street_normalized_first_word + state + zip + 3-digit long/lat (allows some variation in street names and city)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized_first_word = a0.street_normalized_first_word
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and round(a1.longitude,3) = round(a0.longitude,3)
	and round(a1.latitude,3) = round(a0.latitude,3)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '053 - street_number + street_normalized_first_word + state + zip + 2-digit long/lat (allows some variation in street names and city)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized_first_word = a0.street_normalized_first_word
	and a1.governing_district = a0.governing_district
	and a1.postal_area = a0.postal_area
	and round(a1.longitude,2) = round(a0.longitude,2)
	and round(a1.latitude,2) = round(a0.latitude,2)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
		
	
	



insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '060 - zip + full long/lat (allows variations in addresses except zip)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.postal_area = a0.postal_area
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
--13 rows

insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '061 - zip + 4-digit long/lat (allows variations in addresses except zip)' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.postal_area = a0.postal_area
	and round(a1.longitude,4) = round(a0.longitude,4)
	and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
--13 rows



insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '070 - stripped phone + full long/lat' as match_type
from retaildb_test_june2011.dbo.stores_vw s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores_vw s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where s0.stripped_phone_number = s1.stripped_phone_number
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	--and round(a1.longitude,4) = round(a0.longitude,4)
	--and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '071 - phone + street_number + street + 4-digit long/lat' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where s0.phone_number = s1.phone_number
	and a1.street_number = a0.street_number
	and a1.street = a0.street
	and a1.longitude = a0.longitude
	and a1.latitude = a0.latitude
	--and round(a1.longitude,4) = round(a0.longitude,4)
	--and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);




insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '080 - street_number + street_normalized + city + state + [blank zip on either side] + 4-digit long/lat' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized = a0.street_normalized
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and (a1.postal_area = '' or a0.postal_area = '')
	and round(a1.longitude,4) = round(a0.longitude,4)
	and round(a1.latitude,4) = round(a0.latitude,4)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	
insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '081 - street_number + street_normalized street + city + state + [blank zip on either side] + 3-digit long/lat' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized = a0.street_normalized
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and (a1.postal_area = '' or a0.postal_area = '')
	and round(a1.longitude,3) = round(a0.longitude,3)
	and round(a1.latitude,3) = round(a0.latitude,3)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '082 - street_number + street_normalized street + city + state + [blank zip on either side] + 2-digit long/lat' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized = a0.street_normalized
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and (a1.postal_area = '' or a0.postal_area = '')
	and round(a1.longitude,2) = round(a0.longitude,2)
	and round(a1.latitude,2) = round(a0.latitude,2)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	

insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '083 - street_number + street_normalized street + city + state + [blank zip on either side] + 2-digit long/lat' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized = a0.street_normalized
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and (a1.postal_area = '' or a0.postal_area = '')
	and round(a1.longitude,2) = round(a0.longitude,2)
	and round(a1.latitude,2) = round(a0.latitude,2)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);
	

insert into stores_matched (june2011_store_id, june2011_address_id, oct2012_store_id, oct2012_address_id, match_type)
select distinct 
	s0.id as june2011_store_id
	, a0.id as june2011_address_id
	, s1.id as oct_2011_store_id
	, a1.id as oct2012_address_id
	, '084 - street_number + street_normalized street + city + state + [blank zip on either side] + 1-digit long/lat' as match_type
from retaildb_test_june2011.dbo.stores s0 with (nolock)
inner join retaildb_test_june2011.dbo.addresses_vw a0 with (nolock) on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s0.company_id
inner join retaildb_test_oct2012.dbo.stores s1 with (nolock) on s1.company_id = s0.company_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 with (nolock) on a1.store_id = s1.id
where a1.street_number = a0.street_number
	and a1.street_normalized = a0.street_normalized
	and a1.municipality = a0.municipality
	and a1.governing_district = a0.governing_district
	and (a1.postal_area = '' or a0.postal_area = '')
	and round(a1.longitude,1) = round(a0.longitude,1)
	and round(a1.latitude,1) = round(a0.latitude,1)
	and not exists (
		select 1 from stores_matched m 
		where m.june2011_store_id = s0.id
			and m.oct2012_store_id = s1.id	
	);


declare @sql nvarchar(max) = N'
select match_type, COUNT(distinct june2011_store_id) as count_june2011_stores_matched
from stores_matched
group by match_type
with rollup
order by match_type;

select c.id as company_id
	, c.name as company_name
	, s0.id as june2011_store_id
	, a0.id as june_2011_address_id
	, a0.fulladdress
	, a0.latitude
	, a0.longitude
from retaildb_test_june2011.dbo.stores s0
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c on c.id = s0.company_id
where not exists (
	select 1 from stores_matched m
	where m.june2011_store_id = s0.id
	);'
exec sp_executesql @sql;