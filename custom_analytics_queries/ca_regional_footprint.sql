use HandBags_NOV13_CMA_20131127
go

declare @time_period datetime = '2013-07-31'

select 
	c.company_id,
	c.name as company_name,
	store_id, 
	a.street_number, 
	a.street, 
	a.municipality as city,
	a.governing_district as state,
	a.postal_area as zip_code,
	g.region as region,
	g.division as division
from stores s
inner join companies c on c.company_id = s.company_id
inner join addresses a on a.address_id = s.address_id
inner join governing_districts g on g.governing_district = a.governing_district
where s.assumed_opened_date <= @time_period and (s.assumed_closed_date is null or s.assumed_closed_date > @time_period)