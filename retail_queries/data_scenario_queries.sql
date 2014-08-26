use retaildb_timeseries_data_scenario_5
go

select * from companies
select * from competitive_companies order by home_company_id, away_company_id


select s.store_id, s.company_id, c.name as company, s.phone_number, s.complex, s.note, 
	a.street_number, a.street, a.municipality, a.postal_area,
	s.assumed_opened_date, s.assumed_closed_date
from stores s
inner join companies c on c.company_id = s.company_id
inner join addresses a on a.address_id = s.address_id
order by company_id, store_id, assumed_opened_date, assumed_closed_date

declare @store_id int = NULL
declare @threshold int = 1
select cs.home_store_id, cs.away_store_id, cs.start_date, cs.end_date, cs.travel_time
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = @threshold
where @store_id is null or cs.home_store_id = @store_id or cs.away_store_id = @store_id
order by home_store_id, away_store_id




select s.store_id, s.company_id, c.name as company, s.phone_number, s.complex, s.note, 
	a.street_number, a.street, a.municipality, a.postal_area,
	s.assumed_opened_date, s.assumed_closed_date
from stores s
inner join companies c on c.company_id = s.company_id
inner join addresses a on a.address_id = s.address_id
order by company_id, store_id, assumed_opened_date, assumed_closed_date

select m.store_id, m.monopoly_type_id, m.start_date, m.end_date, t.threshold_id
from monopolies m
inner join trade_areas t on t.trade_area_id = m.trade_area_id and t.threshold_id = 4
order by m.store_id, start_date, end_date
