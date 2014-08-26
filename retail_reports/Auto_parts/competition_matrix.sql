use retaildb_timeseries_auto_parts_v5
go


select c.name, 
	isnull(t.[O'Reilly AUTO PARTS], 0) [O'Reilly AUTO PARTS],
	isnull(t.[Auto Parts Independent], 0) [Auto Parts Independent],
	isnull(t.[NAPA Auto Parts], 0) [NAPA Auto Parts],
	isnull(t.[PEPBOYS AUTO], 0) [PEPBOYS AUTO],
	isnull(t.[Tires], 0) [Tires],
	isnull(t.[AUTOPART INTERNATIONAL], 0) [AUTOPART INTERNATIONAL],
	isnull(t.[AutoZone], 0) [AutoZone],
	isnull(t.[Fast Lube & Oil Change Stores], 0) [Fast Lube & Oil Change Stores],
	isnull(t.[Advance Auto Parts], 0) [Advance Auto Parts],
	isnull(t.[CARQUEST AUTO PARTS], 0) [CARQUEST AUTO PARTS],
	isnull(t.[New Auto Dealers], 0) [New Auto Dealers],
	isnull(t.[Auto Plus], 0) [Auto Plus]
from companies c
left join
(
	select *
	from
	(
		select 
			hc.name as home_company,
			ac.name as away_company
		from competitive_stores cs
		inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 5
		inner join stores hs on hs.store_id = cs.home_store_id
		inner join companies hc on hc.company_id = hs.company_id
		inner join stores [as] on [as].store_id = cs.away_store_id
		inner join companies ac on ac.company_id = [as].company_id
		--where cs.start_date <= '20120301' and hs.assumed_opened_date < '20120301' -- previous period
		--where hs.assumed_opened_date > '20120301' and cs.start_date > '20120301' -- openings
		--where hs.assumed_closed_date is not null and cs.end_date is not null -- closings
		where cs.end_date is null and hs.assumed_closed_date is null -- current 
	) t
	pivot
	(
		count(t.away_company)
		for away_company in ([O'Reilly AUTO PARTS], [Auto Parts Independent], [NAPA Auto Parts], [PEPBOYS AUTO], [Tires], [AUTOPART INTERNATIONAL], [AutoZone], [Fast Lube & Oil Change Stores], [Advance Auto Parts], [CARQUEST AUTO PARTS], [New Auto Dealers], [Auto Plus])
	) p
) t on t.home_company = c.name
order by c.name