use retaildb_timeseries_office_supplies_v3
go

select d.trade_area_id, 
	count(*) as count, 
	traffic_count.count, 
	CAST(s.company_id as varchar(10)) + ','+ CAST(s.store_id as varchar(10))
from demographic_numvalues d
inner join trade_areas t on t.trade_area_id = d.trade_area_id
inner join stores s on s.store_id = t.store_id
outer apply
(	
	select count(*) as count
	from demographic_numvalues d2
	where d2.template_name = 'acs_population' and d2.trade_area_id= d.trade_area_id
)  traffic_count
group by d.trade_area_id, 
	traffic_count.count, 
	s.store_id, s.company_id
having traffic_count.count < 20
order by traffic_count.count, count(*) asc