use HandBags_NOV13_CMA_20131127
go

declare @time_period datetime = '2013-07-31'

-- CTE for home store count
; WITH store_counts (company_id, store_count) as
(
	select s.company_id, count(*) as store_count
	from stores s
	where s.assumed_opened_date <= @time_period and (s.assumed_closed_date is null or s.assumed_closed_date > @time_period)
	group by s.company_id
),
-- CTE for all thresholds within this db
trade_area_thresholds (trade_area_threshold) as 
(
	select distinct th.label as trade_area_threshold
	from trade_areas t
	inner join thresholds th on th.threshold_id = t.threshold_id
),
-- CTE for raw competition counts and statistics
competition (home_company_id, trade_area_threshold, competitive_instances, distinct_home_stores_affected) as 
(
	select 
		hc.company_id as home_company_id,
		th.label as trade_area_threshold,
		count(distinct cs.competitive_store_id) as competitive_instances,
		count(distinct hs.store_id) as distinct_home_stores_affected
	from companies hc
	inner join stores hs on hs.company_id = hc.company_id
	inner join trade_areas t on t.store_id = hs.store_id
	inner join thresholds th on th.threshold_id = t.threshold_id
	inner join competitive_stores cs on cs.trade_area_id = t.trade_area_id and 
		cs.start_date <= @time_period and (cs.end_date is null or cs.end_date > @time_period)
	where hs.assumed_opened_date <= @time_period and (hs.assumed_closed_date is null or hs.assumed_closed_date > @time_period)
	group by hc.company_id, th.label
)

-- main query to cross join all companies/thresholds and left join on competition
select 
	hc.company_id as home_company_id,
	hc.name as home_company_name,
	th.trade_area_threshold,
	isnull(cast(c.competitive_instances as float) / scounts.store_count, 0) as competition_ratio,
	isnull((cast(c.distinct_home_stores_affected as float) / scounts.store_count) * 100, 0) as percent_store_base_affected
from companies hc
cross join trade_area_thresholds th
inner join store_counts scounts on scounts.company_id = hc.company_id
left join competition c on c.home_company_id = hc.company_id and th.trade_area_threshold = c.trade_area_threshold
order by hc.name, th.trade_area_threshold

