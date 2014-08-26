use retaildb_timeseries_wfm_organic
go

declare @period char(2) = 'PP'
--declare @period char(2) = 'OP'
--declare @period char(2) = 'CL'
--declare @period char(2) = 'CP'

-- threshold baby!
declare @threshold_id int = 1


-- temp table for competitive #s
declare @comps table(store_id int, comp_instances int, period char(2))

-- get store counts for prior period
insert into @comps(store_id, comp_instances, period)
select 
	s.store_id,
	comp_instances.count as comp_instances,
	'PP'
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
cross apply
(
	select SUM(w.strength) + 1 as count
	from competitive_stores cs
	inner join stores hs on hs.store_id = cs.home_store_id
	inner join stores [as] on [as].store_id = cs.away_store_id
	inner join weighed_competitive_weights w on w.home_company_id = hs.company_id and w.away_company_id = [as].company_id
	where trade_area_id = t.trade_area_id
		and start_date < '20120301'
) comp_instances
where s.assumed_opened_date < '20120301'


-- get store counts for openings
insert into @comps(store_id, comp_instances, period)
select 
	s.store_id,
	comp_instances.count as comp_instances,
	'OP'
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
cross apply
(
	select SUM(w.strength) + 1 as count
	from competitive_stores cs
	inner join stores hs on hs.store_id = cs.home_store_id
	inner join stores [as] on [as].store_id = cs.away_store_id
	inner join weighed_competitive_weights w on w.home_company_id = hs.company_id and w.away_company_id = [as].company_id
	where trade_area_id = t.trade_area_id
		and start_date > '20120301'
) comp_instances
where s.assumed_opened_date > '20120301'


-- get store counts for closings
insert into @comps(store_id, comp_instances, period)
select 
	s.store_id,
	comp_instances.count as comp_instances,
	'CL'
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
cross apply
(
	select SUM(w.strength) + 1 as count
	from competitive_stores cs
	inner join stores hs on hs.store_id = cs.home_store_id
	inner join stores [as] on [as].store_id = cs.away_store_id
	inner join weighed_competitive_weights w on w.home_company_id = hs.company_id and w.away_company_id = [as].company_id
	where trade_area_id = t.trade_area_id
		and end_date is not null
) comp_instances
where s.assumed_closed_date is not null



-- get store counts for current period
insert into @comps(store_id, comp_instances, period)
select 
	s.store_id,
	comp_instances.count as comp_instances,
	'CP'
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
cross apply
(
	select SUM(w.strength) + 1 as count
	from competitive_stores cs
	inner join stores hs on hs.store_id = cs.home_store_id
	inner join stores [as] on [as].store_id = cs.away_store_id
	inner join weighed_competitive_weights w on w.home_company_id = hs.company_id and w.away_company_id = [as].company_id
	where trade_area_id = t.trade_area_id
		and end_date is null
) comp_instances
where s.assumed_closed_date is null










-- get stats

select 
	c.name,
	med_TOTPOP_CY.med_TOTPOP_CY,
	med_TOTHH_CY.med_TOTHH_CY,
	med_MEDAGE_CY.med_MEDAGE_CY,
	med_HINC0_CY.med_HINC0_CY,
	med_HINC15_CY.med_HINC15_CY,
	med_HINC25_CY.med_HINC25_CY,
	med_HINC35_CY.med_HINC35_CY,
	med_HINC50_CY.med_HINC50_CY,
	med_HINC75_CY.med_HINC75_CY,
	med_HINC100_CY.med_HINC100_CY,
	med_HINC150_CY.med_HINC150_CY,
	med_HINC200_CY.med_HINC200_CY,
	med_MEDHINC_CY.med_MEDHINC_CY,
	med_AVGHINC_CY.med_AVGHINC_CY,
	med_PCI_CY.med_PCI_CY,
	med_M17025a_B.med_M17025a_B,
	med_X1002_X.med_X1002_X,
	med_M16295a_B.med_M16295a_B,
	med_agg_income.med_agg_income,
	med_agg_75K_HH.med_agg_75K_HH
