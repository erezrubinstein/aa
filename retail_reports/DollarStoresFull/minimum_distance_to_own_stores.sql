use DOLLFULL_JUN13_CMA_062313
go

create table #stores(company_id int, store_id int, g geography, primary key(company_id, store_id))
insert into #stores
select s.company_id,s. store_id, geography::STPointFromText('POINT(' + CAST(a.longitude AS VARCHAR(20)) + ' ' + CAST(a.latitude AS VARCHAR(20)) + ')', 4326)
from stores s
inner join addresses a on a.address_id = s.address_id
where s.company_id in (70, 81, 67, 65)


select 
	s.company_id, 
	s.store_id, 
	closest_store.store_id as closest_store_id, 
	closest_store.company_id as closest_company_id, 
	closest_store.distance
from #stores s
cross apply
(
	select top 1 s2.company_id, s2.store_id, s.g.STDistance(s2.g) as distance
	from #stores s2
	where s2.company_id = s.company_id and s2.store_id <> s.store_id
	order by distance
) closest_store


drop table #stores