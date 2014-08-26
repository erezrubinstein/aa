use THI_OCT13_CMA_101013
go

select 
	AVG(cast(MEDHINC_CY as float)) as median
from
(
	select 
		ROW_NUMBER() over(order by d.MEDHINC_CY asc) as row_num,
		count(*) over (partition by s.company_id) as count,
		d.MEDHINC_CY
	from demographics_denorm d
	inner join stores s on s.store_id = d.store_id
	inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 12
	where s.company_id = 92
		--and s.assumed_opened_date = '19000101' -- prior period
		--and s.assumed_opened_date > '20120301' -- openings
		--and s.assumed_closed_date is not null -- closings
		and s.assumed_closed_date is null -- current period
) t
where row_num in (count/2+1, (count+1)/2)