use matching;

----select c0.name
----	, s0.id as biglots_june2011_store_id
----	, a0.fulladdress as biglots_june2011_address
----	, away_c0.name as june2011_competitive_company
----	, count(distinct away_s0.id) as june2011_count_competitive_stores
----	, c1.name
----	, s1.id as biglots_oct2012_store_id
----	, a1.fulladdress as biglots_oct2012_address
----	, count(distinct away_s1.id) as oct2012_count_competitive_stores
--select distinct c0.name
--	, s0.id as biglots_june2011_store_id
--	, a0.fulladdress as biglots_june2011_address
--	, away_c0.name as june2011_competitive_company
--	, c1.name
--	, s1.id as biglots_oct2012_store_id
--	, a1.fulladdress as biglots_oct2012_address
--from stores_matched_by_manila m with (nolock)

--inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.june_id
--inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
--inner join retaildb_test_june2011.dbo.companies c0 on c0.id = s0.company_id
--	and c0.id = 2 --BIG LOTS
--inner join retaildb_test_june2011.dbo.competitive_stores cs0 on cs0.home_store_id = s0.id
--inner join retaildb_test_june2011.dbo.stores away_s0 on away_s0.id = cs0.away_store_id
--inner join retaildb_test_june2011.dbo.companies away_c0 on away_c0.id = away_s0.company_id
--	and away_c0.id in (3,4,5) --Dollar General, Dollar Tree, Family Dollar
	
--inner join retaildb_test_oct2012.dbo.stores s1 on s1.id = m.oct_id
--inner join retaildb_test_oct2012.dbo.addresses_vw a1 on a1.store_id = s1.id
--inner join retaildb_test_oct2012.dbo.companies c1 on c1.id = s1.company_id
--	and c1.id = 2 --BIG LOTS (double check)
--inner join retaildb_test_oct2012.dbo.competitive_stores cs1 on cs1.home_store_id = s1.id
--inner join retaildb_test_oct2012.dbo.stores away_s1 on away_s1.id = cs1.away_store_id
--inner join retaildb_test_oct2012.dbo.companies away_c1 on away_c1.id = away_s1.company_id
--	and away_c1.id in (3,4,5) --Dollar General, Dollar Tree, Family Dollar

----group by c0.name, s0.id, a0.fulladdress, away_c0.name, c1.name, s1.id, a1.fulladdress
----order by c0.name, s0.id, a0.fulladdress, away_c0.name, c1.name, s1.id, a1.fulladdress
--;

----select * from retaildb_test_oct2012.dbo.companies
----id	ticker	name
----3		Dollar General
----4		Dollar Tree
----5		Family Dollar





--select distinct c0.name
--	, s0.id as biglots_june2011_store_id
--	, a0.fulladdress as biglots_june2011_address
--	, away_c0.name as june2011_competitive_company
--	, c1.name
--	, s1.id as biglots_oct2012_store_id
--	, a1.fulladdress as biglots_oct2012_address
--from stores_matched_by_manila m with (nolock)

--inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.june_id
--inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
--inner join retaildb_test_june2011.dbo.companies c0 on c0.id = s0.company_id
--	and c0.id = 2 --BIG LOTS
--inner join retaildb_test_june2011.dbo.competitive_stores cs0 on cs0.home_store_id = s0.id
--inner join retaildb_test_june2011.dbo.stores away_s0 on away_s0.id = cs0.away_store_id
--inner join retaildb_test_june2011.dbo.companies away_c0 on away_c0.id = away_s0.company_id
--	and away_c0.id in (3,4,5) --Dollar General, Dollar Tree, Family Dollar
	
--inner join retaildb_test_oct2012.dbo.stores s1 on s1.id = m.oct_id
--inner join retaildb_test_oct2012.dbo.addresses_vw a1 on a1.store_id = s1.id
--inner join retaildb_test_oct2012.dbo.companies c1 on c1.id = s1.company_id
--	and c1.id = 2 --BIG LOTS (double check)
--inner join retaildb_test_oct2012.dbo.competitive_stores cs1 on cs1.home_store_id = s1.id
--inner join retaildb_test_oct2012.dbo.stores away_s1 on away_s1.id = cs1.away_store_id
--inner join retaildb_test_oct2012.dbo.companies away_c1 on away_c1.id = away_s1.company_id
--	and away_c1.id in (3,4,5) --Dollar General, Dollar Tree, Family Dollar
--; --3486
	

