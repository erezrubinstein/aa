use retaildb_test_june2011;

---WARNING the bottom of this script destroys the database!!!
select name + '--', * from companies
--update companies set name = 'HomeGoods' where id = 7;

select count(*) as companies from companies with (nolock); --14
select count(*) as competitions from competitions with (nolock); --196
select count(*) as stores from stores with (nolock); --30337

select s.company_id, c.name, count(*) as count_stores
from retaildb_test_june2011.dbo.stores s with (nolock)
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s.company_id
group by s.company_id, c.name
order by c.name;

--company_id	name	count_stores
--1	99 Cents Only Stores	285
--2	BIG LOTS	1415
--3	DOLLAR GENERAL	9479
--4	DOLLAR TREE	3941
--5	FAMILY DOLLAR	6764
--6	FRED'S	512
--7	HomeGoods	359
--8	Kmart	1256
--9	OLLIE'S Bargain OUTLET	101
--10	TARGET	1768
--11	TUESDAY MORNING	853
--12	Walmart Discount Store	964
--14	Walmart Supercenter	2640


select s.company_id, c.name, count(*) as count_stores
from retaildb_test_june2011_moptest.dbo.stores s with (nolock)
inner join retaildb_test_june2011_moptest.dbo.companies c with (nolock) on c.id = s.company_id
group by s.company_id, c.name
order by c.name;



select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_june2011.dbo.stores s with (nolock)
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
group by s.company_id, c.name
order by c.name;

select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_june2011_moptest.dbo.stores s with (nolock)
inner join retaildb_test_june2011_moptest.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011_moptest.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
group by s.company_id, c.name
order by c.name;




select s.company_id, c.name, count(*) as count_monopolies
from retaildb_test_june2011.dbo.stores s with (nolock)
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011.dbo.monopolies m with (nolock) on m.store_id = s.id
group by s.company_id, c.name
order by c.name;

select s.company_id, c.name, count(*) as count_monopolies
from retaildb_test_june2011_moptest.dbo.stores s with (nolock)
inner join retaildb_test_june2011_moptest.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011_moptest.dbo.monopolies m with (nolock) on m.store_id = s.id
group by s.company_id, c.name
order by c.name;



select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_june2011.dbo.stores s with (nolock)
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011.dbo.monopolies m with (nolock) on m.store_id = s.id
group by s.company_id, c.name
order by c.name;

select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_june2011_moptest.dbo.stores s with (nolock)
inner join retaildb_test_june2011_moptest.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011_moptest.dbo.monopolies m with (nolock) on m.store_id = s.id
group by s.company_id, c.name
order by c.name;






select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_june2011.dbo.stores s with (nolock)
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011.dbo.monopolies m with (nolock) on m.store_id = s.id
where not exists (
	select 1 from retaildb_test_june2011_moptest.dbo.monopolies m2 with (nolock)
	where m2.store_id = m.store_id
)
group by s.company_id, c.name
order by c.name;


select *
from retaildb_test_june2011.dbo.stores s with (nolock)
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011.dbo.monopolies m with (nolock) on m.store_id = s.id
inner join retaildb_test_june2011.dbo.addresses a with (nolock) on a.store_id = s.id
where not exists (
	select 1 from retaildb_test_june2011_moptest.dbo.monopolies m2 with (nolock)
	where m2.store_id = m.store_id
)
order by c.name;
--id	company_id	address_id	opened_on	phone_number	complex	created_at	updated_at	closed_on	state	note	id	ticker	name	created_at	updated_at	store_id	radius_thresh	created_at	updated_at	complete_flag	monopoly_type_id	id	store_id	street_number	street	municipality	governing_district	postal_area	country_id	latitude	longitude	created_at	updated_at
--101395	2	NULL	NULL	(503) 566-7674		2012-11-05 14:02:57.117	2012-11-05 14:02:57.117	NULL	NULL		2		BIG LOTS	2012-10-22 18:48:17.203	2012-11-05 14:02:47.177	101395	10	2012-11-06 01:06:16.663	2012-11-06 01:06:16.663	1	2	1395	101395	4040	Market Street Northeast	Salem	OR	97301	840	37.2903925	-122.9825715	2012-11-05 14:02:57.120	2012-11-05 14:02:57.120
--116093	5	NULL	NULL	252-756-7117		2012-11-05 14:16:12.467	2012-11-05 14:16:12.467	NULL	NULL		5		FAMILY DOLLAR	2012-10-22 18:48:17.203	2012-11-05 14:16:03.817	116093	10	2012-11-05 22:57:17.913	2012-11-05 22:57:17.913	1	2	16093	116093	655	Worthington Rd	Winterville	NC	28590-7847	840	30.508769	-77.383031	2012-11-05 14:16:12.470	2012-11-05 14:16:12.470



