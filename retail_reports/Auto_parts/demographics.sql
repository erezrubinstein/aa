use retaildb_timeseries_auto_parts_v5_shrunken
go

declare @period char(2) = 'PP'
--declare @period char(2) = 'OP'
--declare @period char(2) = 'CL'
--declare @period char(2) = 'CP'


-- temp table for competitive #s
declare @comps table(store_id int, comp_instances int, period char(2))

-- get store counts for prior period
insert into @comps(store_id, comp_instances, period)
select 
	s.store_id,
	comp_instances.count as comp_instances,
	'PP'
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 5
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
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 5
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
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 5
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
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 5
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
med_PCI_CY.med_PCI_CY,
med_ACSTOTHH.med_ACSTOTHH,
med_ACSVEHBASE.med_ACSVEHBASE,
med_ACSOVEH0.med_ACSOVEH0,
med_ACSOVEH1.med_ACSOVEH1,
med_ACSOVEH2.med_ACSOVEH2,
med_ACSOVEH3.med_ACSOVEH3,
med_ACSOVEH4.med_ACSOVEH4,
med_ACSOVEH5UP.med_ACSOVEH5UP,
med_ACSRVEH0.med_ACSRVEH0,
med_ACSRVEH1.med_ACSRVEH1,
med_ACSRVEH2.med_ACSRVEH2,
med_ACSRVEH3.med_ACSRVEH3,
med_ACSRVEH4.med_ACSRVEH4,
med_ACSRVEH5UP.med_ACSRVEH5UP,
med_Year_30.med_Year_30,
med_X6016_X.med_X6016_X,
med_X6011_X.med_X6011_X,
med_X6013_X.med_X6013_X,
med_X6018_X.med_X6018_X,
med_X6017_X.med_X6017_X,
med_X6064_X.med_X6064_X,
med_X6022_X.med_X6022_X,
med_X6039_X.med_X6039_X,
med_X6058_X.med_X6058_X,
med_X6065_X.med_X6065_X,
med_X6035_X.med_X6035_X,
med_X6024_X.med_X6024_X,
med_X6027_X.med_X6027_X,
med_X6025_X.med_X6025_X,
med_X6029_X.med_X6029_X,
med_X6026_X.med_X6026_X,
med_X6037_X.med_X6037_X,
med_X6036_X.med_X6036_X,
med_X6032_X.med_X6032_X,
med_X6031_X.med_X6031_X,
med_X6038_X.med_X6038_X,
med_X6030_X.med_X6030_X,
med_X6033_X.med_X6033_X,
med_X6028_X.med_X6028_X,
med_X6034_X.med_X6034_X,
med_ACSTRANBAS.med_ACSTRANBAS,
med_ACSDRALONE.med_ACSDRALONE,
med_ACSCARPOOL.med_ACSCARPOOL,
med_ACSPUBTRAN.med_ACSPUBTRAN,
med_ACSBUS.med_ACSBUS,
med_ACSSTRTCAR.med_ACSSTRTCAR,
med_ACSSUBWAY.med_ACSSUBWAY,
med_ACSRAILRD.med_ACSRAILRD,
med_ACSFERRY.med_ACSFERRY,
med_ACSTAXICAB.med_ACSTAXICAB,
med_ACSMCYCLE.med_ACSMCYCLE,
med_ACSBICYCLE.med_ACSBICYCLE,
med_ACSWALKED.med_ACSWALKED,
med_ACSOTHTRAN.med_ACSOTHTRAN,
med_ACSWRKHOME.med_ACSWRKHOME,
med_ACSTWRKBAS.med_ACSTWRKBAS,
med_ACSTWORKU5.med_ACSTWORKU5,
med_ACSTWORK5.med_ACSTWORK5,
med_ACSTWORK10.med_ACSTWORK10,
med_ACSTWORK15.med_ACSTWORK15,
med_ACSTWORK20.med_ACSTWORK20,
med_ACSTWORK25.med_ACSTWORK25,
med_ACSTWORK30.med_ACSTWORK30,
med_ACSTWORK35.med_ACSTWORK35,
med_ACSTWORK40.med_ACSTWORK40,
med_ACSTWORK45.med_ACSTWORK45,
med_ACSTWORK60.med_ACSTWORK60,
med_ACSTWORK90.med_ACSTWORK90,
med_agg_income.med_agg_income,
med_traffic.med_traffic,
med_auto_parts_DIY_proxy.med_auto_parts_DIY_proxy,
med_auto_parts_DIFM_proxy.med_auto_parts_DIFM_proxy,
med_auto_fleet.med_auto_fleet,
med_commutation_driving_pct.med_commutation_driving_pct,
med_commutation_commute_time.med_commutation_commute_time
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		from demographics_denorm d
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
		AVG(t.PCI_CY) as med_PCI_CY
	from
	(
		select
			d.company_name,
			d.PCI_CY / c.comp_instances as PCI_CY,
			ROW_NUMBER() over( partition by company_name order by d.PCI_CY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
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
		AVG(t.ACSTOTHH) as med_ACSTOTHH
	from
	(
		select
			d.company_name,
			d.ACSTOTHH / c.comp_instances as ACSTOTHH,
			ROW_NUMBER() over( partition by company_name order by d.ACSTOTHH / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTOTHH on med_ACSTOTHH.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSVEHBASE) as med_ACSVEHBASE
	from
	(
		select
			d.company_name,
			d.ACSVEHBASE / c.comp_instances as ACSVEHBASE,
			ROW_NUMBER() over( partition by company_name order by d.ACSVEHBASE / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSVEHBASE on med_ACSVEHBASE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSOVEH0) as med_ACSOVEH0
	from
	(
		select
			d.company_name,
			d.ACSOVEH0 / c.comp_instances as ACSOVEH0,
			ROW_NUMBER() over( partition by company_name order by d.ACSOVEH0 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSOVEH0 on med_ACSOVEH0.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSOVEH1) as med_ACSOVEH1
	from
	(
		select
			d.company_name,
			d.ACSOVEH1 / c.comp_instances as ACSOVEH1,
			ROW_NUMBER() over( partition by company_name order by d.ACSOVEH1 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSOVEH1 on med_ACSOVEH1.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSOVEH2) as med_ACSOVEH2
	from
	(
		select
			d.company_name,
			d.ACSOVEH2 / c.comp_instances as ACSOVEH2,
			ROW_NUMBER() over( partition by company_name order by d.ACSOVEH2 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSOVEH2 on med_ACSOVEH2.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSOVEH3) as med_ACSOVEH3
	from
	(
		select
			d.company_name,
			d.ACSOVEH3 / c.comp_instances as ACSOVEH3,
			ROW_NUMBER() over( partition by company_name order by d.ACSOVEH3 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSOVEH3 on med_ACSOVEH3.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSOVEH4) as med_ACSOVEH4
	from
	(
		select
			d.company_name,
			d.ACSOVEH4 / c.comp_instances as ACSOVEH4,
			ROW_NUMBER() over( partition by company_name order by d.ACSOVEH4 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSOVEH4 on med_ACSOVEH4.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSOVEH5UP) as med_ACSOVEH5UP
	from
	(
		select
			d.company_name,
			d.ACSOVEH5UP / c.comp_instances as ACSOVEH5UP,
			ROW_NUMBER() over( partition by company_name order by d.ACSOVEH5UP / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSOVEH5UP on med_ACSOVEH5UP.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSRVEH0) as med_ACSRVEH0
	from
	(
		select
			d.company_name,
			d.ACSRVEH0 / c.comp_instances as ACSRVEH0,
			ROW_NUMBER() over( partition by company_name order by d.ACSRVEH0 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSRVEH0 on med_ACSRVEH0.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSRVEH1) as med_ACSRVEH1
	from
	(
		select
			d.company_name,
			d.ACSRVEH1 / c.comp_instances as ACSRVEH1,
			ROW_NUMBER() over( partition by company_name order by d.ACSRVEH1 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSRVEH1 on med_ACSRVEH1.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSRVEH2) as med_ACSRVEH2
	from
	(
		select
			d.company_name,
			d.ACSRVEH2 / c.comp_instances as ACSRVEH2,
			ROW_NUMBER() over( partition by company_name order by d.ACSRVEH2 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSRVEH2 on med_ACSRVEH2.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSRVEH3) as med_ACSRVEH3
	from
	(
		select
			d.company_name,
			d.ACSRVEH3 / c.comp_instances as ACSRVEH3,
			ROW_NUMBER() over( partition by company_name order by d.ACSRVEH3 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSRVEH3 on med_ACSRVEH3.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSRVEH4) as med_ACSRVEH4
	from
	(
		select
			d.company_name,
			d.ACSRVEH4 / c.comp_instances as ACSRVEH4,
			ROW_NUMBER() over( partition by company_name order by d.ACSRVEH4 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSRVEH4 on med_ACSRVEH4.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSRVEH5UP) as med_ACSRVEH5UP
	from
	(
		select
			d.company_name,
			d.ACSRVEH5UP / c.comp_instances as ACSRVEH5UP,
			ROW_NUMBER() over( partition by company_name order by d.ACSRVEH5UP / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSRVEH5UP on med_ACSRVEH5UP.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.Year_30) as med_Year_30
	from
	(
		select
			d.company_name,
			d.Year_30 / c.comp_instances as Year_30,
			ROW_NUMBER() over( partition by company_name order by d.Year_30 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_Year_30 on med_Year_30.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6016_X) as med_X6016_X
	from
	(
		select
			d.company_name,
			d.X6016_X / c.comp_instances as X6016_X,
			ROW_NUMBER() over( partition by company_name order by d.X6016_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6016_X on med_X6016_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6011_X) as med_X6011_X
	from
	(
		select
			d.company_name,
			d.X6011_X / c.comp_instances as X6011_X,
			ROW_NUMBER() over( partition by company_name order by d.X6011_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6011_X on med_X6011_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6013_X) as med_X6013_X
	from
	(
		select
			d.company_name,
			d.X6013_X / c.comp_instances as X6013_X,
			ROW_NUMBER() over( partition by company_name order by d.X6013_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6013_X on med_X6013_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6018_X) as med_X6018_X
	from
	(
		select
			d.company_name,
			d.X6018_X / c.comp_instances as X6018_X,
			ROW_NUMBER() over( partition by company_name order by d.X6018_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6018_X on med_X6018_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6017_X) as med_X6017_X
	from
	(
		select
			d.company_name,
			d.X6017_X / c.comp_instances as X6017_X,
			ROW_NUMBER() over( partition by company_name order by d.X6017_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6017_X on med_X6017_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6064_X) as med_X6064_X
	from
	(
		select
			d.company_name,
			d.X6064_X / c.comp_instances as X6064_X,
			ROW_NUMBER() over( partition by company_name order by d.X6064_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6064_X on med_X6064_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6022_X) as med_X6022_X
	from
	(
		select
			d.company_name,
			d.X6022_X / c.comp_instances as X6022_X,
			ROW_NUMBER() over( partition by company_name order by d.X6022_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6022_X on med_X6022_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6039_X) as med_X6039_X
	from
	(
		select
			d.company_name,
			d.X6039_X / c.comp_instances as X6039_X,
			ROW_NUMBER() over( partition by company_name order by d.X6039_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6039_X on med_X6039_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6058_X) as med_X6058_X
	from
	(
		select
			d.company_name,
			d.X6058_X / c.comp_instances as X6058_X,
			ROW_NUMBER() over( partition by company_name order by d.X6058_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6058_X on med_X6058_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6065_X) as med_X6065_X
	from
	(
		select
			d.company_name,
			d.X6065_X / c.comp_instances as X6065_X,
			ROW_NUMBER() over( partition by company_name order by d.X6065_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6065_X on med_X6065_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6035_X) as med_X6035_X
	from
	(
		select
			d.company_name,
			d.X6035_X / c.comp_instances as X6035_X,
			ROW_NUMBER() over( partition by company_name order by d.X6035_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6035_X on med_X6035_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6024_X) as med_X6024_X
	from
	(
		select
			d.company_name,
			d.X6024_X / c.comp_instances as X6024_X,
			ROW_NUMBER() over( partition by company_name order by d.X6024_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6024_X on med_X6024_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6027_X) as med_X6027_X
	from
	(
		select
			d.company_name,
			d.X6027_X / c.comp_instances as X6027_X,
			ROW_NUMBER() over( partition by company_name order by d.X6027_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6027_X on med_X6027_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6025_X) as med_X6025_X
	from
	(
		select
			d.company_name,
			d.X6025_X / c.comp_instances as X6025_X,
			ROW_NUMBER() over( partition by company_name order by d.X6025_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6025_X on med_X6025_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6029_X) as med_X6029_X
	from
	(
		select
			d.company_name,
			d.X6029_X / c.comp_instances as X6029_X,
			ROW_NUMBER() over( partition by company_name order by d.X6029_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6029_X on med_X6029_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6026_X) as med_X6026_X
	from
	(
		select
			d.company_name,
			d.X6026_X / c.comp_instances as X6026_X,
			ROW_NUMBER() over( partition by company_name order by d.X6026_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6026_X on med_X6026_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6037_X) as med_X6037_X
	from
	(
		select
			d.company_name,
			d.X6037_X / c.comp_instances as X6037_X,
			ROW_NUMBER() over( partition by company_name order by d.X6037_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6037_X on med_X6037_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6036_X) as med_X6036_X
	from
	(
		select
			d.company_name,
			d.X6036_X / c.comp_instances as X6036_X,
			ROW_NUMBER() over( partition by company_name order by d.X6036_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6036_X on med_X6036_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6032_X) as med_X6032_X
	from
	(
		select
			d.company_name,
			d.X6032_X / c.comp_instances as X6032_X,
			ROW_NUMBER() over( partition by company_name order by d.X6032_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6032_X on med_X6032_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6031_X) as med_X6031_X
	from
	(
		select
			d.company_name,
			d.X6031_X / c.comp_instances as X6031_X,
			ROW_NUMBER() over( partition by company_name order by d.X6031_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6031_X on med_X6031_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6038_X) as med_X6038_X
	from
	(
		select
			d.company_name,
			d.X6038_X / c.comp_instances as X6038_X,
			ROW_NUMBER() over( partition by company_name order by d.X6038_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6038_X on med_X6038_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6030_X) as med_X6030_X
	from
	(
		select
			d.company_name,
			d.X6030_X / c.comp_instances as X6030_X,
			ROW_NUMBER() over( partition by company_name order by d.X6030_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6030_X on med_X6030_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6033_X) as med_X6033_X
	from
	(
		select
			d.company_name,
			d.X6033_X / c.comp_instances as X6033_X,
			ROW_NUMBER() over( partition by company_name order by d.X6033_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6033_X on med_X6033_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6028_X) as med_X6028_X
	from
	(
		select
			d.company_name,
			d.X6028_X / c.comp_instances as X6028_X,
			ROW_NUMBER() over( partition by company_name order by d.X6028_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6028_X on med_X6028_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X6034_X) as med_X6034_X
	from
	(
		select
			d.company_name,
			d.X6034_X / c.comp_instances as X6034_X,
			ROW_NUMBER() over( partition by company_name order by d.X6034_X / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X6034_X on med_X6034_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTRANBAS) as med_ACSTRANBAS
	from
	(
		select
			d.company_name,
			d.ACSTRANBAS / c.comp_instances as ACSTRANBAS,
			ROW_NUMBER() over( partition by company_name order by d.ACSTRANBAS / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTRANBAS on med_ACSTRANBAS.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSDRALONE) as med_ACSDRALONE
	from
	(
		select
			d.company_name,
			d.ACSDRALONE / c.comp_instances as ACSDRALONE,
			ROW_NUMBER() over( partition by company_name order by d.ACSDRALONE / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSDRALONE on med_ACSDRALONE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSCARPOOL) as med_ACSCARPOOL
	from
	(
		select
			d.company_name,
			d.ACSCARPOOL / c.comp_instances as ACSCARPOOL,
			ROW_NUMBER() over( partition by company_name order by d.ACSCARPOOL / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSCARPOOL on med_ACSCARPOOL.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSPUBTRAN) as med_ACSPUBTRAN
	from
	(
		select
			d.company_name,
			d.ACSPUBTRAN / c.comp_instances as ACSPUBTRAN,
			ROW_NUMBER() over( partition by company_name order by d.ACSPUBTRAN / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSPUBTRAN on med_ACSPUBTRAN.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSBUS) as med_ACSBUS
	from
	(
		select
			d.company_name,
			d.ACSBUS / c.comp_instances as ACSBUS,
			ROW_NUMBER() over( partition by company_name order by d.ACSBUS / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSBUS on med_ACSBUS.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSSTRTCAR) as med_ACSSTRTCAR
	from
	(
		select
			d.company_name,
			d.ACSSTRTCAR / c.comp_instances as ACSSTRTCAR,
			ROW_NUMBER() over( partition by company_name order by d.ACSSTRTCAR / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSSTRTCAR on med_ACSSTRTCAR.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSSUBWAY) as med_ACSSUBWAY
	from
	(
		select
			d.company_name,
			d.ACSSUBWAY / c.comp_instances as ACSSUBWAY,
			ROW_NUMBER() over( partition by company_name order by d.ACSSUBWAY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSSUBWAY on med_ACSSUBWAY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSRAILRD) as med_ACSRAILRD
	from
	(
		select
			d.company_name,
			d.ACSRAILRD / c.comp_instances as ACSRAILRD,
			ROW_NUMBER() over( partition by company_name order by d.ACSRAILRD / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSRAILRD on med_ACSRAILRD.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSFERRY) as med_ACSFERRY
	from
	(
		select
			d.company_name,
			d.ACSFERRY / c.comp_instances as ACSFERRY,
			ROW_NUMBER() over( partition by company_name order by d.ACSFERRY / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSFERRY on med_ACSFERRY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTAXICAB) as med_ACSTAXICAB
	from
	(
		select
			d.company_name,
			d.ACSTAXICAB / c.comp_instances as ACSTAXICAB,
			ROW_NUMBER() over( partition by company_name order by d.ACSTAXICAB / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTAXICAB on med_ACSTAXICAB.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSMCYCLE) as med_ACSMCYCLE
	from
	(
		select
			d.company_name,
			d.ACSMCYCLE / c.comp_instances as ACSMCYCLE,
			ROW_NUMBER() over( partition by company_name order by d.ACSMCYCLE / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSMCYCLE on med_ACSMCYCLE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSBICYCLE) as med_ACSBICYCLE
	from
	(
		select
			d.company_name,
			d.ACSBICYCLE / c.comp_instances as ACSBICYCLE,
			ROW_NUMBER() over( partition by company_name order by d.ACSBICYCLE / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSBICYCLE on med_ACSBICYCLE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSWALKED) as med_ACSWALKED
	from
	(
		select
			d.company_name,
			d.ACSWALKED / c.comp_instances as ACSWALKED,
			ROW_NUMBER() over( partition by company_name order by d.ACSWALKED / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSWALKED on med_ACSWALKED.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSOTHTRAN) as med_ACSOTHTRAN
	from
	(
		select
			d.company_name,
			d.ACSOTHTRAN / c.comp_instances as ACSOTHTRAN,
			ROW_NUMBER() over( partition by company_name order by d.ACSOTHTRAN / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSOTHTRAN on med_ACSOTHTRAN.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSWRKHOME) as med_ACSWRKHOME
	from
	(
		select
			d.company_name,
			d.ACSWRKHOME / c.comp_instances as ACSWRKHOME,
			ROW_NUMBER() over( partition by company_name order by d.ACSWRKHOME / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSWRKHOME on med_ACSWRKHOME.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWRKBAS) as med_ACSTWRKBAS
	from
	(
		select
			d.company_name,
			d.ACSTWRKBAS / c.comp_instances as ACSTWRKBAS,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWRKBAS / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWRKBAS on med_ACSTWRKBAS.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORKU5) as med_ACSTWORKU5
	from
	(
		select
			d.company_name,
			d.ACSTWORKU5 / c.comp_instances as ACSTWORKU5,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORKU5 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORKU5 on med_ACSTWORKU5.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK5) as med_ACSTWORK5
	from
	(
		select
			d.company_name,
			d.ACSTWORK5 / c.comp_instances as ACSTWORK5,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK5 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK5 on med_ACSTWORK5.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK10) as med_ACSTWORK10
	from
	(
		select
			d.company_name,
			d.ACSTWORK10 / c.comp_instances as ACSTWORK10,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK10 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK10 on med_ACSTWORK10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK15) as med_ACSTWORK15
	from
	(
		select
			d.company_name,
			d.ACSTWORK15 / c.comp_instances as ACSTWORK15,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK15 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK15 on med_ACSTWORK15.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK20) as med_ACSTWORK20
	from
	(
		select
			d.company_name,
			d.ACSTWORK20 / c.comp_instances as ACSTWORK20,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK20 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK20 on med_ACSTWORK20.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK25) as med_ACSTWORK25
	from
	(
		select
			d.company_name,
			d.ACSTWORK25 / c.comp_instances as ACSTWORK25,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK25 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK25 on med_ACSTWORK25.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK30) as med_ACSTWORK30
	from
	(
		select
			d.company_name,
			d.ACSTWORK30 / c.comp_instances as ACSTWORK30,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK30 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK30 on med_ACSTWORK30.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK35) as med_ACSTWORK35
	from
	(
		select
			d.company_name,
			d.ACSTWORK35 / c.comp_instances as ACSTWORK35,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK35 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK35 on med_ACSTWORK35.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK40) as med_ACSTWORK40
	from
	(
		select
			d.company_name,
			d.ACSTWORK40 / c.comp_instances as ACSTWORK40,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK40 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK40 on med_ACSTWORK40.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK45) as med_ACSTWORK45
	from
	(
		select
			d.company_name,
			d.ACSTWORK45 / c.comp_instances as ACSTWORK45,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK45 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK45 on med_ACSTWORK45.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK60) as med_ACSTWORK60
	from
	(
		select
			d.company_name,
			d.ACSTWORK60 / c.comp_instances as ACSTWORK60,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK60 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK60 on med_ACSTWORK60.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ACSTWORK90) as med_ACSTWORK90
	from
	(
		select
			d.company_name,
			d.ACSTWORK90 / c.comp_instances as ACSTWORK90,
			ROW_NUMBER() over( partition by company_name order by d.ACSTWORK90 / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ACSTWORK90 on med_ACSTWORK90.company_name = c.name

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
		from demographics_denorm d
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
		AVG(t.traffic) as med_traffic
	from
	(
		select
			d.company_name,
			d.traffic / c.comp_instances as traffic,
			ROW_NUMBER() over( partition by company_name order by d.traffic / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_traffic on med_traffic.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.auto_parts_DIY_proxy) as med_auto_parts_DIY_proxy
	from
	(
		select
			d.company_name,
			d.auto_parts_DIY_proxy / c.comp_instances as auto_parts_DIY_proxy,
			ROW_NUMBER() over( partition by company_name order by d.auto_parts_DIY_proxy / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_auto_parts_DIY_proxy on med_auto_parts_DIY_proxy.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.auto_parts_DIFM_proxy) as med_auto_parts_DIFM_proxy
	from
	(
		select
			d.company_name,
			d.auto_parts_DIFM_proxy / c.comp_instances as auto_parts_DIFM_proxy,
			ROW_NUMBER() over( partition by company_name order by d.auto_parts_DIFM_proxy / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_auto_parts_DIFM_proxy on med_auto_parts_DIFM_proxy.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.auto_fleet) as med_auto_fleet
	from
	(
		select
			d.company_name,
			d.auto_fleet / c.comp_instances as auto_fleet,
			ROW_NUMBER() over( partition by company_name order by d.auto_fleet / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_auto_fleet on med_auto_fleet.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.commutation_driving_pct) as med_commutation_driving_pct
	from
	(
		select
			d.company_name,
			d.commutation_driving_pct / c.comp_instances as commutation_driving_pct,
			ROW_NUMBER() over( partition by company_name order by d.commutation_driving_pct / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_commutation_driving_pct on med_commutation_driving_pct.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.commutation_commute_time) as med_commutation_commute_time
	from
	(
		select
			d.company_name,
			d.commutation_commute_time / c.comp_instances as commutation_commute_time,
			ROW_NUMBER() over( partition by company_name order by d.commutation_commute_time / c.comp_instances asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_commutation_commute_time on med_commutation_commute_time.company_name = c.name

order by c.name



