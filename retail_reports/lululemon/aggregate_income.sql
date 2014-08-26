use retaildb_timeseries_lululemon_v20
go

declare @dem_pci int = 88
declare @dem_total_pop int = 13

-- get demographic data
declare @demographics table(company_id int, company_name varchar(100), trade_area_id int, total_income bigint, assumed_opened_date datetime, assumed_closed_date datetime)
insert into @demographics
select 
	c.company_id,
	c.name, 
	t.trade_area_id,
	cast(pci.value * total_pop.value as bigint),
	s.assumed_opened_date,
	s.assumed_closed_date
from companies c
inner join stores s on s.company_id = c.company_id
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
inner join demographic_numvalues pci on pci.trade_area_id = t.trade_area_id and pci.data_item_id = @dem_pci
inner join demographic_numvalues total_pop on total_pop.trade_area_id = t.trade_area_id and total_pop.data_item_id = @dem_total_pop


--declare competitors temp table
declare @comp_counts table(trade_area_id int, count int, period char(2), primary key(trade_area_id, period))

-- get store counts for perior period
insert into @comp_counts (trade_area_id, count, period)
select t.trade_area_id, 
	count(*),
	'PP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
where cs.start_date < '20120301' and hs.assumed_opened_date < '20120301'
group by t.trade_area_id

-- get store counts for openings
insert into @comp_counts (trade_area_id, count, period)
select t.trade_area_id, 
	count(*),
	'OP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
where cs.start_date > '20120301' and hs.assumed_opened_date > '20120301' 
group by t.trade_area_id

-- get store counts for closings
insert into @comp_counts (trade_area_id, count, period)
select t.trade_area_id, 
	count(*),
	'CL'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
where cs.end_date is not null and hs.assumed_closed_date is not null
group by t.trade_area_id

-- get store counts for current period
insert into @comp_counts (trade_area_id, count, period)
select t.trade_area_id, 
	count(*),
	'CP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
where cs.end_date is null and hs.assumed_closed_date is null
group by t.trade_area_id




-- query per each period
select c.name as company_name,
	isnull(pp.total_income, 0) as prior_period,
	isnull(OP.total_income, 0) as openings,
	isnull(CL.total_income, 0) as closings,
	isnull(CP.total_income, 0) as current_period
from companies c
outer apply
(	
	select d.company_name, AVG(d.total_income / (isnull(cc.count, 0) + 1)) as total_income
	from @demographics d
	left join @comp_counts cc on cc.trade_area_id = d.trade_area_id and cc.period = 'PP'
	where d.company_id = c.company_id 
		and d.assumed_opened_date < '20120301'
	group by d.company_name
) pp
outer apply
(	
	select d.company_name, AVG(d.total_income / (isnull(cc.count, 0) + 1)) as total_income
	from @demographics d
	left join @comp_counts cc on cc.trade_area_id = d.trade_area_id and cc.period = 'OP'
	where d.company_id = c.company_id 
		and d.assumed_opened_date > '20120301'
	group by d.company_name
) OP
outer apply
(	
	select d.company_name, AVG(d.total_income / (isnull(cc.count, 0) + 1)) as total_income
	from @demographics d
	left join @comp_counts cc on cc.trade_area_id = d.trade_area_id and cc.period = 'CL'
	where d.company_id = c.company_id 
		and d.assumed_closed_date is not null
	group by d.company_name
) CL
outer apply
(	
	select d.company_name, AVG(d.total_income / (isnull(cc.count, 0) + 1)) as total_income
	from @demographics d
	left join @comp_counts cc on cc.trade_area_id = d.trade_area_id and cc.period = 'CP'
	where d.company_id = c.company_id 
		and d.assumed_closed_date is null
	group by d.company_name
) CP
order by c.name
