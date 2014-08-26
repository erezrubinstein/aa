use LL_OCT3_CMA_100213
go

create table #other_stores(project_id int, company_id int, store_id int, g geography, primary key(project_id, company_id, store_id))

-- mattress
insert into #other_stores
select 1, s.company_id,s. store_id,
	geography::STPointFromText('POINT(' + CAST(a.longitude AS VARCHAR(20)) + ' ' + CAST(a.latitude AS VARCHAR(20)) + ')', 4326)
from MATTRESS_JUL13_CMA_061913.dbo.stores s
inner join MATTRESS_JUL13_CMA_061913.dbo.addresses a on a.address_id = s.address_id
where s.company_id in (64, 65, 66)

-- TTS
insert into #other_stores
select 2, s.company_id,s. store_id,
	geography::STPointFromText('POINT(' + CAST(a.longitude AS VARCHAR(20)) + ' ' + CAST(a.latitude AS VARCHAR(20)) + ')', 4326)
from TTS_AUG13_CMA_080413.dbo.stores s
inner join TTS_AUG13_CMA_080413.dbo.addresses a on a.address_id = s.address_id
where s.company_id in (73, 74, 75, 72, 70, 84, 77, 68, 85, 69, 78, 67, 76, 71, 80, 66, 81, 64, 83)

-- LOW-OSH
insert into #other_stores
select 3, s.company_id,s. store_id,
	geography::STPointFromText('POINT(' + CAST(a.longitude AS VARCHAR(20)) + ' ' + CAST(a.latitude AS VARCHAR(20)) + ')', 4326)
from LOWOSH_JUL13_CMA_073013.dbo.stores s
inner join LOWOSH_JUL13_CMA_073013.dbo.addresses a on a.address_id = s.address_id
where s.company_id in (9, 2, 6, 5, 7, 8, 3, 12, 1, 10, 4, 11)

-- home centers
insert into #other_stores
select 4, s.company_id,s. store_id,
	geography::STPointFromText('POINT(' + CAST(a.longitude AS VARCHAR(20)) + ' ' + CAST(a.latitude AS VARCHAR(20)) + ')', 4326)
from HOMECENT_JUL13_CMA_072213.dbo.stores s
inner join HOMECENT_JUL13_CMA_072213.dbo.addresses a on a.address_id = s.address_id
where s.company_id in (65, 64, 66, 67)

-- ll stores
create table #ll_stores(company_id int, store_id int, g geography, primary key(company_id, store_id))
insert into #ll_stores
select s.company_id,s. store_id,
	geography::STPointFromText('POINT(' + CAST(a.longitude AS VARCHAR(20)) + ' ' + CAST(a.latitude AS VARCHAR(20)) + ')', 4326)
from stores s
inner join addresses a on a.address_id = s.address_id
where s.company_id in (65)


-- index time!
CREATE SPATIAL INDEX index_spacial ON #ll_stores(g)
CREATE SPATIAL INDEX index_spacial ON #other_stores(g)

-- find matches
create table #store_search_pairs (home_store_id int, away_project_id int, away_store_id int, home_geography geography, away_geography geography, primary key(home_store_id, away_project_id, away_store_id))

insert into #store_search_pairs
select s.store_id, s_away.project_id, s_away.store_id, s.g, s_away.g
from #ll_stores s
inner join #other_stores s_away WITH (INDEX(index_spacial)) on s.g.STDistance(s_away.g) < 10000 


-- claculate distances and minimum distances
create table #distances(store_id int primary key, other_project_id int, closest_store_id int, distance float)
insert into #distances
select 
	s.store_id,
	closest_store.away_project_id,
	closest_store.away_store_id as closest_store_id, 
	closest_store.distance
from #ll_stores s
outer apply
(
	select top 1 s2.away_store_id, 
		s2.home_geography.STDistance(s2.away_geography) as distance,
		s2.away_project_id
	from #store_search_pairs s2
	where s2.home_store_id = s.store_id
	order by distance
) closest_store



---- nice query to show pairs and home/away details
--select 
--	c.name as company,
--	s.store_id,
--	isnull(s.phone_number, '') as phone_number,
--	a.street_number, 
--	a.street,
--	a.municipality as city,
--	a.governing_district as state,
--	a.postal_area as zip,
--	a.latitude,
--	a.longitude,
--	d.closest_store_id,
	--case 
	--	when d.other_project_id = 1 then 'SCSS'
	--	when d.other_project_id = 2 then 'TTS'
	--	when d.other_project_id = 3 then 'LOW-OSH'
	--	when d.other_project_id = 4 then 'home centers'
	--	else 'oops'
	--end as matching_project, 
