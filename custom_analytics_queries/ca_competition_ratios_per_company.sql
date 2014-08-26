use HandBags_NOV13_CMA_20131127
go


select 
	hc.company_id,
	hc.name as company_name, 
	ac.company_id as away_company_id,
	ac.name as away_company_name, 
	th.label as trade_area_threshold,
	count(*) as competitive_instances,
	count(distinct t.trade_area_id) as store_count,
	-- only need to cast one as float.  No need to do both.
	cast(count(*) as float) / count(distinct t.trade_area_id) as competition_ratio
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id
inner join thresholds th on th.threshold_id = t.threshold_id
inner join stores hs on hs.store_id = cs.home_store_id
inner join companies hc on hc.company_id = hs.company_id
inner join stores [as] on [as].store_id = cs.away_store_id
inner join companies ac on ac.company_id = [as].company_id
where cs.start_date <= '20120301' and (cs.end_date is null or cs.end_date > '20120301')
group by hc.company_id, hc.name, ac.company_id, ac.name, th.label

