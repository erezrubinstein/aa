use retaildb_timeseries_wfm_organic
go


select c.name, 
	isnull(t.[Bristol Farms], 0) [Bristol Farms],
	isnull(t.[NEW SEASONS MARKET], 0) [NEW SEASONS MARKET],
	isnull(t.[NATURAL GROCERS], 0) [NATURAL GROCERS],
	isnull(t.[Earth Origins - All Banners], 0) [Earth Origins - All Banners],
	isnull(t.[Other High-End Natural/Organic/Gourmet Grocers], 0) [Other High-End Natural/Organic/Gourmet Grocers],
	isnull(t.[Mainstream Grocery], 0) [Mainstream Grocery],
	isnull(t.[fresh & easy], 0) [fresh & easy],
	isnull(t.[Warehouse], 0) [Warehouse],
	isnull(t.[WHOLE FOODS MARKET], 0) [WHOLE FOODS MARKET],
	isnull(t.[Earth Fare], 0) [Earth Fare],
	isnull(t.[Wegmans], 0) [Wegmans],
	isnull(t.[BALDUCCI'S], 0) [BALDUCCI'S],
	isnull(t.[metropolitanmarket], 0) [metropolitanmarket],
	isnull(t.[TRADER JOE'S], 0) [TRADER JOE'S],
	isnull(t.[CHAMBERLIN'S MARKET & CAFÉ], 0) [CHAMBERLIN'S MARKET & CAFÉ],
	isnull(t.[SPROUTS - All Banners], 0) [SPROUTS - All Banners],
	isnull(t.[PAVILIONS], 0) [PAVILIONS],
	isnull(t.[AKiN'S NATURAL FOODS MARKET], 0) [AKiN'S NATURAL FOODS MARKET],
	isnull(t.[WHOLE FOODS MARKET STORES IN DEVELOPMENT], 0) [WHOLE FOODS MARKET STORES IN DEVELOPMENT],
	isnull(t.[FAIRWAY], 0) [FAIRWAY],
	isnull(t.[THE FRESH MARKET], 0) [THE FRESH MARKET]
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
		inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
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
		for away_company in ([Bristol Farms], [NEW SEASONS MARKET], [NATURAL GROCERS], [Earth Origins - All Banners], [Other High-End Natural/Organic/Gourmet Grocers], [Mainstream Grocery], [fresh & easy], [Warehouse], [WHOLE FOODS MARKET], [Earth Fare], [Wegmans], [BALDUCCI'S], [metropolitanmarket], [TRADER JOE'S], [CHAMBERLIN'S MARKET & CAFÉ], [SPROUTS - All Banners], [PAVILIONS], [AKiN'S NATURAL FOODS MARKET], [WHOLE FOODS MARKET STORES IN DEVELOPMENT], [FAIRWAY], [THE FRESH MARKET])
	) p
) t on t.home_company = c.name
order by c.name
