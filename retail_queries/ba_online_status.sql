use SCSS_SEP13_CMA_091513
go

declare @threshold_id int = 1
--select * from thresholds


select distinct
	acs_pop.count as acs_pop, 
	acs_housing.count as acs_housing,
	--ba_server_template.count as ba_server_template,
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
	where d2.template_name = 'acs_population' and d2.trade_area_id= t.trade_area_id
)  acs_pop
outer apply
(	
	select count(*) as count
	from demographic_numvalues d2
	where d2.template_name = 'acs_housing' and d2.trade_area_id= t.trade_area_id
)  acs_housing
--outer apply
--(	
--	select count(*) as count
--	from demographic_numvalues d2
--	where d2.template_name = 'QSR_OCT13' and d2.trade_area_id= t.trade_area_id
--)  ba_server_template
where t.threshold_id = @threshold_id
order by acs_pop.count asc