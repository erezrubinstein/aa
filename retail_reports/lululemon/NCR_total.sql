use retaildb_timeseries_lululemon_v20
go

-- declare store counts temp table
declare @store_counts table(company_name varchar(50), count int, period char(2), primary key(company_name, period))

-- get store counts for perior period
insert into @store_counts (company_name, count, period)
select c.name, count(*), 'PP'
from stores s
inner join companies c on c.company_id = s.company_id
where s.assumed_opened_date < '20120301'
group by c.name

-- get store counts for openings
insert into @store_counts (company_name, count, period)
select c.name, count(*), 'OP'
from stores s
inner join companies c on c.company_id = s.company_id
where s.assumed_opened_date > '20120301'
group by c.name

-- get store counts for closings
insert into @store_counts (company_name, count, period)
select c.name, count(*), 'CL'
from stores s
inner join companies c on c.company_id = s.company_id
where s.assumed_closed_date is not NULL
group by c.name

-- get store counts for current period
insert into @store_counts (company_name, count, period)
select c.name, count(*), 'CP'
from stores s
inner join companies c on c.company_id = s.company_id
where s.assumed_closed_date is NULL
group by c.name




--declare competitors temp table
declare @comp_counts table(company_name varchar(50), count int, period char(2), primary key(company_name, period))

-- get store counts for perior period
insert into @comp_counts (company_name, count, period)
select hc.name as company_name, 
	count(*) as competitive_instances,
	'PP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
where cs.start_date < '20120301' and hs.assumed_opened_date < '20120301'
group by hc.name
order by hc.name

-- get store counts for openings
insert into @comp_counts (company_name, count, period)
select hc.name as company_name, 
	count(*) as competitive_instances,
	'OP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
where cs.start_date > '20120301' and hs.assumed_opened_date > '20120301' 
group by hc.name
order by hc.name

-- get store counts for closings
insert into @comp_counts (company_name, count, period)
select hc.name as company_name, 
	count(*) as competitive_instances,
	'CL'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
where cs.end_date is not null and hs.assumed_closed_date is not null
group by hc.name
order by hc.name

-- get store counts for current period
insert into @comp_counts (company_name, count, period)
select hc.name as company_name, 
	count(*) as competitive_instances,
	'CP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
where cs.end_date is null and hs.assumed_closed_date is null
group by hc.name
order by hc.name



-- declare periods
declare  @periods table (id int primary key identity, name varchar(100), period varchar(100))
insert into @periods (name, period)
select 'prior_period', 'PP'
union all
select 'openings', 'OP' 
union all
select 'closings', 'CL' 
union all
select 'current_period', 'CP'


-- get NCR pivot per period
select *
from
(
	select c.name, 
		p.name as period, 
		case 
			when sc.count is NULL then NULL
			else 
				cast(isnull(cc.count, 0) as float) / cast(isnull(sc.count, 0) as float)
		end as NCR
	from companies c
	cross join @periods p
	left join @comp_counts cc on cc.company_name = c.name and cc.period = p.period
	left join @store_counts sc on sc.company_name = c.name and sc.period = p.period
) t
pivot
(
	SUM(NCR)
	for period in ([prior_period], [openings], [closings], [current_period])
) c
order by name