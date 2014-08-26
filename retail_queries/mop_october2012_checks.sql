
select s.company_id, c.name, count(distinct cs.away_store_id) as original_count_competitive_stores
from retaildb_test_server_original.dbo.stores s with (nolock)
inner join retaildb_test_server_original.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_server_original.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
group by s.company_id, c.name
order by c.name;

select s.company_id, c.name, count(distinct cs.away_store_id) as new_count_competitive_stores
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

select count(*) from retaildb_test_server.dbo.monopolies 
select count(*) from retaildb_test_server_original.dbo.monopolies 



select * from retaildb_test_server.dbo.monopolies where store_id = 42016
select * from retaildb_test_server_original.dbo.monopolies where store_id = 42016

select count(*) from retaildb_test_server.dbo.monopolies 
select count(*) from retaildb_test_server_original.dbo.monopolies 



select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_server.dbo.stores s with (nolock)
inner join retaildb_test_server.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_server.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
where not exists (
	select 1 from retaildb_test_server_original.dbo.competitive_stores cs2 with (nolock)
	where cs2.home_store_id = cs.home_store_id
		and cs.away_store_id = cs.away_store_id
)
group by s.company_id, c.name
order by c.name;



select s.company_id, c.name, count(*) as count_competitive_stores
from retaildb_test_server_original.dbo.stores s with (nolock)
inner join retaildb_test_server_original.dbo.companies c with (nolock) on c.id = s.company_id
inner join retaildb_test_server_original.dbo.competitive_stores cs with (nolock) on cs.home_store_id = s.id
where not exists (
	select 1 from retaildb_test_server.dbo.competitive_stores cs2 with (nolock)
	where cs2.home_store_id = cs.home_store_id
		and cs.away_store_id = cs.away_store_id
)
group by s.company_id, c.name
order by c.name;


select company_name, count(distinct away_store_id) cnt
from retaildb_test_server.dbo.qa_report_new_vw 
group by company_name
