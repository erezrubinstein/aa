use retaildb_timeseries_lululemon_v20
go


--declare @period char(2) = 'PP'
--declare @period char(2) = 'OP'
--declare @period char(2) = 'CL'
declare @period char(2) = 'CP'


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
declare @comp_counts table(home_company varchar(50), away_company varchar(50), count int, period char(2), primary key(home_company, away_company, period))

-- get store counts for perior period
insert into @comp_counts (home_company, away_company, count, period)
select hc.name, 
	ac.name,
	count(*),
	'PP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
inner join stores [as] on [as].store_id = cs.away_store_id
inner join companies ac on ac.company_id = [as].company_id
where cs.start_date < '20120301' and hs.assumed_opened_date < '20120301'
group by hc.name, ac.name

-- get store counts for openings
insert into @comp_counts (home_company, away_company, count, period)
select hc.name, 
	ac.name,
	count(*),
	'OP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
inner join stores [as] on [as].store_id = cs.away_store_id
inner join companies ac on ac.company_id = [as].company_id
where cs.start_date > '20120301' and hs.assumed_opened_date > '20120301'
group by hc.name, ac.name

-- get store counts for closings
insert into @comp_counts (home_company, away_company, count, period)
select hc.name, 
	ac.name,
	count(*),
	'CL'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
inner join stores [as] on [as].store_id = cs.away_store_id
inner join companies ac on ac.company_id = [as].company_id
where cs.end_date is not null and hs.assumed_closed_date is not null
group by hc.name, ac.name

-- get store counts for current period
insert into @comp_counts (home_company, away_company, count, period)
select hc.name, 
	ac.name,
	count(*),
	'CP'
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
inner join stores [as] on [as].store_id = cs.away_store_id
inner join companies ac on ac.company_id = [as].company_id
where cs.end_date is null and hs.assumed_closed_date is null
group by hc.name, ac.name



---- get NCR per store (per period)
select *
from
(
	select c.name as home_company,
		c2.name as away_company,
		case 
			when sc.count is NULL then NULL
			else 
				cast(isnull(cc.count, 0) as float) / cast(isnull(sc.count, 0) as float)
		end as NCR
	from companies c
	inner join companies c2 on c2.name <> c.name
	left join @comp_counts cc on cc.home_company = c.name and cc.away_company = c2.name and cc.period = @period
	left join @store_counts sc on sc.company_name = c.name and sc.period = @period
) t
pivot
(
	sum(NCR)
	for away_company in ([ATHLETA], [Calvin Klein PERFORMANCE], [FOREVER 21], [Free People], [GAP Full Line], [GAP Outlet], [LORNA JANE], [lucy], [lucy Authorized Dealers], [lululemon athletica Authorized Dealers], [lululemon athletica Showrooms], [lululemon athletica Stores], [Nike], [NORDSTROM], [UNDER ARMOUR], [Victoria's Secret VSX Sport])
) p
