use LL_OCT3_CMA_100213
go

--calculate all openings per period
select 
	c.name as company_name,
	isnull(prior_period.count, 0) as prior_period,
	isnull(openings.count, 0) as openings,
	isnull(closings.count, 0) as closings,
	isnull(current_period.count, 0) as current_period
-- left from companies so that we get companies with no changes in one period
from companies c

-- calculate prior period
left join 
(
	select c.name as company_name, count(*) as count
	from stores s
	inner join companies c on c.company_id = s.company_id
	where s.assumed_opened_date < '20120301' 
	group by c.name, c.company_id
) prior_period on prior_period.company_name = c.name

-- calculate openings
left join 
(
	select c.name as company_name, count(*) as count
	from stores s
	inner join companies c on c.company_id = s.company_id
	where s.assumed_opened_date > '20120301'
	group by c.name, c.company_id
) openings on openings.company_name = c.name

-- calculate closings
left join 
(
	select c.name as company_name, count(*) as count
	from stores s
	inner join companies c on c.company_id = s.company_id
	where s.assumed_closed_date is not null
	group by c.name, c.company_id
) closings on closings.company_name = c.name

-- calculate current period
left join 
(
	select c.name as company_name, count(*) as count
	from stores s
	inner join companies c on c.company_id = s.company_id
	where s.assumed_closed_date is null
	group by c.name, c.company_id
) current_period on current_period.company_name = c.name
order by c.name
