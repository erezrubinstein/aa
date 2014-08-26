use retaildb_timeseries_lululemon_v20
go

-- get all the comptition counts in one query
declare @comp_counts table(company_id int, company_name varchar(100), start_date datetime, end_date datetime, assumed_opened_date datetime, assumed_closed_date datetime)
	
insert into @comp_counts (company_id, company_name, start_date, end_date, assumed_opened_date, assumed_closed_date)
select 
	c.company_id,
	c.name as company_name,
	cs.start_date,
	cs.end_date,
	s.assumed_opened_date,
	s.assumed_closed_date
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id and t.threshold_id = 1
inner join stores s on s.store_id = cs.home_store_id
inner join companies c on c.company_id = s.company_id


-- query per each period
select c.name as company_name,
	isnull(pp.count, 0) as prior_period,
	isnull(OP.count, 0) as openings,
	isnull(CL.count, 0) as closings,
	isnull(CP.count, 0) as current_period
from companies c
outer apply
(	
	select company_name, count(*) as count
	from @comp_counts
	where company_id = c.company_id 
		and start_date < '20120301' and assumed_opened_date < '20120301'
	group by company_name
) pp
outer apply
(	
	select company_name, count(*) as count
	from @comp_counts
	where company_id = c.company_id 
		and assumed_opened_date > '20120301' and start_date > '20120301'
	group by company_name
) OP
outer apply
(	
	select company_name, count(*) as count
	from @comp_counts
	where company_id = c.company_id 
		and assumed_closed_date is not null and end_date is not null
	group by company_name
) CL
outer apply
(	
	select company_name, count(*) as count
	from @comp_counts
	where company_id = c.company_id 
		and end_date is null and assumed_closed_date is null
	group by company_name
) CP
order by c.name
