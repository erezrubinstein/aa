use retaildb_test_june2011
go


--stores that have neither competition relationships nor are flagged as monopolies
select s1.id, s1.company_id
from stores s1
where not exists (
		select 1 from competitive_stores cs where cs.home_store_id = s1.id
	)
	and not exists (
		select 1 from monopolies m where m.store_id = s1.id
	)


--duplicate stores
select s.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area, count(*) cnt
from addresses a
inner join stores s on s.id = a.store_id
group by s.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area
having count(*) > 1;


--stores that don't have basic demographic stats
--means gp1 didn't run successfully for these stores
--should be 0
select count(*) 
from stores s
where not exists (select 1 from [retail_demographic_basic_stats_vw] b where b.store_id = s.id)


--stores that don't have ANY demographic values
--should be 0
select count(*) 
from stores s
inner join trade_areas t on t.store_id = s.id
where not exists (select 1 from demographic_numvalues nv where nv.trade_area_id = t.id)


--stores that don't have trade areas
--should be 0
select count(*) 
from stores s
where not exists (select 1 from trade_areas t where t.store_id = s.id)


--stores that don't have addresses
--should be 0
select count(*)
from stores s
where not exists (select 1 from addresses a where a.store_id = s.id)


--addresses that point to missing stores
select count(*)
from addresses a
where not exists (select 1 from stores s where s.id = a.store_id)


--competitions that point to missing companies
select count(*)
from competitions cmp
where not exists (select 1 from companies c where c.id = cmp.home_company_id)


--competitions that point to missing companies
select count(*)
from competitions cmp
where not exists (select 1 from companies c where c.id = cmp.away_company_id)

	
--competitive_stores that point to missing stores
select count(*)
from competitive_stores cmp
where not exists (select 1 from stores s where s.id = cmp.home_store_id)


--competitive_stores that point to missing stores
select count(*)
from competitive_stores cmp
where not exists (select 1 from stores s where s.id = cmp.away_store_id)


--stores that have < 10 population (probably geocoded in the ocean)
select * from qa_report_demographics_vw where home_population < 10