--deleted competitions
select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_june2011.dbo.stores s with (nolock)
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
where not exists (
	select 1 from retaildb_test_june2011_moptest.dbo.competitive_stores cs2 with (nolock)
	where cs2.home_store_id = cs.home_store_id
		and cs.away_store_id = cs.away_store_id
)
group by s.company_id, c.name
order by c.name;


select *
from retaildb_test_june2011.dbo.stores s with (nolock)
inner join retaildb_test_june2011.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
where not exists (
	select 1 from retaildb_test_june2011_moptest.dbo.competitive_stores cs2 with (nolock)
	where cs2.home_store_id = cs.home_store_id
		and cs.away_store_id = cs.away_store_id
)
order by c.name;

--home
select * from addresses_vw where store_id in (
105924,
106418
)
--away
select * from addresses_vw where store_id in (
106418,
102898,
105924
)


--check competition store additions

select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_june2011_moptest.dbo.stores s with (nolock)
inner join retaildb_test_june2011_moptest.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011_moptest.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
where not exists (
	select 1 from retaildb_test_june2011.dbo.competitive_stores cs2 with (nolock)
	where cs2.home_store_id = cs.home_store_id
		and cs.away_store_id = cs.away_store_id
)
group by s.company_id, c.name
order by c.name;
--company_id	name	count_competitive_stores
--2	BIG LOTS	12
--5	FAMILY DOLLAR	23

select s.company_id, c.name, a.longitude, a.latitude, count(*) as count_competitive_stores
from retaildb_test_june2011_moptest.dbo.stores s with (nolock)
inner join retaildb_test_june2011_moptest.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_june2011_moptest.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
inner join retaildb_test_june2011_moptest.dbo.addresses a with (nolock) on a.store_id = s.id
where not exists (
	select 1 from retaildb_test_june2011.dbo.competitive_stores cs2 with (nolock)
	where cs2.home_store_id = cs.home_store_id
		and cs.away_store_id = cs.away_store_id
)
group by s.company_id, c.name, a.longitude, a.latitude
order by c.name;

--check lat long range
--check that competition count increased by only 1



--delete from stores where company_id in (7)
--delete from addresses where not exists (select 1 from stores s where s.id = addresses.store_id)
--(1615 row(s) affected)

--check dupe addresses
--select s.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area, count(*) cnt
--from addresses a
--inner join stores s on s.id = a.store_id
--group by s.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area
--having count(*) > 1;

--10	1400	N Hayden Island Dr	Portland	OR	97217	2

--select * from addresses a
--where a.street_number = 1400
--and a.street = 'N Hayden Island Dr'
--and a.municipality = 'Portland'
--and a.governing_district = 'OR'

--select * from stores where id in (26985,26987)
----26985	10	NULL	NULL	5032470331		2012-11-05 14:56:25.577	2012-11-05 14:56:25.577	NULL	NULL	
----26987	10	NULL	NULL	5032470331		2012-11-05 14:56:25.620	2012-11-05 14:56:25.620	NULL	NULL	

----delete from stores where id = 26987
----delete from addresses where store_id = 26987

--demographic load
select count(*) as trade_areas from trade_areas with (nolock) --303
--select count(*) as demographic_profiles from demographic_profiles with (nolock) --303

--proximity load
--select count(*) as competition_instances from competition_instances with (nolock) --12989
--select count(*) as competition_measurements from competition_measurements with (nolock) --12989
--select s.company_id, count(*) as count_competition_instances
--from competition_instances ci with (nolock)
--inner join stores s with (nolock) on s.id = ci.home_store_id 
--group by s.company_id;
-- company_id	count_competition_instances
-- ----------	---------------------------
-- 1				12989

--age by sex load
select count(*) as demographic_profile_segment_values from demographic_profile_segment_values with (nolock) --10908

--new gp1 tables
select count(*) as demographic_numvalues, count(distinct trade_area_id) as distinct_trade_areas from demographic_numvalues
--1714	8
select count(*) as demographic_strvalues, count(distinct trade_area_id) as distinct_trade_areas from demographic_strvalues
--40	8

--new gp2 tables
--
select MIN([travel_time]) as min_travel_time
	, AVG([travel_time]) as avg_travel_time
	, max([travel_time]) 
from competitive_stores with (nolock);

select count(*) as competitive_stores
	, count(distinct home_store_id) as distinct_home_stores  
	, count(distinct away_store_id) as distinct_away_stores
from competitive_stores with (nolock);

select count(*) as monopolies from monopolies with (nolock);

