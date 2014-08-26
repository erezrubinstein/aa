
select count(distinct s1.id)
from stores s1
inner join competitive_stores cs on cs.home_store_id = s1.id
inner join stores s2 on s2.id = cs.away_store_id and s2.company_id = s1.company_id
--23795

select count(distinct s1.id)
from stores s1
where not exists (
	select 1 from competitive_stores cs 
	inner join stores s2 on s2.id = cs.away_store_id
	where cs.home_store_id = s1.id
		and s2.company_id = s1.company_id
)
--8712