from companies c
left join
(
	select
		t.company_name,
		AVG(t.TOTPOP_CY) as med_TOTPOP_CY
	from
	(
		select
			d.company_name,
			d.TOTPOP_CY / c.comp_instances as TOTPOP_CY,
			ROW_NUMBER() over( partition by company_name order by d.TOTPOP_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TOTPOP_CY on med_TOTPOP_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.TOTHH_CY) as med_TOTHH_CY
	from
	(
		select
			d.company_name,
			d.TOTHH_CY / c.comp_instances as TOTHH_CY,
			ROW_NUMBER() over( partition by company_name order by d.TOTHH_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TOTHH_CY on med_TOTHH_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MEDAGE_CY) as med_MEDAGE_CY
	from
	(
		select
			d.company_name,
			d.MEDAGE_CY / c.comp_instances as MEDAGE_CY,
			ROW_NUMBER() over( partition by company_name order by d.MEDAGE_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MEDAGE_CY on med_MEDAGE_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC0_CY) as med_HINC0_CY
	from
	(
		select
			d.company_name,
			d.HINC0_CY / c.comp_instances as HINC0_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC0_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC0_CY on med_HINC0_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC15_CY) as med_HINC15_CY
	from
	(
		select
			d.company_name,
			d.HINC15_CY / c.comp_instances as HINC15_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC15_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC15_CY on med_HINC15_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC25_CY) as med_HINC25_CY
	from
	(
		select
			d.company_name,
			d.HINC25_CY / c.comp_instances as HINC25_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC25_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC25_CY on med_HINC25_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC35_CY) as med_HINC35_CY
	from
	(
		select
			d.company_name,
			d.HINC35_CY / c.comp_instances as HINC35_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC35_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC35_CY on med_HINC35_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC50_CY) as med_HINC50_CY
	from
	(
		select
			d.company_name,
			d.HINC50_CY / c.comp_instances as HINC50_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC50_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC50_CY on med_HINC50_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC75_CY) as med_HINC75_CY
	from
	(
		select
			d.company_name,
			d.HINC75_CY / c.comp_instances as HINC75_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC75_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC75_CY on med_HINC75_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC100_CY) as med_HINC100_CY
	from
	(
		select
			d.company_name,
			d.HINC100_CY / c.comp_instances as HINC100_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC100_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC100_CY on med_HINC100_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC150_CY) as med_HINC150_CY
	from
	(
		select
			d.company_name,
			d.HINC150_CY / c.comp_instances as HINC150_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC150_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC150_CY on med_HINC150_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC200_CY) as med_HINC200_CY
	from
	(
		select
			d.company_name,
			d.HINC200_CY / c.comp_instances as HINC200_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC200_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC200_CY on med_HINC200_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MEDHINC_CY) as med_MEDHINC_CY
	from
	(
		select
			d.company_name,
			d.MEDHINC_CY / c.comp_instances as MEDHINC_CY,
			ROW_NUMBER() over( partition by company_name order by d.MEDHINC_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MEDHINC_CY on med_MEDHINC_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AVGHINC_CY) as med_AVGHINC_CY
	from
	(
		select
			d.company_name,
			d.AVGHINC_CY / c.comp_instances as AVGHINC_CY,
			ROW_NUMBER() over( partition by company_name order by d.AVGHINC_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AVGHINC_CY on med_AVGHINC_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.PCI_CY) as med_PCI_CY
	from
	(
		select
			d.company_name,
			d.PCI_CY / c.comp_instances as PCI_CY,
			ROW_NUMBER() over( partition by company_name order by d.PCI_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_PCI_CY on med_PCI_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.M17025a_B) as med_M17025a_B
	from
	(
		select
			d.company_name,
			d.M17025a_B / c.comp_instances as M17025a_B,
			ROW_NUMBER() over( partition by company_name order by d.M17025a_B / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_M17025a_B on med_M17025a_B.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X1002_X) as med_X1002_X
	from
	(
		select
			d.company_name,
			d.X1002_X / c.comp_instances as X1002_X,
			ROW_NUMBER() over( partition by company_name order by d.X1002_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X1002_X on med_X1002_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.M16295a_B) as med_M16295a_B
	from
	(
		select
			d.company_name,
			d.M16295a_B / c.comp_instances as M16295a_B,
			ROW_NUMBER() over( partition by company_name order by d.M16295a_B / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_M16295a_B on med_M16295a_B.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.agg_income) as med_agg_income
	from
	(
		select
			d.company_name,
			d.agg_income / c.comp_instances as agg_income,
			ROW_NUMBER() over( partition by company_name order by d.agg_income / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_agg_income on med_agg_income.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.agg_75K_HH) as med_agg_75K_HH
	from
	(
		select
			d.company_name,
			d.agg_75K_HH / c.comp_instances as agg_75K_HH,
			ROW_NUMBER() over( partition by company_name order by d.agg_75K_HH / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_agg_75K_HH on med_agg_75K_HH.company_name = c.name
order by c.name



