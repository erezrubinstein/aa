use HandBags_NOV13_CMA_20131127
go

-- select distinct assumed_opened_date from stores

declare @cohort_date datetime = '20130731'
declare @previous_cohort_date datetime = '19000101'

--calculate all openings per period
select 
	c.company_id,
	c.name as company_name,
	count(distinct s.store_id) as store_count,
	count(distinct so.store_id) as openings_count, 
	count(distinct sc.store_id) as closings_count
from companies c
-- active stores in cohort
left join stores s on s.company_id = c.company_id and s.assumed_opened_date <= @cohort_date and (s.assumed_closed_date is null or s.assumed_closed_date > @cohort_date)
-- openings
left join stores so on so.company_id = c.company_id and so.assumed_opened_date > @previous_cohort_date and so.assumed_opened_date <= @cohort_date
-- closing
left join stores sc on sc.company_id = c.company_id and sc.assumed_closed_date > @previous_cohort_date and sc.assumed_closed_date <= @cohort_date
group by c.name, c.company_id
