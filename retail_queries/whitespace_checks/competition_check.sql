use TTS_AUG13_20MSQWHSPC_080413
go


SELECT c.company_id, c.name, s.store_id, comp.count, a.longitude, a.latitude
from stores s
inner join addresses a on a.address_id = s.address_id
inner join companies c on c.company_id = s.company_id
cross apply
(
	select count(*) as count
	from competitive_stores 
	where away_store_id = s.store_id
) comp
where c.company_id <> 1 and comp.count <> 1