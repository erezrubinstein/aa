use whitespace_4_mile__8_29_2013
go

declare @threshold_id int = 1
--select * from thresholds


select distinct
	dem.count as dems,
	CAST(s.company_id as varchar(10)) + ','+ CAST(s.store_id as varchar(10)),
	t.trade_area_id,
	a.latitude, a.longitude
from trade_areas t
inner join stores s on s.store_id = t.store_id
inner join addresses a on a.address_id = s.address_id
outer apply
(	
	select count(*) as count
	from demographic_numvalues d2
	where d2.template_name = 'QSR_OCT13' and d2.trade_area_id= t.trade_area_id
)  dem
where t.threshold_id = @threshold_id
	and dem.count = 0
order by dem.count asc