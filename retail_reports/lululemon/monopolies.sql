use retaildb_timeseries_lululemon_v20
go


select *
from
(
	select c.name as company_name,
		-- as per Jeremy - if store has transition, and it's a single and complete in the same period, count it as single (1, not 2)
		min(mt.name) as monopoly_type
		--minmt.name as monopoly_type
	from companies c
	inner join stores s on s.company_id = c.company_id
	inner join trade_areas t on t.store_id = s.store_id
	left join monopolies m on m.trade_area_id = t.trade_area_id
	left join monopoly_types mt on mt.monopoly_type_id = m.monopoly_type_id
		--and m.start_date < '20120301' and s.assumed_opened_date < '20120301' -- prior period
		--and m.start_date > '20120301' and s.assumed_opened_date > '20120301' -- openings
		--and m.end_date is not null and s.assumed_closed_date is not null -- closings
		and m.end_date is null and s.assumed_closed_date is null-- current period
	where t.threshold_id = 1
	-- very importnat GROUP BY.  This makes sure to count double monopolies (if they change) as one monopoly not two
	GROUP BY s.store_id, c.name
) t
pivot
(
	count(monopoly_type)
	for monopoly_type in ([Complete], [Single Player])
) p