use retaildb_timeseries_lululemon_v20
go

--declare @period char(2) = 'PP'
--declare @period char(2) = 'OP'
--declare @period char(2) = 'CL'
declare @period char(2) = 'CP'


--declare competitors temp table
declare @comp_counts table(company_name varchar(50), count int, period char(2))

-- get store counts for perior period
insert into @comp_counts (company_name, count, period)
select c.name, comp.count, 'PP'
from stores s
inner join companies c on c.company_id = s.company_id
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
cross apply
(
	select count(*) as count
	from competitive_stores 
	where trade_area_id = t.trade_area_id
		and start_date < '20120301' and s.assumed_opened_date < '20120301'
) comp
where s.assumed_opened_date < '20120301'

-- get store counts for openings
insert into @comp_counts (company_name, count, period)
select c.name, comp.count, 'OP'
from stores s
inner join companies c on c.company_id = s.company_id
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
cross apply
(
	select count(*) as count
	from competitive_stores 
	where trade_area_id = t.trade_area_id
		and start_date > '20120301' 
) comp
where s.assumed_opened_date > '20120301' 

-- get store counts for closings
insert into @comp_counts (company_name, count, period)
select c.name, comp.count, 'CL'
from stores s
inner join companies c on c.company_id = s.company_id
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
cross apply
(
	select count(*) as count
	from competitive_stores 
	where trade_area_id = t.trade_area_id
		and end_date is not null 
) comp
where s.assumed_closed_date is not null

-- get store counts for current period
insert into @comp_counts (company_name, count, period)
select c.name, comp.count, 'CP'
from stores s
inner join companies c on c.company_id = s.company_id
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
cross apply
(
	select count(*) as count
	from competitive_stores 
	where trade_area_id = t.trade_area_id
		and end_date is null
) comp
where s.assumed_closed_date is null



-- get built in aggregate stats
select 
	c.name as company,
	main.avg,
	main.min,
	main.max,
	main.stdev,
	median_competition.median_competition
from companies c
left join 
(
	select 
		company_name,
		avg(cast(count as float)) avg,
		MIN(cast(count as float)) min,
		MAX(cast(count as float)) max,
		STDEV(cast(count as float)) stdev
	from @comp_counts 
	where period = @period
	group by company_name
) main on main.company_name = c.name
left join
(
	select 
		company,
		AVG(cast(comp_count as float)) as median_competition
	from
	(
		select 
			c.name as company,
			cast(cc.count as float) as comp_count,
			ROW_NUMBER() over( partition by c.name order by cc.count asc) as row_num,
			count(*) over (partition by c.name) as count
		from companies c
		left join @comp_counts cc on cc.company_name = c.name and cc.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company
) median_competition on median_competition.company = c.name
order by c.name