--select top 10 * from competitive_stores


----cleanup after arcpy, redo ruby part 2
--truncate table competition_instances
--truncate table trade_areas
--truncate table demographic_profiles
--truncate table competition_measurements
--truncate table demographic_profile_segment_values

--truncate table demographic_numvalues
--truncate table demographic_strvalues

--truncate table competitive_stores
--truncate table monopolies

--dbcc checkident(demographic_numvalues, reseed, 0)
--dbcc checkident(demographic_strvalues, reseed, 0)

----cleanup everything except companies:
--truncate table stores
--truncate table addresses

--truncate table companies_sectors
--truncate table competitions



--refresh competitions from main db, since I just inserted a bunch of dupes!!!

--begin transaction

--select * from competitions order by 2,3

--truncate table competitions

--set identity_insert competitions on

--insert into competitions (id, home_company_id, away_company_id, strength, created_at, updated_at)
--select id, home_company_id, away_company_id, strength, created_at, updated_at
--from retaildb_test_server.dbo.competitions

--set identity_insert competitions off

--select * from competitions order by 2,3

--commit



--select MIN(id), MAX(id) from retaildb_test_june2011.dbo.stores
----1	31953
--select MIN(id), MAX(id) from retaildb_test_server.dbo.stores
----25020	57526


--begin transaction

--set identity_insert stores on

--insert into stores (id, company_id, address_id, opened_on, phone_number, complex, created_at, updated_at, closed_on, [state], note)
--select id + 100000, company_id, address_id, opened_on, phone_number, complex, created_at, updated_at, closed_on, [state], note
--from stores
--where id < 100000;

--set identity_insert stores off

--update addresses set store_id = store_id + 100000 where store_id < 100000;

--delete from stores where id < 100000;

--select MIN(id), MAX(id) from dbo.stores
----100001 131953
--select MIN(store_id), MAX(store_id) from dbo.addresses

--commit


--select * from demographic_segments


select MAX(created_at) from demographic_numvalues with (nolock) --2012-11-06 12:39:51.680

select CONVERT(char(16), created_at, 120) created_minute, count(distinct trade_area_id) 
from demographic_numvalues with (nolock)
group by CONVERT(char(16), created_at, 120)
order by 1 desc;



--debugging queries:


select * from monopolies;

select * from stores where id = 100018
select * from addresses where store_id = 100018
select * from trade_areas where store_id = 100018

select * from demographic_numvalues v
inner join demographic_types t on t.id = v.demographic_type_id
where trade_area_id = 28927 
order by t.id

select * from demographic_numvalues v
inner join demographic_types t on t.id = v.demographic_type_id
where trade_area_id = 28927 
and demographic_type_id in (
			621, --TOTPOP_CY
			696) --PCI_CY
			
select * from retail_demographic_basic_stats_vw where trade_area_id = 143
select * from retail_demographic_basic_stats where trade_area_id = 143


select count(*) from competitive_stores where home_store_id = 127576



select * from retail_demographic_basic_stats_vw



SELECT *
FROM stores s with (nolock)
where not exists (select 1 from retail_demographic_basic_stats_vw b with (nolock) where b.store_id = s.id)
--and s.id = 129111




select * from trade_areas t where not exists (select 1 from demographic_numvalues nv where nv.trade_area_id = t.id)

select * from demographic_numvalues where trade_area_id = 26932
select * from trade_areas where store_id = 131725
select * from stores where id = 131725










select s.company_id, c.name, count(distinct cs.away_store_id) as count_competitive_stores
from retaildb_test_server_original.dbo.stores s with (nolock)
inner join retaildb_test_server_original.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_server_original.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
group by s.company_id, c.name
order by c.name;

select s.company_id, c.name, count(distinct cs.away_store_id) as count_competitive_stores
from retaildb_test_server.dbo.stores s with (nolock)
inner join retaildb_test_server.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_server.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
group by s.company_id, c.name
order by c.name;




select s.company_id, c.name, count(*) as count_monopolies
from retaildb_test_server_original.dbo.stores s with (nolock)
inner join retaildb_test_server_original.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_server_original.dbo.monopolies m with (nolock) on m.store_id = s.id
group by s.company_id, c.name
order by c.name;

select s.company_id, c.name, count(*) as count_monopolies
from retaildb_test_server.dbo.stores s with (nolock)
inner join retaildb_test_server.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_server.dbo.monopolies m with (nolock) on m.store_id = s.id
group by s.company_id, c.name
order by c.name;


select * from retaildb_test_server.dbo.monopolies where store_id = 42016
select * from retaildb_test_server_original.dbo.monopolies where store_id = 42016