--select c0.name
--	, s0.id as biglots_june2011_store_id
--	, a0.fulladdress as biglots_june2011_address
--	, away_c0.name as june2011_competitive_company
--	, away_s0.id as june2011_competitive_store_id
--	, away_a0.fulladdress as june2011_competitive_address
--	, cs0.travel_time as june2011_travel_time
--	, c1.name
--	, s1.id as biglots_oct2012_store_id
--	, a1.fulladdress as biglots_oct2012_address
--	, away_c1.name as oct2012_competitive_company
--	, away_s1.id as oct2012_competitive_store_id
--	, away_a1.fulladdress as oct2012_competitive_address
--	, cs1.travel_time as oct2012_travel_time
--from stores_matched_by_manila m with (nolock)

--inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.june_id
--inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
--inner join retaildb_test_june2011.dbo.companies c0 on c0.id = s0.company_id
--	and c0.id = 2 --BIG LOTS
--inner join retaildb_test_june2011.dbo.competitive_stores cs0 on cs0.home_store_id = s0.id
--inner join retaildb_test_june2011.dbo.stores away_s0 on away_s0.id = cs0.away_store_id
--inner join retaildb_test_june2011.dbo.addresses_vw away_a0 on away_a0.store_id = away_s0.id
--inner join retaildb_test_june2011.dbo.companies away_c0 on away_c0.id = away_s0.company_id
--	and away_c0.id in (3,4,5) --Dollar General, Dollar Tree, Family Dollar

--inner join stores_matched_by_manila m2_away_s0 with (nolock) on m2_away_s0.june_id = cs0.away_store_id

--inner join retaildb_test_oct2012.dbo.stores s1 on s1.id = m.oct_id
--inner join retaildb_test_oct2012.dbo.addresses_vw a1 on a1.store_id = s1.id
--inner join retaildb_test_oct2012.dbo.companies c1 on c1.id = s1.company_id
--	and c1.id = 2 --BIG LOTS (double check)
--inner join retaildb_test_oct2012.dbo.competitive_stores cs1 on cs1.home_store_id = s1.id
--inner join retaildb_test_oct2012.dbo.stores away_s1 on away_s1.id = cs1.away_store_id
--	and away_s1.id <> m2_away_s0.oct_id --not the same competition as before
--inner join retaildb_test_oct2012.dbo.addresses_vw away_a1 on away_a1.store_id = away_s1.id
--inner join retaildb_test_oct2012.dbo.companies away_c1 on away_c1.id = away_s1.company_id
--	and away_c1.id in (3,4,5) --Dollar General, Dollar Tree, Family Dollar
--order by a0.fulladdress, c1.name, a1.fulladdress
--; --
	


--basic june report 
--big lots stores with dollar-store competitors 
select distinct c0.name
	, s0.id as biglots_june2011_store_id
	, a0.fulladdress as biglots_june2011_address
	, away_c0.name as june2011_competitive_company
	, away_s0.id as june2011_competitive_store_id
	, away_a0.fulladdress as june2011_competitive_address
	, cs0.travel_time as june2011_travel_time
	, m.oct_id as biglots_oct2012_store_id
into biglots_june2011_dollar_store_competitors
from stores_matched_by_manila m with (nolock)
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.june_id
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
inner join retaildb_test_june2011.dbo.companies c0 on c0.id = s0.company_id
	and c0.id = 2 --BIG LOTS
inner join retaildb_test_june2011.dbo.competitive_stores cs0 on cs0.home_store_id = s0.id
inner join retaildb_test_june2011.dbo.stores away_s0 on away_s0.id = cs0.away_store_id
inner join retaildb_test_june2011.dbo.addresses_vw away_a0 on away_a0.store_id = away_s0.id
inner join retaildb_test_june2011.dbo.companies away_c0 on away_c0.id = away_s0.company_id
	and away_c0.id in (3,4,5) --Dollar General, Dollar Tree, Family Dollar
order by a0.fulladdress, away_c0.name, away_a0.fulladdress
; --26562

create nonclustered index IX_biglots_oct2012_store_id on biglots_june2011_dollar_store_competitors (biglots_oct2012_store_id);
create nonclustered index IX_biglots_june2011_store_id on biglots_june2011_dollar_store_competitors (biglots_june2011_store_id);

select *
from biglots_june2011_dollar_store_competitors;



