use LL_OCT3_CMA_100213
go

-- declare companies
declare @companies table(company_id int primary key)
insert into @companies 

--auto parts
--select 70 union all
--select 71 union all
--select 72 union all
--select 74 union all
--select 75 union all
--select 78 union all
--select 79 union all
--select 80

--all companies
select company_id from companies

--main home centers
--select 64 union all
--select 65 union all
--select 66 

----dollar convinience
--select 75
--select 74
--select 68

----main dollar companies
--select 65 union all
--select 67 union all
--select 70 union all
--select 71 union all
--select 77 union all
--select 78 union all
--select 80 union all
--select 81 


-- find all stores and calculate geography
create table #stores_w_format(company_id int, store_id int, store_format varchar(500), g geography, primary key(company_id, store_id, store_format))
insert into #stores_w_format
select s.company_id,s. store_id, isnull(s.store_format, ''),
	geography::STPointFromText('POINT(' + CAST(a.longitude AS VARCHAR(20)) + ' ' + CAST(a.latitude AS VARCHAR(20)) + ')', 4326)
from stores s
inner join addresses a on a.address_id = s.address_id
where s.company_id in (select company_id from @companies) and s.assumed_closed_date is null


-- create spacial index
CREATE SPATIAL INDEX index_spacial ON #stores_w_format(g)


-- declare table for search pairs
create table #store_search_pairs (home_store_id int, away_store_id int, home_geography geography, away_geography geography, primary key(home_store_id, away_store_id))

-- init loop variables
declare @search_bounds float = 0
declare @search_bounds_increment float = 5000
declare @message varchar(100) = ''

-- begin finding stores at ranges of 3K meters from each other.  Keep going until 10X meters or itteration finds less than 1K.
-- this makes the algorithm not be o(N^2)
WHILE @search_bounds < @search_bounds_increment * 20 and (@search_bounds = 0 or @@ROWCOUNT > 100)
BEGIN
	
	-- keep incrementing degree by 1000 meters until you find some stores
	set @search_bounds = @search_bounds + @search_bounds_increment
	
	-- print by using raiserror, which flushes right away
	set @message = 'searchbounds = ' + cast(@search_bounds as varchar(10))
	RAISERROR(@message ,0,1) WITH NOWAIT
	
	-- don't always keep searching... have a "last case"
	insert into #store_search_pairs
	select s.store_id, s_away.store_id, s.g, s_away.g
	from #stores_w_format s
	inner join #stores_w_format s_away WITH (INDEX(index_spacial))
		on s.g.STDistance(s_away.g) < @search_bounds 
		and s_away.company_id = s.company_id and s_away.store_id <> s.store_id and s_away.store_format = s.store_format
	-- do not insert stores that have already been inserted
	where s.store_id not in (select distinct home_store_id from #store_search_pairs)
END


-- one final search for anything that didn't have matches (i..e the rest)
insert into #store_search_pairs
select s.store_id, s_away.store_id, s.g, s_away.g
from #stores_w_format s
inner join #stores_w_format s_away on s_away.company_id = s.company_id and s_away.store_id <> s.store_id and s_away.store_format = s.store_format
-- do not insert stores that have already been inserted
where s.store_id not in (select distinct home_store_id from #store_search_pairs)

-- claculate distances and minimum distances
create table #distances(store_id int primary key, closest_store_id int, distance float)
insert into #distances
select 
	s.store_id,
	closest_store.away_store_id as closest_store_id, 
	closest_store.distance
from stores s
outer apply
(
	select top 1 s2.away_store_id, s2.home_geography.STDistance(s2.away_geography) as distance
	from #store_search_pairs s2
	where s2.home_store_id = s.store_id
	order by distance
) closest_store
where s.company_id in (select company_id from @companies) and s.assumed_closed_date is null


-- nice query to show pairs and home/away details
select 
	c.name as company,
	s.store_id,
	d.closest_store_id,
	d.distance as distance_meters,
	isnull(s.phone_number, '') as phone_number,
	a.street_number, 
	a.street,
	a.municipality as city,
	a.governing_district as state,
	a.postal_area as zip,
	a.latitude,
	a.longitude,
	ISNULL(s.note, '') as note,
	ISNULL(s.store_format, '') as store_format,
	ISNULL(a.shopping_center_name, '') as mall,
	isnull(away_store.phone_number, '') as away_phone_number,
	away_a.street_number as away_street_number, 
	away_a.street as away_street,
	away_a.municipality as away_city,
	away_a.governing_district as away_state,
	away_a.postal_area as away_zip,
	away_a.latitude as away_lat,
	away_a.longitude as away_long,
	ISNULL(away_store.note, '') as away_note,
	ISNULL(away_store.store_format, '') as away_store_format,
	ISNULL(away_a.shopping_center_name, '') as away_mall
from stores s
inner join #distances d on d.store_id = s.store_id
inner join addresses a on a.address_id = s.address_id
inner join companies c on c.company_id = s.company_id
left join stores away_store on away_store.store_id = d.closest_store_id
left join addresses away_a on away_a.address_id = away_store.address_id
order by isnull(d.distance, 10000000), a.postal_area, a.governing_district, a.municipality, a.street

-- drop those guys!
drop table #distances
drop table #store_search_pairs
drop table #stores_w_format