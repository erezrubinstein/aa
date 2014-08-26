/*
Duplicate address check investigation script
--------------------------------------------
2013-01-09 jsternberg
--------------------------------------------
This script explains how to look at bad data from a staging build.
The check looks for potentially duplicate address records, 
as defined by: 

multiple rows in the addresses table with:

1. different address_id's

2. the same:
	a. street number
	b. street
	c. suite (with NULL == '')
	d. shopping center (with NULL == '')
	e. city (aka municipality)
	f. state (aka governing_district)
	g. zip_code (aka postal_area)
	
3. AND are attached to stores for 1 company
*/

--review bad data entries
select * from data_check_types where data_check_type_id = 3;
select * from data_checks where data_check_type_id = 3 and bad_data_rows > 0;
select * 
from data_checks dc
inner join data_check_values dv on dv.data_check_id = dc.data_check_id
where dc.data_check_type_id = 3 and dc.bad_data_rows > 0;

--joined to the actual address table via entity_id:
select a.*
from data_checks dc
inner join data_check_values dv on dv.data_check_id = dc.data_check_id
inner join addresses a on a.address_id = dv.entity_id
where dc.data_check_type_id = 3 and dc.bad_data_rows > 0;


--re-run the bad data check itself interactively
with dupes as
(
select s.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area, count(*) cnt
from addresses a
inner join stores s on s.address_id = a.address_id
group by s.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area
having count(*) > 1
)
select a.address_id as id, c.company_id, c.name, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area, d.cnt
from addresses a 
inner join stores s on s.address_id = a.address_id
inner join dupes as d on a.street_number = d.street_number
	and a.street = d.street
	and a.municipality = d.municipality
	and a.governing_district = d.governing_district
	and a.postal_area = d.postal_area	
inner join companies c on c.company_id = d.company_id and c.company_id = s.company_id
order by c.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area
;


--explore sample bad data -- step 1: 
select *
from addresses a
inner join stores s on s.address_id = a.address_id
where a.address_id in (167, 173, 191);

--example output (first few columns):
--address_id	street_number	street	municipality	governing_district	postal_area	country_id	latitude	longitude	created_at	updated_at	suite	shopping_center_name
--167	1	Premium Outlet Blvd	Wrentham	MA	02093	NULL	42.038962	-71.352388	2013-01-09 05:13:17.113	2013-01-09 05:13:17.113	NULL	Wrentham Village
--167	1	Premium Outlet Blvd	Wrentham	MA	02093	NULL	42.038962	-71.352388	2013-01-09 05:13:17.113	2013-01-09 05:13:17.113	NULL	Wrentham Village
--173	10000	Research Boulevard	Austin	TX	78759	NULL	30.392862	-97.748742	2013-01-09 05:13:17.457	2013-01-09 05:13:17.457	NULL	NULL
--173	10000	Research Boulevard	Austin	TX	78759	NULL	30.392862	-97.748742	2013-01-09 05:13:17.457	2013-01-09 05:13:17.457	NULL	NULL
--191	10250	Santa Monica Blvd	Los Angeles	CA	90067	NULL	34.059318	-118.418556	2013-01-09 05:13:18.477	2013-01-09 05:13:18.477	NULL	NULL
--191	10250	Santa Monica Blvd	Los Angeles	CA	90067	NULL	34.059318	-118.418556	2013-01-09 05:13:18.477	2013-01-09 05:13:18.477	NULL	NULL


select sf.full_path, sf.source_file_id, a.*, acl.*
from addresses a
inner join addresses_change_log acl on acl.address_id = a.address_id
inner join source_files sf on sf.source_file_id = acl.source_file_id
where a.address_id in (167, 173, 191);



--proposed modification of bad data check logic:
--add suite and shopping center

with dupes as
(
select s.company_id, a.street_number, a.street, a.suite, a.shopping_center_name, a.municipality, a.governing_district, a.postal_area, count(*) cnt
from addresses a
inner join stores s on s.address_id = a.address_id
group by s.company_id, a.street_number, a.street, a.municipality, a.suite, a.shopping_center_name, a.governing_district, a.postal_area
having count(*) > 1
)
select a.address_id as id, c.company_id, c.name, a.street_number, a.street, a.suite, a.shopping_center_name, a.municipality, a.governing_district, a.postal_area, d.cnt
from addresses a 
inner join stores s on s.address_id = a.address_id
inner join dupes as d on a.street_number = d.street_number
	and a.street = d.street
	and coalesce(a.suite,'') = coalesce(d.suite,'')
	and coalesce(a.shopping_center_name,'') = coalesce(d.shopping_center_name,'')
	and a.municipality = d.municipality
	and a.governing_district = d.governing_district
	and a.postal_area = d.postal_area	
inner join companies c on c.company_id = d.company_id and c.company_id = s.company_id
order by c.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area
;

select sf.full_path, sf.source_file_id, a.*, acl.*
from addresses a
inner join addresses_change_log acl on acl.address_id = a.address_id
inner join source_files sf on sf.source_file_id = acl.source_file_id
where a.address_id in (167, 8021);

select * 
from source_file_records sfr 
where sfr.source_file_id = 45
	and street_number = '1'
	and street = 'Premium Outlet Blvd'
	and city = 'Wrentham'
	and state = 'MA'
	and zip = '02093';

--only 1 record?
--{"RecordType": "D", "Action": "C", "LoaderRecordID": "None", "Address": "1 Premium Outlet Blvd", "City": "Wrentham", "State": "MA", "Zip": "2093", "Phone": "5083845320", "Country": "None", "MallName": "Wrentham Village", "OpenedOn": "None", "Suite": "None", "CompanyGeneratedStoreNum": "None", "StoreFormat": "Factory Store,Petites", "Note": "None", "Longitude": "-71.351225", "Latitude": "42.03719"}


select * 
from source_file_records sfr 
where sfr.source_file_id = 45
	--and street_number = '1'
	--and street = 'Premium Outlet Blvd'
	and city = 'Wrentham'
	and state = 'MA'
	--and zip = '02093';


--hm... something must be wrong with the check.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


--Conclusion: bug in the dupe check itself! Instead of count(*), we need count(distinct address_id)
--this gets 0 records!

with dupes as
(
select s.company_id, a.street_number, a.street, a.suite, a.shopping_center_name, a.municipality, a.governing_district, a.postal_area, count(distinct a.address_id) cnt
from addresses a
inner join stores s on s.address_id = a.address_id
group by s.company_id, a.street_number, a.street, a.municipality, a.suite, a.shopping_center_name, a.governing_district, a.postal_area
having count(distinct a.address_id) > 1
)
select a.address_id as id, c.company_id, c.name, a.street_number, a.street, a.suite, a.shopping_center_name, a.municipality, a.governing_district, a.postal_area, d.cnt
from addresses a 
inner join stores s on s.address_id = a.address_id
inner join dupes as d on a.street_number = d.street_number
	and a.street = d.street
	and coalesce(a.suite,'') = coalesce(d.suite,'')
	and coalesce(a.shopping_center_name,'') = coalesce(d.shopping_center_name,'')
	and a.municipality = d.municipality
	and a.governing_district = d.governing_district
	and a.postal_area = d.postal_area	
inner join companies c on c.company_id = d.company_id and c.company_id = s.company_id
order by c.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area
;