use HandBags_NOV13_CMA_20131127
go

declare @previous_time_period datetime = '19000101'
declare @time_period datetime = '20130731'
create table #trade_area_demographics (company_id int, company_name nvarchar(255), trade_area_threshold varchar(50),data_item_id int, demographic_description varchar(255), demographic_name varchar(255), value decimal(21, 5), value_competition_adjusted decimal(21, 5), comp_count_plus_one int)

-- cte for competition counts
;with trade_area_competition(trade_area_id, comp_count_plus_one) as
(	
	select 
		t.trade_area_id,
		-- cast as float for floating point math
		-- add one to make it include the home trade area (for normalization)
		cast(count(distinct cs.away_store_id) as float) + 1
	from trade_areas t
	-- left join to account for monopolies
	left join competitive_stores cs on cs.trade_area_id = t.trade_area_id
	group by t.trade_area_id
)

insert into #trade_area_demographics (company_id, company_name, trade_area_threshold, data_item_id, demographic_description, demographic_name, value, value_competition_adjusted, comp_count_plus_one)
select
	c.company_id,
	c.name as company_name,
	th.label as trade_area_threshold,
	di.data_item_id,
	di.description as demographic_description,
	di.name as demographic_name,
	d.value,
	d.value / comp.comp_count_plus_one as value_competition_adjusted,
	comp.comp_count_plus_one + 1 as comp_count_plus_one
from companies c
inner join stores s on s.company_id = c.company_id
inner join trade_areas t on t.store_id = s.store_id
inner join thresholds th on th.threshold_id = t.threshold_id
inner join demographic_numvalues d on d.trade_area_id = t.trade_area_id
inner join data_items di on di.data_item_id = d.data_item_id
inner join trade_area_competition comp on comp.trade_area_id = t.trade_area_id
where d.data_item_id > 10 
	-- for all stores
	and s.assumed_opened_date <= @time_period and (s.assumed_closed_date is null or s.assumed_closed_date > @time_period)
	-- for openings
	--and s.assumed_opened_date > @previous_time_period and s.assumed_opened_date <= @time_period
	-- for closings
	--s.assumed_closed_date > @previous_time_period and s.assumed_closed_date <= @time_period


select
	main.company_id,
	main.company_name,
	main.trade_area_threshold,
	main.data_item_id,
	main.demographic_description,
	main.demographic_name,
    isnull(main.avg, 0) as avg,
    isnull(median.median_value, 0) as med,
    isnull(main.min, 0) as min,
    isnull(main.max, 0) as max,
    isnull(main.stdev, 0) as stdev,
    isnull(main.avg_competition_adjusted, 0) as avg_competition_adjusted,
    isnull(median_competition_adjusted.median_value, 0) as med_competition_adjusted,
    isnull(main.min_competition_adjusted, 0) as min_competition_adjusted,
    isnull(main.max_competition_adjusted, 0) as max_competition_adjusted,
    isnull(main.stdev_competition_adjusted, 0) as stdev_competition_adjusted
from
(
	select
		dems.company_id,
		dems.company_name,
		dems.trade_area_threshold,
		dems.data_item_id,
		dems.demographic_description,
		dems.demographic_name,
		avg(dems.value) as avg,
		min(dems.value) as min,
		max(dems.value) as max,
		stdev(dems.value) as stdev,
		avg(dems.value_competition_adjusted) as avg_competition_adjusted,
		min(dems.value_competition_adjusted) as min_competition_adjusted,
		max(dems.value_competition_adjusted) as max_competition_adjusted,
		stdev(dems.value_competition_adjusted) as stdev_competition_adjusted
	from #trade_area_demographics dems
	group by dems.company_id, dems.company_name, dems.trade_area_threshold, dems.data_item_id, dems.demographic_description, dems.demographic_name
) main
inner join
(
	select 
		company_id,
		trade_area_threshold,
		data_item_id,
		AVG(value) as median_value
	from
	(
		select 
			company_id,
			trade_area_threshold,
			data_item_id,
			value,
			ROW_NUMBER() over( partition by company_id, trade_area_threshold, data_item_id order by value asc) as row_num,
			count(*) over (partition by company_id, trade_area_threshold, data_item_id) as count
		from #trade_area_demographics
	) t
	where row_num in (count / 2 + 1, (count + 1) / 2)
	group by company_id, trade_area_threshold, data_item_id
) median on median.company_id = main.company_id and median.trade_area_threshold = main.trade_area_threshold 
	and median.data_item_id = main.data_item_id
inner join
(
	select 
		company_id,
		trade_area_threshold,
		data_item_id,
		AVG(value) as median_value
	from
	(
		select 
			company_id,
			trade_area_threshold,
			data_item_id,
			value / comp_count_plus_one as value,
			ROW_NUMBER() over( partition by company_id, trade_area_threshold, data_item_id order by value / comp_count_plus_one asc) as row_num,
			count(*) over (partition by company_id, trade_area_threshold, data_item_id) as count
		from #trade_area_demographics
	) t
	where row_num in (count / 2 + 1, (count + 1) / 2)
	group by company_id, trade_area_threshold, data_item_id
) median_competition_adjusted on median_competition_adjusted.company_id = main.company_id and median_competition_adjusted.trade_area_threshold = main.trade_area_threshold 
	and median_competition_adjusted.data_item_id = main.data_item_id
	
drop table #trade_area_demographics