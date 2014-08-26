use retaildb_timeseries_staging_myeyedr
go

declare @period char(2) = 'PP'
--declare @period char(2) = 'OP'
--declare @period char(2) = 'CL'
--declare @period char(2) = 'CP'

-- threshold baby!
declare @threshold_id int = 5


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
med_POP0_CY.med_POP0_CY,
med_POP5_CY.med_POP5_CY,
med_POP10_CY.med_POP10_CY,
med_POP15_CY.med_POP15_CY,
med_POP20_CY.med_POP20_CY,
med_POP2534_CY.med_POP2534_CY,
med_POP3544_CY.med_POP3544_CY,
med_POP4554_CY.med_POP4554_CY,
med_POP5564_CY.med_POP5564_CY,
med_POP6574_CY.med_POP6574_CY,
med_POP7584_CY.med_POP7584_CY,
med_POP85_CY.med_POP85_CY,
med_WHITE_CY.med_WHITE_CY,
med_BLACK_CY.med_BLACK_CY,
med_AMERIND_CY.med_AMERIND_CY,
med_ASIAN_CY.med_ASIAN_CY,
med_PACIFIC_CY.med_PACIFIC_CY,
med_OTHRACE_CY.med_OTHRACE_CY,
med_RACE2UP_CY.med_RACE2UP_CY,
med_HISPPOPCY.med_HISPPOPCY,
med_M17068a_B.med_M17068a_B,
med_M17074a_B.med_M17074a_B,
med_M17082a_B.med_M17082a_B,
med_M17083a_B.med_M17083a_B,
med_M17084a_B.med_M17084a_B,
med_M17113a_B.med_M17113a_B,
med_X8033_X.med_X8033_X,
med_X8021_X.med_X8021_X,
med_agg_income.med_agg_income
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
			d.TOTPOP_CY,
			ROW_NUMBER() over( partition by company_name order by d.TOTPOP_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.TOTHH_CY,
			ROW_NUMBER() over( partition by company_name order by d.TOTHH_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.MEDAGE_CY,
			ROW_NUMBER() over( partition by company_name order by d.MEDAGE_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC0_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC0_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC15_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC15_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC25_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC25_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC35_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC35_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC50_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC50_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC75_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC75_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC100_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC100_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC150_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC150_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.HINC200_CY,
			ROW_NUMBER() over( partition by company_name order by d.HINC200_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.MEDHINC_CY,
			ROW_NUMBER() over( partition by company_name order by d.MEDHINC_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.AVGHINC_CY,
			ROW_NUMBER() over( partition by company_name order by d.AVGHINC_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
			d.PCI_CY,
			ROW_NUMBER() over( partition by company_name order by d.PCI_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
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
		AVG(t.POP0_CY) as med_POP0_CY
	from
	(
		select
			d.company_name,
			d.POP0_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP0_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP0_CY on med_POP0_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5_CY) as med_POP5_CY
	from
	(
		select
			d.company_name,
			d.POP5_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP5_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5_CY on med_POP5_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP10_CY) as med_POP10_CY
	from
	(
		select
			d.company_name,
			d.POP10_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP10_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP10_CY on med_POP10_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP15_CY) as med_POP15_CY
	from
	(
		select
			d.company_name,
			d.POP15_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP15_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP15_CY on med_POP15_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP20_CY) as med_POP20_CY
	from
	(
		select
			d.company_name,
			d.POP20_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP20_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP20_CY on med_POP20_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP2534_CY) as med_POP2534_CY
	from
	(
		select
			d.company_name,
			d.POP2534_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP2534_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP2534_CY on med_POP2534_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP3544_CY) as med_POP3544_CY
	from
	(
		select
			d.company_name,
			d.POP3544_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP3544_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP3544_CY on med_POP3544_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP4554_CY) as med_POP4554_CY
	from
	(
		select
			d.company_name,
			d.POP4554_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP4554_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP4554_CY on med_POP4554_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5564_CY) as med_POP5564_CY
	from
	(
		select
			d.company_name,
			d.POP5564_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP5564_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5564_CY on med_POP5564_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP6574_CY) as med_POP6574_CY
	from
	(
		select
			d.company_name,
			d.POP6574_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP6574_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP6574_CY on med_POP6574_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP7584_CY) as med_POP7584_CY
	from
	(
		select
			d.company_name,
			d.POP7584_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP7584_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP7584_CY on med_POP7584_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP85_CY) as med_POP85_CY
	from
	(
		select
			d.company_name,
			d.POP85_CY,
			ROW_NUMBER() over( partition by company_name order by d.POP85_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP85_CY on med_POP85_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.WHITE_CY) as med_WHITE_CY
	from
	(
		select
			d.company_name,
			d.WHITE_CY,
			ROW_NUMBER() over( partition by company_name order by d.WHITE_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_WHITE_CY on med_WHITE_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.BLACK_CY) as med_BLACK_CY
	from
	(
		select
			d.company_name,
			d.BLACK_CY,
			ROW_NUMBER() over( partition by company_name order by d.BLACK_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_BLACK_CY on med_BLACK_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AMERIND_CY) as med_AMERIND_CY
	from
	(
		select
			d.company_name,
			d.AMERIND_CY,
			ROW_NUMBER() over( partition by company_name order by d.AMERIND_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AMERIND_CY on med_AMERIND_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ASIAN_CY) as med_ASIAN_CY
	from
	(
		select
			d.company_name,
			d.ASIAN_CY,
			ROW_NUMBER() over( partition by company_name order by d.ASIAN_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ASIAN_CY on med_ASIAN_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.PACIFIC_CY) as med_PACIFIC_CY
	from
	(
		select
			d.company_name,
			d.PACIFIC_CY,
			ROW_NUMBER() over( partition by company_name order by d.PACIFIC_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_PACIFIC_CY on med_PACIFIC_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OTHRACE_CY) as med_OTHRACE_CY
	from
	(
		select
			d.company_name,
			d.OTHRACE_CY,
			ROW_NUMBER() over( partition by company_name order by d.OTHRACE_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OTHRACE_CY on med_OTHRACE_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.RACE2UP_CY) as med_RACE2UP_CY
	from
	(
		select
			d.company_name,
			d.RACE2UP_CY,
			ROW_NUMBER() over( partition by company_name order by d.RACE2UP_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RACE2UP_CY on med_RACE2UP_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HISPPOPCY) as med_HISPPOPCY
	from
	(
		select
			d.company_name,
			d.HISPPOPCY,
			ROW_NUMBER() over( partition by company_name order by d.HISPPOPCY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HISPPOPCY on med_HISPPOPCY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.M17068a_B) as med_M17068a_B
	from
	(
		select
			d.company_name,
			d.M17068a_B,
			ROW_NUMBER() over( partition by company_name order by d.M17068a_B asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_M17068a_B on med_M17068a_B.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.M17074a_B) as med_M17074a_B
	from
	(
		select
			d.company_name,
			d.M17074a_B,
			ROW_NUMBER() over( partition by company_name order by d.M17074a_B asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_M17074a_B on med_M17074a_B.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.M17082a_B) as med_M17082a_B
	from
	(
		select
			d.company_name,
			d.M17082a_B,
			ROW_NUMBER() over( partition by company_name order by d.M17082a_B asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_M17082a_B on med_M17082a_B.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.M17083a_B) as med_M17083a_B
	from
	(
		select
			d.company_name,
			d.M17083a_B,
			ROW_NUMBER() over( partition by company_name order by d.M17083a_B asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_M17083a_B on med_M17083a_B.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.M17084a_B) as med_M17084a_B
	from
	(
		select
			d.company_name,
			d.M17084a_B,
			ROW_NUMBER() over( partition by company_name order by d.M17084a_B asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_M17084a_B on med_M17084a_B.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.M17113a_B) as med_M17113a_B
	from
	(
		select
			d.company_name,
			d.M17113a_B,
			ROW_NUMBER() over( partition by company_name order by d.M17113a_B asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_M17113a_B on med_M17113a_B.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X8033_X) as med_X8033_X
	from
	(
		select
			d.company_name,
			d.X8033_X,
			ROW_NUMBER() over( partition by company_name order by d.X8033_X asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X8033_X on med_X8033_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.X8021_X) as med_X8021_X
	from
	(
		select
			d.company_name,
			d.X8021_X,
			ROW_NUMBER() over( partition by company_name order by d.X8021_X asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_X8021_X on med_X8021_X.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.agg_income) as med_agg_income
	from
	(
		select
			d.company_name,
			d.agg_income,
			ROW_NUMBER() over( partition by company_name order by d.agg_income asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_5_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_agg_income on med_agg_income.company_name = c.name


order by c.name



