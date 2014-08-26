use retaildb_timeseries_sporting_goods_v5
go


--declare competitors temp table
declare @comp_counts table(company_name varchar(50), count float)

-- get comp_counts per every store
insert into @comp_counts (company_name, count)
select c.name, isnull(comp.count, 0)
from stores s
inner join companies c on c.company_id = s.company_id
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
cross apply
(
	select 
		sum(
			weights.weight
		) as count
	from competitive_stores cs
	inner join competitive_companies cc on cc.competitive_company_id = cs.competitive_company_id
	inner join companies c_home on c_home.company_id = cc.home_company_id
	inner join companies c_away on c_away.company_id = cc.away_company_id
	inner join jeremy_weights.dbo.weights weights on weights.home_company_name = c_home.name and weights.away_company_name = c_away.name
	where cs.trade_area_id = t.trade_area_id
	and cs.end_date is null
) comp
where s.assumed_closed_date is null




-- get built in aggregate stats
select 
	c.name as company,
	main.avg,
	main.min,
	main.max,
	main.stdev,
	median_competition.median_competition
from companies c
left join 
(
	select 
		company_name,
		avg(cast(count as float)) avg,
		MIN(cast(count as float)) min,
		MAX(cast(count as float)) max,
		STDEV(cast(count as float)) stdev
	from @comp_counts 
	group by company_name
) main on main.company_name = c.name
left join
(
	select 
		company,
		AVG(cast(comp_count as float)) as median_competition
	from
	(
		select 
			c.name as company,
			cast(cc.count as float) as comp_count,
			ROW_NUMBER() over( partition by c.name order by cc.count asc) as row_num,
			count(*) over (partition by c.name) as count
		from companies c
		left join @comp_counts cc on cc.company_name = c.name
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company
) median_competition on median_competition.company = c.name
order by c.name

