use retaildb_timeseries_dev
go


--stores that have neither competition relationships nor are flagged as monopolies
select s1.store_id as id
from stores s1
where not exists (
		select 1 from competitive_stores cs where cs.home_store_id = s1.store_id
	)
	and not exists (
		select 1 from monopolies m where m.store_id = s1.store_id
	)

--duplicate addresses
with dupes as
(
select street_number, street, municipality, governing_district, postal_area, count(*) cnt
from addresses
group by street_number, street, municipality, governing_district, postal_area
having count(*) > 1)
select a.address_id as id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area, d.cnt 
from addresses a inner join dupes as d on 
a.street_number = d.street_number
and a.street = d.street
and a.municipality = d.municipality
and a.governing_district = d.governing_district
and a.postal_area = d.postal_area
;



--stores that don't have basic demographic stats
--means gp1 didn't run successfully for these stores
--should be 0
select s.store_id as id
from stores s
where not exists (select 1 from [retail_demographic_basic_stats_vw] b where b.store_id = s.store_id)


--stores that don't have ANY demographic values
--should be 0
select s.store_id as id
from stores s
inner join trade_areas t on t.store_id = s.store_id
where not exists (select 1 from demographic_numvalues nv where nv.trade_area_id = t.store_id)


--stores that don't have trade areas
--should be 0
select s.store_id as id
from stores s
where not exists (select 1 from trade_areas t where t.store_id = s.store_id)


--stores that don't have addresses
--should be 0
select store_id as id
from stores
where address_id is null


--competitions that point to missing companies
select cmp.id as id
from competitions cmp
where not exists (select 1 from companies c where c.company_id = cmp.home_company_id)


--competitions that point to missing companies
select cmp.id as id
from competitions cmp
where not exists (select 1 from companies c where c.company_id = cmp.away_company_id)

	
--competitive_stores that point to missing stores
select cmp.away_store_id as id
from competitive_stores cmp
where not exists (select 1 from stores s where s.store_id = cmp.home_store_id)


--competitive_stores that point to missing stores
select cmp.home_store_id as id
from competitive_stores cmp
where not exists (select 1 from stores s where s.store_id = cmp.away_store_id)


--stores that have < 10 population (probably geocoded in the ocean)
select store_id as id from qa_report_demographics_vw where home_population < 10



delete from data_check_types where data_check_type_id >= 2











select * from addresses where --nullif(street, '') is not null and 
(left(street,1) = ' ' or right(street,1) = ' ')




select * from addresses where nullif(postal_area, '') is not null and (LEFT(postal_area,1) = ' ' or right(postal_area,1) = ' ')
