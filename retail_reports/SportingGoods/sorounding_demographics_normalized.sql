use retaildb_timeseries_sporting_goods_v5
go

declare @total_pop int = 13
declare @total_households int = 16
declare @median_age int = 31



-- temp table for stats per period
create table #stats (company_name varchar(50), store_id int, comp_instances float, total_pop float, norm_total_pop float)

-- get store counts for prior period
insert into #stats
select 
	c.name as company,
	s.store_id,
	isnull(comp_instances.count, 1) as comp_instances,
	total_pop.value as total_pop,
	CAST(total_pop.value as float) / CAST(isnull(comp_instances.count, 1) as float) as norm_total_pop
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
inner join demographic_numvalues total_pop on total_pop.trade_area_id = t.trade_area_id and total_pop.data_item_id = @total_pop
inner join companies c on c.company_id = s.company_id
cross apply
(
	select	
		sum(
			isnull(weights.weight, 0)
		) + 1 as count
	from trade_areas t2 
	left join competitive_stores cs on cs.trade_area_id = t2.trade_area_id
	left join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id 
	left join companies c_home on c_home.company_id = cc.home_company_id
	left join companies c_away on c_away.company_id = cc.away_company_id
	left join jeremy_weights.dbo.weights weights on weights.home_company_name = c_home.name and weights.away_company_name = c_away.name
	where t2.trade_area_id = t.trade_area_id
		and cs.end_date is null
) comp_instances
where s.assumed_closed_date is null
order by c.name asc, s.store_id asc




-- sum up the main stats query with all the median queries
select 
	c.name as company,
	main.avg_total_pop,
	main.min_total_pop,
	main.max_total_pop,
	median_total_pop.median_total_pop
from companies c
left join
(
	select 
		company_name,
		AVG(CAST(norm_total_pop as float))  avg_total_pop,
		MIN(CAST(norm_total_pop as float)) as min_total_pop,
		MAX(CAST(norm_total_pop as float)) as max_total_pop
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
			CAST(norm_total_pop as float) as total_pop,
			ROW_NUMBER() over( partition by company_name order by CAST(norm_total_pop as float) asc) as row_num,
			count(*) over (partition by company_name) as count
		from #stats st
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) median_total_pop on median_total_pop.company_name = c.name
order by company

drop table #stats