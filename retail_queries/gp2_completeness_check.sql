--stores that are neither in competitve_stores nor monopolies
--means we haven't run that store through gp2 yet
select s1.id, s1.company_id
from stores s1
where not exists (
		select 1 from competitive_stores cs where cs.home_store_id = s1.id
	)
	and not exists (
		select 1 from monopolies m where m.store_id = s1.id
	)