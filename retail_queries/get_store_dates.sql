use retaildb_timeseries_dollar_stores_v1
go

select c.name, s.company_id, s.assumed_opened_date
from stores s
inner join companies c on c.company_id = s.company_id
group by c.name, s.company_id, s.assumed_opened_date
order by assumed_opened_date