--basic oct report 
--big lots stores with dollar-store competitors
--that also existed in the jun db
select distinct c1.name
	, s1.id as biglots_oct2012_store_id
	, a1.fulladdress as biglots_oct2012_address
	, away_c1.name as oct2012_competitive_company
	, away_s1.id as oct2012_competitive_store_id
	, away_a1.fulladdress as oct2012_competitive_address
	, cs1.travel_time as oct2012_travel_time
	, m.june_id as biglots_june2011_store_id
into biglots_oct2012_dollar_store_competitors
from stores_matched_by_manila m with (nolock)
inner join retaildb_test_oct2012.dbo.stores s1 on s1.id = m.oct_id
inner join retaildb_test_oct2012.dbo.addresses_vw a1 on a1.store_id = s1.id
inner join retaildb_test_oct2012.dbo.companies c1 on c1.id = s1.company_id
	and c1.id = 2 --BIG LOTS (double check)
inner join retaildb_test_oct2012.dbo.competitive_stores cs1 on cs1.home_store_id = s1.id
inner join retaildb_test_oct2012.dbo.stores away_s1 on away_s1.id = cs1.away_store_id
inner join retaildb_test_oct2012.dbo.addresses_vw away_a1 on away_a1.store_id = away_s1.id
inner join retaildb_test_oct2012.dbo.companies away_c1 on away_c1.id = away_s1.company_id
	and away_c1.id in (3,4,5) --Dollar General, Dollar Tree, Family Dollar
; --29575


create nonclustered index IX_biglots_oct2012_store_id on biglots_oct2012_dollar_store_competitors (biglots_oct2012_store_id);
create nonclustered index IX_biglots_june2011_store_id on biglots_oct2012_dollar_store_competitors (biglots_june2011_store_id);


select * 
from biglots_oct2012_dollar_store_competitors;











select *
from biglots_june2011_dollar_store_competitors
where biglots_oct2012_store_id = 25798;

select * 
from biglots_oct2012_dollar_store_competitors
where biglots_oct2012_store_id = 25798;






select biglots_oct2012_store_id, count(distinct june2011_competitive_store_id) cnt_june2011_competitors
from biglots_june2011_dollar_store_competitors
group by biglots_oct2012_store_id
order by biglots_oct2012_store_id;

select biglots_oct2012_store_id, count(distinct oct2012_competitive_store_id) cnt_oct2012_competitors
from biglots_oct2012_dollar_store_competitors
group by biglots_oct2012_store_id
order by biglots_oct2012_store_id;




select *
from biglots_june2011_dollar_store_competitors
where biglots_oct2012_store_id = 25323
order by june2011_competitive_address;

select * 
from biglots_oct2012_dollar_store_competitors
where biglots_oct2012_store_id = 25323
order by oct2012_competitive_address;



select * from dbo.stores_matched_by_manila
where oct_id = 41614	--109 44th Street Sw, Wyoming, MI 49548

--select * from dbo.stores_matched_by_manila
--where oct_id between 41000 and 42000




with june2011 as (
	select biglots_oct2012_store_id, count(distinct june2011_competitive_store_id) cnt_june2011_dollar_store_competitors
	from biglots_june2011_dollar_store_competitors
	group by biglots_oct2012_store_id
), oct2012 as (
	select biglots_oct2012_store_id, count(distinct oct2012_competitive_store_id) cnt_oct2012_dollar_store__competitors
	from biglots_oct2012_dollar_store_competitors
	group by biglots_oct2012_store_id
)
select june2011.biglots_oct2012_store_id
	, a.fulladdress
	, june2011.cnt_june2011_dollar_store_competitors
	, oct2012.cnt_oct2012_dollar_store__competitors
	, case when oct2012.cnt_oct2012_dollar_store__competitors < june2011.cnt_june2011_dollar_store_competitors
		then 'decreased competition' 
		when oct2012.cnt_oct2012_dollar_store__competitors > june2011.cnt_june2011_dollar_store_competitors
		then 'increased competition'
		when oct2012.cnt_oct2012_dollar_store__competitors = june2011.cnt_june2011_dollar_store_competitors 
		then 'same competition'
		end as competition_changed
from june2011
inner join oct2012 on oct2012.biglots_oct2012_store_id = june2011.biglots_oct2012_store_id
inner join retaildb_test_oct2012.dbo.addresses_vw a on a.store_id = june2011.biglots_oct2012_store_id
order by june2011.biglots_oct2012_store_id;
 
 
 
 
 
 
select *
from biglots_june2011_dollar_store_competitors
order by biglots_oct2012_store_id;

select * 
from biglots_oct2012_dollar_store_competitors
order by biglots_oct2012_store_id;
