use retaildb_timeseries_jcrew_v7
go

declare @total_pop int = 13
declare @total_households int = 16
declare @median_age int = 31

--declare @competition_strength int = 1
declare @competition_strength int = 2



-- temp table for stats per period
create table #stats (company_name varchar(50), store_id int, comp_instances float, total_pop float, total_households float, median_age float)

-- get store counts for prior period
insert into #stats
select 
	c.name as company,
	s.store_id,
	comp_instances.count as comp_instances,
	total_pop.value as total_pop,
	total_households.value as total_households,
	median_age.value as median_age
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
inner join demographic_numvalues total_pop on total_pop.trade_area_id = t.trade_area_id and total_pop.data_item_id = @total_pop
inner join demographic_numvalues total_households on total_households.trade_area_id = t.trade_area_id and total_households.data_item_id = @total_households
inner join demographic_numvalues median_age on median_age.trade_area_id = t.trade_area_id and median_age.data_item_id = @median_age
inner join companies c on c.company_id = s.company_id
cross apply
(
	select	
		sum(
			case when cc.competition_strength = 1 then 1
			else .5
			end
		) + 1 as count
	from competitive_stores cs
	inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id 
		and 
		(
			(@competition_strength = 1 and cc.competition_strength = 1)
			or
			(@competition_strength = 2 and cc.competition_strength > 0)
		)
	where cs.trade_area_id = t.trade_area_id
) comp_instances
order by c.name asc, s.store_id asc




-- sum up the main stats query with all the median queries
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
	select 
		company_name,
		AVG(total_pop / cast(s.comp_instances as float))  avg_total_pop,
		MIN(total_pop / cast(s.comp_instances as float)) as min_total_pop,
		MAX(total_pop / cast(s.comp_instances as float)) as max_total_pop,
		AVG(total_households / cast(s.comp_instances as float)) as avg_total_households,
		MIN(total_households / cast(s.comp_instances as float)) as min_total_households,
		MAX(total_households / cast(s.comp_instances as float)) as max_total_households,
		AVG(median_age / cast(s.comp_instances as float)) as avg_median_age,
		MIN(median_age / cast(s.comp_instances as float)) as min_median_age,
		MAX(median_age / cast(s.comp_instances as float)) as max_median_age
	from #stats s
	group by company_name
) main on main.company_name = c.name
left join
(
	select 
		company_name,
		AVG(total_pop) as median_total_pop
	from
	(
		select 
			st.company_name,
			cast(st.total_pop as float) / cast(st.comp_instances as float) as total_pop,
			ROW_NUMBER() over( partition by company_name order by cast(st.total_pop as float) / cast(st.comp_instances as float) asc) as row_num,
			count(*) over (partition by company_name) as count
		from #stats st
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) median_total_pop on median_total_pop.company_name = c.name
left join
(
	select 
		t.company_name,
		AVG(median_total_households) as median_total_households
	from
	(
		select 
			st.company_name,
			st.total_households / cast(st.comp_instances as float)  as median_total_households,
			ROW_NUMBER() over( partition by company_name order by st.total_households / cast(st.comp_instances as float) asc) as row_num,
			count(*) over (partition by company_name) as count
		from #stats st
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) median_total_households on median_total_households.company_name = c.name
left join
(
	select 
		company_name,
		AVG(median_age) as median_median_age
	from
	(
		select 
			st.company_name,
			st.median_age / cast(st.comp_instances as float) as median_age,
			ROW_NUMBER() over( partition by company_name order by st.median_age / cast(st.comp_instances as float) asc) as row_num,
			count(*) over (partition by company_name) as count
		from #stats st
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) median_median_age on median_median_age.company_name = c.name
where c.name like 'J.CREW%'
order by company

drop table #stats