--	d.distance as distance_meters
--from stores s
--inner join #distances d on d.store_id = s.store_id
--inner join addresses a on a.address_id = s.address_id
--inner join companies c on c.company_id = s.company_id
--order by isnull(d.distance, 10000000), a.postal_area, a.governing_district, a.municipality, a.street




-- get demographics from other databases

create table #demographics (trade_area_id int NOT NULL, data_item_id int NOT NULL, value decimal(21, 8) NOT NULL, created_at datetime NOT NULL, updated_at datetime NOT NULL, segment_id int NULL, period_id int NOT NULL, target_period_id int NULL, template_name varchar(100) NOT NULL)

insert into #demographics (trade_area_id, data_item_id, value, created_at, updated_at, segment_id, period_id, target_period_id, template_name)
select t.trade_area_id, d.data_item_id, d.value, GETUTCDATE(), GETUTCDATE(), d.segment_id, d.period_id, d.target_period_id, d.template_name
from #distances dist
inner join trade_areas t on t.store_id = dist.store_id and t.threshold_id = 1
left join MATTRESS_JUL13_CMA_061913.dbo.trade_areas ta on ta.store_id = dist.closest_store_id and ta.threshold_id = 1
left join MATTRESS_JUL13_CMA_061913.dbo.demographic_numvalues d on d.trade_area_id = ta.trade_area_id and d.template_name = 'acs_housing'
where dist.other_project_id = 1

insert into #demographics (trade_area_id, data_item_id, value, created_at, updated_at, segment_id, period_id, target_period_id, template_name)
select t.trade_area_id, d.data_item_id, d.value, GETUTCDATE(), GETUTCDATE(), d.segment_id, d.period_id, d.target_period_id, d.template_name
from #distances dist
inner join trade_areas t on t.store_id = dist.store_id and t.threshold_id = 1
left join TTS_AUG13_CMA_080413.dbo.trade_areas ta on ta.store_id = dist.closest_store_id and ta.threshold_id = 1
left join TTS_AUG13_CMA_080413.dbo.demographic_numvalues d on d.trade_area_id = ta.trade_area_id and d.template_name = 'acs_housing'
where dist.other_project_id = 2

insert into #demographics (trade_area_id, data_item_id, value, created_at, updated_at, segment_id, period_id, target_period_id, template_name)
select t.trade_area_id, d.data_item_id, d.value, GETUTCDATE(), GETUTCDATE(), d.segment_id, d.period_id, d.target_period_id, d.template_name
from #distances dist
inner join trade_areas t on t.store_id = dist.store_id and t.threshold_id = 1
left join LOWOSH_JUL13_CMA_073013.dbo.trade_areas ta on ta.store_id = dist.closest_store_id and ta.threshold_id = 1
left join LOWOSH_JUL13_CMA_073013.dbo.demographic_numvalues d on d.trade_area_id = ta.trade_area_id and d.template_name = 'acs_housing'
where dist.other_project_id = 3

insert into #demographics (trade_area_id, data_item_id, value, created_at, updated_at, segment_id, period_id, target_period_id, template_name)
select t.trade_area_id, d.data_item_id, d.value, GETUTCDATE(), GETUTCDATE(), d.segment_id, d.period_id, d.target_period_id, d.template_name
from #distances dist
inner join trade_areas t on t.store_id = dist.store_id and t.threshold_id = 1
left join HOMECENT_JUL13_CMA_072213.dbo.trade_areas ta on ta.store_id = dist.closest_store_id and ta.threshold_id = 1
left join HOMECENT_JUL13_CMA_072213.dbo.demographic_numvalues d on d.trade_area_id = ta.trade_area_id and d.template_name = 'acs_housing'
where dist.other_project_id = 4


insert into demographic_numvalues (trade_area_id, data_item_id, value, created_at, updated_at, segment_id, period_id, target_period_id, template_name)
select trade_area_id, data_item_id, value, created_at, updated_at, segment_id, period_id, target_period_id, template_name
from #demographics order by trade_area_id, data_item_id


-- killer
/*
drop table #demographics
drop table #other_stores
drop table #ll_stores
drop table #store_search_pairs
drop table #distances
*/