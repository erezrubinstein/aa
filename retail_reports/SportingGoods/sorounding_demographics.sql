use retaildb_timeseries_sporting_goods_v5
go



declare @total_pop int = 13
declare @total_households int = 16
declare @median_age int = 31


-- temp table for stats per period
create table #stats (company_name varchar(50), store_id int, total_pop float, total_households float, median_age float)

-- get store counts for prior period
insert into #stats
select 
	c.name as company,
	s.store_id,
	total_pop.value as total_pop,
	total_households.value as total_households,
	median_age.value as median_age
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
inner join demographic_numvalues total_pop on total_pop.trade_area_id = t.trade_area_id and total_pop.data_item_id = @total_pop
inner join demographic_numvalues total_households on total_households.trade_area_id = t.trade_area_id and total_households.data_item_id = @total_households
inner join demographic_numvalues median_age on median_age.trade_area_id = t.trade_area_id and median_age.data_item_id = @median_age
inner join companies c on c.company_id = s.company_id
order by c.name asc, s.store_id asc


-- run statistics
select 
	c.name as company,
	main.avg_total_pop,
	main.min_total_pop,
	main.max_total_pop,
	median_total_pop.median_total_pop,
	main.avg_total_households,
	main.min_total_households,
	main.max_total_households,
	median_total_households.median_total_households,
	main.avg_median_age,
	main.min_median_age,
	main.max_median_age,
	median_median_age.median_median_age
from companies c
left join
(
	-- main stats
	select 
		company_name,
		AVG(total_pop) as avg_total_pop,
		MIN(total_pop) as min_total_pop,
		MAX(total_pop) as max_total_pop,
		AVG(total_households) as avg_total_households,
		MIN(total_households) as min_total_households,
		MAX(total_households) as max_total_households,
		AVG(median_age) as avg_median_age,
		MIN(median_age) as min_median_age,
		MAX(median_age) as max_median_age
	from #stats s
	group by company_name
) main on main.company_name = c.name
left join
(
	select 
		company,
		AVG(total_pop) as median_total_pop
	from
	(
		select 
			s.company_name as company,
			s.total_pop,
			ROW_NUMBER() over( partition by s.company_name order by s.total_pop asc) as row_num,
			count(*) over (partition by s.company_name) as count
		from #stats s
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company
) median_total_pop on median_total_pop.company = main.company_name
left join
(
	select 
		company,
		AVG(median_total_households) as median_total_households
	from
	(
		select 
			s.company_name as company,
			s.total_households as median_total_households,
			ROW_NUMBER() over( partition by s.company_name order by s.total_households asc) as row_num,
			count(*) over (partition by s.company_name) as count
		from #stats s
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company
) median_total_households on median_total_households.company = main.company_name
left join
(
	select 
		company,
		AVG(median_age) as median_median_age
	from
	(
		select 
			s.company_name as company,
			s.median_age as median_age,
			ROW_NUMBER() over( partition by s.company_name order by s.median_age asc) as row_num,
			count(*) over (partition by s.company_name) as count
		from #stats s
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company
) median_median_age on median_median_age.company = main.company_name
order by company

drop table #stats