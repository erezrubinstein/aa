use retaildb_timeseries_uggs
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
	select count(*) + 1 as count
	from competitive_stores cs
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
	select count(*) + 1 as count
	from competitive_stores cs
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
	select count(*) + 1 as count
	from competitive_stores cs
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
	select count(*) + 1 as count
	from competitive_stores cs
	where trade_area_id = t.trade_area_id
		and end_date is null
) comp_instances
where s.assumed_closed_date is null










-- get stats

select 
	c.name,
	med_TOTPOP10.med_TOTPOP10,
med_TOTPOP_CY.med_TOTPOP_CY,
med_TOTPOP_FY.med_TOTPOP_FY,
med_TOTHH10.med_TOTHH10,
med_TOTHH_CY.med_TOTHH_CY,
med_TOTHH_FY.med_TOTHH_FY,
med_FAMHH10.med_FAMHH10,
med_FAMHH_CY.med_FAMHH_CY,
med_FAMHH_FY.med_FAMHH_FY,
med_AVGHHSZ10.med_AVGHHSZ10,
med_AVGHHSZ_CY.med_AVGHHSZ_CY,
med_AVGHHSZ_FY.med_AVGHHSZ_FY,
med_OWNER10.med_OWNER10,
med_OWNER_CY.med_OWNER_CY,
med_OWNER_FY.med_OWNER_FY,
med_RENTER10.med_RENTER10,
med_RENTER_CY.med_RENTER_CY,
med_RENTER_FY.med_RENTER_FY,
med_MEDAGE10.med_MEDAGE10,
med_MEDAGE_CY.med_MEDAGE_CY,
med_MEDAGE_FY.med_MEDAGE_FY,
med_SCRIPT_ANU.med_SCRIPT_ANU,
med_POPRATE_S.med_POPRATE_S,
med_TR_POP_NAT.med_TR_POP_NAT,
med_SCRIPT_A_1.med_SCRIPT_A_1,
med_HHRATE_S.med_HHRATE_S,
med_TR_HH_NAT.med_TR_HH_NAT,
med_SCRIPT_A_2.med_SCRIPT_A_2,
med_FAMRATE_S.med_FAMRATE_S,
med_TR_FAM_NAT.med_TR_FAM_NAT,
med_SCRIPT_AN1.med_SCRIPT_AN1,
med_OWNRATE_S.med_OWNRATE_S,
med_TR_OWN_NAT.med_TR_OWN_NAT,
med_SCRIPT_AN0.med_SCRIPT_AN0,
med_INCRATE_S.med_INCRATE_S,
med_TR_MHI_NAT.med_TR_MHI_NAT,
med_HINC0_CY.med_HINC0_CY,
med_HINC0_CY_P.med_HINC0_CY_P,
med_HINC0_FY.med_HINC0_FY,
med_HINC0_FY_P.med_HINC0_FY_P,
med_HINC15_CY.med_HINC15_CY,
med_HINC15_CY_P.med_HINC15_CY_P,
med_HINC15_FY.med_HINC15_FY,
med_HINC15_FY_P.med_HINC15_FY_P,
med_HINC25_CY.med_HINC25_CY,
med_HINC25_CY_P.med_HINC25_CY_P,
med_HINC25_FY.med_HINC25_FY,
med_HINC25_FY_P.med_HINC25_FY_P,
med_HINC35_CY.med_HINC35_CY,
med_HINC35_CY_P.med_HINC35_CY_P,
med_HINC35_FY.med_HINC35_FY,
med_HINC35_FY_P.med_HINC35_FY_P,
med_HINC50_CY.med_HINC50_CY,
med_HINC50_CY_P.med_HINC50_CY_P,
med_HINC50_FY.med_HINC50_FY,
med_HINC50_FY_P.med_HINC50_FY_P,
med_HINC75_CY.med_HINC75_CY,
med_HINC75_CY_P.med_HINC75_CY_P,
med_HINC75_FY.med_HINC75_FY,
med_HINC75_FY_P.med_HINC75_FY_P,
med_HINC100_CY.med_HINC100_CY,
med_HINC100_CY_P.med_HINC100_CY_P,
med_HINC100_FY.med_HINC100_FY,
med_HINC100_FY_P.med_HINC100_FY_P,
med_HINC150_CY.med_HINC150_CY,
med_HINC150_CY_P.med_HINC150_CY_P,
med_HINC150_FY.med_HINC150_FY,
med_HINC150_FY_P.med_HINC150_FY_P,
med_HINC200_CY.med_HINC200_CY,
med_HINC200_CY_P.med_HINC200_CY_P,
med_HINC200_FY.med_HINC200_FY,
med_HINC200_FY_P.med_HINC200_FY_P,
med_MEDHINC_CY.med_MEDHINC_CY,
med_MEDHINC_FY.med_MEDHINC_FY,
med_AVGHINC_CY.med_AVGHINC_CY,
med_AVGHINC_FY.med_AVGHINC_FY,
med_PCI_CY.med_PCI_CY,
med_PCI_FY.med_PCI_FY,
med_POP0C10.med_POP0C10,
med_POP0C10_P.med_POP0C10_P,
med_POP0_CY.med_POP0_CY,
med_POP0_CY_P.med_POP0_CY_P,
med_POP0_FY.med_POP0_FY,
med_POP0_FY_P.med_POP0_FY_P,
med_POP5C10.med_POP5C10,
med_POP5C10_P.med_POP5C10_P,
med_POP5_CY.med_POP5_CY,
med_POP5_CY_P.med_POP5_CY_P,
med_POP5_FY.med_POP5_FY,
med_POP5_FY_P.med_POP5_FY_P,
med_POP10C10.med_POP10C10,
med_POP10C10_P.med_POP10C10_P,
med_POP10_CY.med_POP10_CY,
med_POP10_CY_P.med_POP10_CY_P,
med_POP10_FY.med_POP10_FY,
med_POP10_FY_P.med_POP10_FY_P,
med_POP15C10.med_POP15C10,
med_POP15C10_P.med_POP15C10_P,
med_POP15_CY.med_POP15_CY,
med_POP15_CY_P.med_POP15_CY_P,
med_POP15_FY.med_POP15_FY,
med_POP15_FY_P.med_POP15_FY_P,
med_POP20C10.med_POP20C10,
med_POP20C10_P.med_POP20C10_P,
med_POP20_CY.med_POP20_CY,
med_POP20_CY_P.med_POP20_CY_P,
med_POP20_FY.med_POP20_FY,
med_POP20_FY_P.med_POP20_FY_P,
med_POP2534C10.med_POP2534C10,
med_POP2534C10_P.med_POP2534C10_P,
med_POP2534_CY.med_POP2534_CY,
med_POP2534_CY_P.med_POP2534_CY_P,
med_POP2534_FY.med_POP2534_FY,
med_POP2534_FY_P.med_POP2534_FY_P,
med_POP3544C10.med_POP3544C10,
med_POP3544C10_P.med_POP3544C10_P,
med_POP3544_CY.med_POP3544_CY,
med_POP3544_CY_P.med_POP3544_CY_P,
med_POP3544_FY.med_POP3544_FY,
med_POP3544_FY_P.med_POP3544_FY_P,
med_POP4554C10.med_POP4554C10,
med_POP4554C10_P.med_POP4554C10_P,
med_POP4554_CY.med_POP4554_CY,
med_POP4554_CY_P.med_POP4554_CY_P,
med_POP4554_FY.med_POP4554_FY,
med_POP4554_FY_P.med_POP4554_FY_P,
med_POP5564C10.med_POP5564C10,
med_POP5564C10_P.med_POP5564C10_P,
med_POP5564_CY.med_POP5564_CY,
med_POP5564_CY_P.med_POP5564_CY_P,
med_POP5564_FY.med_POP5564_FY,
med_POP5564_FY_P.med_POP5564_FY_P,
med_POP6574C10.med_POP6574C10,
med_POP6574C10_P.med_POP6574C10_P,
med_POP6574_CY.med_POP6574_CY,
med_POP6574_CY_P.med_POP6574_CY_P,
med_POP6574_FY.med_POP6574_FY,
med_POP6574_FY_P.med_POP6574_FY_P,
med_POP7584C10.med_POP7584C10,
med_POP7584C10_P.med_POP7584C10_P,
med_POP7584_CY.med_POP7584_CY,
med_POP7584_CY_P.med_POP7584_CY_P,
med_POP7584_FY.med_POP7584_FY,
med_POP7584_FY_P.med_POP7584_FY_P,
med_POP85C10.med_POP85C10,
med_POP85PC10_P.med_POP85PC10_P,
med_POP85_CY.med_POP85_CY,
med_POP85P_CY_P.med_POP85P_CY_P,
med_POP85_FY.med_POP85_FY,
med_POP85P_FY_P.med_POP85P_FY_P,
med_WHITE10.med_WHITE10,
med_WHITE10_P.med_WHITE10_P,
med_WHITE_CY.med_WHITE_CY,
med_WHITE_CY_P.med_WHITE_CY_P,
med_WHITE_FY.med_WHITE_FY,
med_WHITE_FY_P.med_WHITE_FY_P,
med_BLACK10.med_BLACK10,
med_BLACK10_P.med_BLACK10_P,
med_BLACK_CY.med_BLACK_CY,
med_BLACK_CY_P.med_BLACK_CY_P,
med_BLACK_FY.med_BLACK_FY,
med_BLACK_FY_P.med_BLACK_FY_P,
med_AMERIND10.med_AMERIND10,
med_AMERIND10_P.med_AMERIND10_P,
med_AMERIND_CY.med_AMERIND_CY,
med_AMERIND_CY_P.med_AMERIND_CY_P,
med_AMERIND_FY.med_AMERIND_FY,
med_AMERIND_FY_P.med_AMERIND_FY_P,
med_ASIAN10.med_ASIAN10,
med_ASIAN10_P.med_ASIAN10_P,
med_ASIAN_CY.med_ASIAN_CY,
med_ASIAN_CY_P.med_ASIAN_CY_P,
med_ASIAN_FY.med_ASIAN_FY,
med_ASIAN_FY_P.med_ASIAN_FY_P,
med_PACIFIC10.med_PACIFIC10,
med_PACIFIC10_P.med_PACIFIC10_P,
med_PACIFIC_CY.med_PACIFIC_CY,
med_PACIFIC_CY_P.med_PACIFIC_CY_P,
med_PACIFIC_FY.med_PACIFIC_FY,
med_PACIFIC_FY_P.med_PACIFIC_FY_P,
med_OTHRACE10.med_OTHRACE10,
med_OTHRACE10_P.med_OTHRACE10_P,
med_OTHRACE_CY.med_OTHRACE_CY,
med_OTHRACE_CY_P.med_OTHRACE_CY_P,
med_OTHRACE_FY.med_OTHRACE_FY,
med_OTHRACE_FY_P.med_OTHRACE_FY_P,
med_RACE2UP10.med_RACE2UP10,
med_RACE2UP10_P.med_RACE2UP10_P,
med_RACE2UP_CY.med_RACE2UP_CY,
med_RACE2UP_CY_P.med_RACE2UP_CY_P,
med_RACE2UP_FY.med_RACE2UP_FY,
med_RACE2UP_FY_P.med_RACE2UP_FY_P,
med_HISPPOP10.med_HISPPOP10,
med_HISPPOP10_P.med_HISPPOP10_P,
med_HISPPOPCY.med_HISPPOPCY,
med_HISPPOP_CY_P.med_HISPPOP_CY_P,
med_HISPPOPFY.med_HISPPOPFY,
med_HISPPOPFY_P.med_HISPPOPFY_P,
med_POPRATE.med_POPRATE,
med_HHRATE.med_HHRATE,
med_FAMRATE.med_FAMRATE,
med_OWNRATE.med_OWNRATE,
med_INCRATE.med_INCRATE,
med_MALE0C10.med_MALE0C10,
med_MALE5C10.med_MALE5C10,
med_MALE10C10.med_MALE10C10,
med_MALE15C10.med_MALE15C10,
med_MALE20C10.med_MALE20C10,
med_MALE25C10.med_MALE25C10,
med_MALE30C10.med_MALE30C10,
med_MALE35C10.med_MALE35C10,
med_MALE40C10.med_MALE40C10,
med_MALE45C10.med_MALE45C10,
med_MALE50C10.med_MALE50C10,
med_MALE55C10.med_MALE55C10,
med_MALE60C10.med_MALE60C10,
med_MALE65C10.med_MALE65C10,
med_MALE70C10.med_MALE70C10,
med_MALE75C10.med_MALE75C10,
med_MALE80C10.med_MALE80C10,
med_MALE85C10.med_MALE85C10,
med_MAL18UP10.med_MAL18UP10,
med_MAL21UP10.med_MAL21UP10,
med_MEDMAGE10.med_MEDMAGE10,
med_FEM0C10.med_FEM0C10,
med_FEM5C10.med_FEM5C10,
med_FEM10C10.med_FEM10C10,
med_FEM15C10.med_FEM15C10,
med_FEM20C10.med_FEM20C10,
med_FEM25C10.med_FEM25C10,
med_FEM30C10.med_FEM30C10,
med_FEM35C10.med_FEM35C10,
med_FEM40C10.med_FEM40C10,
med_FEM45C10.med_FEM45C10,
med_FEM50C10.med_FEM50C10,
med_FEM55C10.med_FEM55C10,
med_FEM60C10.med_FEM60C10,
med_FEM65C10.med_FEM65C10,
med_FEM70C10.med_FEM70C10,
med_FEM75C10.med_FEM75C10,
med_FEM80C10.med_FEM80C10,
med_FEM85C10.med_FEM85C10,
med_FEM18UP10.med_FEM18UP10,
med_FEM21UP10.med_FEM21UP10,
med_MEDFAGE10.med_MEDFAGE10,
med_agg_income.med_agg_income
from companies c
left join
(
	select
		t.company_name,
		AVG(t.TOTPOP10) as med_TOTPOP10
	from
	(
		select
			d.company_name,
			d.TOTPOP10,
			ROW_NUMBER() over( partition by company_name order by d.TOTPOP10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TOTPOP10 on med_TOTPOP10.company_name = c.name

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
		AVG(t.TOTPOP_FY) as med_TOTPOP_FY
	from
	(
		select
			d.company_name,
			d.TOTPOP_FY,
			ROW_NUMBER() over( partition by company_name order by d.TOTPOP_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TOTPOP_FY on med_TOTPOP_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.TOTHH10) as med_TOTHH10
	from
	(
		select
			d.company_name,
			d.TOTHH10,
			ROW_NUMBER() over( partition by company_name order by d.TOTHH10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TOTHH10 on med_TOTHH10.company_name = c.name

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
		AVG(t.TOTHH_FY) as med_TOTHH_FY
	from
	(
		select
			d.company_name,
			d.TOTHH_FY,
			ROW_NUMBER() over( partition by company_name order by d.TOTHH_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TOTHH_FY on med_TOTHH_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FAMHH10) as med_FAMHH10
	from
	(
		select
			d.company_name,
			d.FAMHH10,
			ROW_NUMBER() over( partition by company_name order by d.FAMHH10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FAMHH10 on med_FAMHH10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FAMHH_CY) as med_FAMHH_CY
	from
	(
		select
			d.company_name,
			d.FAMHH_CY,
			ROW_NUMBER() over( partition by company_name order by d.FAMHH_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FAMHH_CY on med_FAMHH_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FAMHH_FY) as med_FAMHH_FY
	from
	(
		select
			d.company_name,
			d.FAMHH_FY,
			ROW_NUMBER() over( partition by company_name order by d.FAMHH_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FAMHH_FY on med_FAMHH_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AVGHHSZ10) as med_AVGHHSZ10
	from
	(
		select
			d.company_name,
			d.AVGHHSZ10,
			ROW_NUMBER() over( partition by company_name order by d.AVGHHSZ10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AVGHHSZ10 on med_AVGHHSZ10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AVGHHSZ_CY) as med_AVGHHSZ_CY
	from
	(
		select
			d.company_name,
			d.AVGHHSZ_CY,
			ROW_NUMBER() over( partition by company_name order by d.AVGHHSZ_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AVGHHSZ_CY on med_AVGHHSZ_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AVGHHSZ_FY) as med_AVGHHSZ_FY
	from
	(
		select
			d.company_name,
			d.AVGHHSZ_FY,
			ROW_NUMBER() over( partition by company_name order by d.AVGHHSZ_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AVGHHSZ_FY on med_AVGHHSZ_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OWNER10) as med_OWNER10
	from
	(
		select
			d.company_name,
			d.OWNER10,
			ROW_NUMBER() over( partition by company_name order by d.OWNER10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OWNER10 on med_OWNER10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OWNER_CY) as med_OWNER_CY
	from
	(
		select
			d.company_name,
			d.OWNER_CY,
			ROW_NUMBER() over( partition by company_name order by d.OWNER_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OWNER_CY on med_OWNER_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OWNER_FY) as med_OWNER_FY
	from
	(
		select
			d.company_name,
			d.OWNER_FY,
			ROW_NUMBER() over( partition by company_name order by d.OWNER_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OWNER_FY on med_OWNER_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.RENTER10) as med_RENTER10
	from
	(
		select
			d.company_name,
			d.RENTER10,
			ROW_NUMBER() over( partition by company_name order by d.RENTER10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RENTER10 on med_RENTER10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.RENTER_CY) as med_RENTER_CY
	from
	(
		select
			d.company_name,
			d.RENTER_CY,
			ROW_NUMBER() over( partition by company_name order by d.RENTER_CY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RENTER_CY on med_RENTER_CY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.RENTER_FY) as med_RENTER_FY
	from
	(
		select
			d.company_name,
			d.RENTER_FY,
			ROW_NUMBER() over( partition by company_name order by d.RENTER_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RENTER_FY on med_RENTER_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MEDAGE10) as med_MEDAGE10
	from
	(
		select
			d.company_name,
			d.MEDAGE10,
			ROW_NUMBER() over( partition by company_name order by d.MEDAGE10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MEDAGE10 on med_MEDAGE10.company_name = c.name

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
		AVG(t.MEDAGE_FY) as med_MEDAGE_FY
	from
	(
		select
			d.company_name,
			d.MEDAGE_FY,
			ROW_NUMBER() over( partition by company_name order by d.MEDAGE_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MEDAGE_FY on med_MEDAGE_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.SCRIPT_ANU) as med_SCRIPT_ANU
	from
	(
		select
			d.company_name,
			d.SCRIPT_ANU,
			ROW_NUMBER() over( partition by company_name order by d.SCRIPT_ANU asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_SCRIPT_ANU on med_SCRIPT_ANU.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POPRATE_S) as med_POPRATE_S
	from
	(
		select
			d.company_name,
			d.POPRATE_S,
			ROW_NUMBER() over( partition by company_name order by d.POPRATE_S asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POPRATE_S on med_POPRATE_S.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.TR_POP_NAT) as med_TR_POP_NAT
	from
	(
		select
			d.company_name,
			d.TR_POP_NAT,
			ROW_NUMBER() over( partition by company_name order by d.TR_POP_NAT asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TR_POP_NAT on med_TR_POP_NAT.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.SCRIPT_A_1) as med_SCRIPT_A_1
	from
	(
		select
			d.company_name,
			d.SCRIPT_A_1,
			ROW_NUMBER() over( partition by company_name order by d.SCRIPT_A_1 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_SCRIPT_A_1 on med_SCRIPT_A_1.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HHRATE_S) as med_HHRATE_S
	from
	(
		select
			d.company_name,
			d.HHRATE_S,
			ROW_NUMBER() over( partition by company_name order by d.HHRATE_S asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HHRATE_S on med_HHRATE_S.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.TR_HH_NAT) as med_TR_HH_NAT
	from
	(
		select
			d.company_name,
			d.TR_HH_NAT,
			ROW_NUMBER() over( partition by company_name order by d.TR_HH_NAT asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TR_HH_NAT on med_TR_HH_NAT.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.SCRIPT_A_2) as med_SCRIPT_A_2
	from
	(
		select
			d.company_name,
			d.SCRIPT_A_2,
			ROW_NUMBER() over( partition by company_name order by d.SCRIPT_A_2 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_SCRIPT_A_2 on med_SCRIPT_A_2.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FAMRATE_S) as med_FAMRATE_S
	from
	(
		select
			d.company_name,
			d.FAMRATE_S,
			ROW_NUMBER() over( partition by company_name order by d.FAMRATE_S asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FAMRATE_S on med_FAMRATE_S.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.TR_FAM_NAT) as med_TR_FAM_NAT
	from
	(
		select
			d.company_name,
			d.TR_FAM_NAT,
			ROW_NUMBER() over( partition by company_name order by d.TR_FAM_NAT asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TR_FAM_NAT on med_TR_FAM_NAT.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.SCRIPT_AN1) as med_SCRIPT_AN1
	from
	(
		select
			d.company_name,
			d.SCRIPT_AN1,
			ROW_NUMBER() over( partition by company_name order by d.SCRIPT_AN1 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_SCRIPT_AN1 on med_SCRIPT_AN1.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OWNRATE_S) as med_OWNRATE_S
	from
	(
		select
			d.company_name,
			d.OWNRATE_S,
			ROW_NUMBER() over( partition by company_name order by d.OWNRATE_S asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OWNRATE_S on med_OWNRATE_S.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.TR_OWN_NAT) as med_TR_OWN_NAT
	from
	(
		select
			d.company_name,
			d.TR_OWN_NAT,
			ROW_NUMBER() over( partition by company_name order by d.TR_OWN_NAT asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TR_OWN_NAT on med_TR_OWN_NAT.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.SCRIPT_AN0) as med_SCRIPT_AN0
	from
	(
		select
			d.company_name,
			d.SCRIPT_AN0,
			ROW_NUMBER() over( partition by company_name order by d.SCRIPT_AN0 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_SCRIPT_AN0 on med_SCRIPT_AN0.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.INCRATE_S) as med_INCRATE_S
	from
	(
		select
			d.company_name,
			d.INCRATE_S,
			ROW_NUMBER() over( partition by company_name order by d.INCRATE_S asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_INCRATE_S on med_INCRATE_S.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.TR_MHI_NAT) as med_TR_MHI_NAT
	from
	(
		select
			d.company_name,
			d.TR_MHI_NAT,
			ROW_NUMBER() over( partition by company_name order by d.TR_MHI_NAT asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_TR_MHI_NAT on med_TR_MHI_NAT.company_name = c.name

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
		AVG(t.HINC0_CY_P) as med_HINC0_CY_P
	from
	(
		select
			d.company_name,
			d.HINC0_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC0_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC0_CY_P on med_HINC0_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC0_FY) as med_HINC0_FY
	from
	(
		select
			d.company_name,
			d.HINC0_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC0_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC0_FY on med_HINC0_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC0_FY_P) as med_HINC0_FY_P
	from
	(
		select
			d.company_name,
			d.HINC0_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC0_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC0_FY_P on med_HINC0_FY_P.company_name = c.name

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
		AVG(t.HINC15_CY_P) as med_HINC15_CY_P
	from
	(
		select
			d.company_name,
			d.HINC15_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC15_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC15_CY_P on med_HINC15_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC15_FY) as med_HINC15_FY
	from
	(
		select
			d.company_name,
			d.HINC15_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC15_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC15_FY on med_HINC15_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC15_FY_P) as med_HINC15_FY_P
	from
	(
		select
			d.company_name,
			d.HINC15_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC15_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC15_FY_P on med_HINC15_FY_P.company_name = c.name

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
		AVG(t.HINC25_CY_P) as med_HINC25_CY_P
	from
	(
		select
			d.company_name,
			d.HINC25_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC25_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC25_CY_P on med_HINC25_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC25_FY) as med_HINC25_FY
	from
	(
		select
			d.company_name,
			d.HINC25_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC25_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC25_FY on med_HINC25_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC25_FY_P) as med_HINC25_FY_P
	from
	(
		select
			d.company_name,
			d.HINC25_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC25_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC25_FY_P on med_HINC25_FY_P.company_name = c.name

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
		AVG(t.HINC35_CY_P) as med_HINC35_CY_P
	from
	(
		select
			d.company_name,
			d.HINC35_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC35_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC35_CY_P on med_HINC35_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC35_FY) as med_HINC35_FY
	from
	(
		select
			d.company_name,
			d.HINC35_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC35_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC35_FY on med_HINC35_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC35_FY_P) as med_HINC35_FY_P
	from
	(
		select
			d.company_name,
			d.HINC35_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC35_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC35_FY_P on med_HINC35_FY_P.company_name = c.name

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
		AVG(t.HINC50_CY_P) as med_HINC50_CY_P
	from
	(
		select
			d.company_name,
			d.HINC50_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC50_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC50_CY_P on med_HINC50_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC50_FY) as med_HINC50_FY
	from
	(
		select
			d.company_name,
			d.HINC50_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC50_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC50_FY on med_HINC50_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC50_FY_P) as med_HINC50_FY_P
	from
	(
		select
			d.company_name,
			d.HINC50_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC50_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC50_FY_P on med_HINC50_FY_P.company_name = c.name

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
		AVG(t.HINC75_CY_P) as med_HINC75_CY_P
	from
	(
		select
			d.company_name,
			d.HINC75_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC75_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC75_CY_P on med_HINC75_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC75_FY) as med_HINC75_FY
	from
	(
		select
			d.company_name,
			d.HINC75_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC75_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC75_FY on med_HINC75_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC75_FY_P) as med_HINC75_FY_P
	from
	(
		select
			d.company_name,
			d.HINC75_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC75_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC75_FY_P on med_HINC75_FY_P.company_name = c.name

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
		AVG(t.HINC100_CY_P) as med_HINC100_CY_P
	from
	(
		select
			d.company_name,
			d.HINC100_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC100_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC100_CY_P on med_HINC100_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC100_FY) as med_HINC100_FY
	from
	(
		select
			d.company_name,
			d.HINC100_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC100_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC100_FY on med_HINC100_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC100_FY_P) as med_HINC100_FY_P
	from
	(
		select
			d.company_name,
			d.HINC100_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC100_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC100_FY_P on med_HINC100_FY_P.company_name = c.name

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
		AVG(t.HINC150_CY_P) as med_HINC150_CY_P
	from
	(
		select
			d.company_name,
			d.HINC150_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC150_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC150_CY_P on med_HINC150_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC150_FY) as med_HINC150_FY
	from
	(
		select
			d.company_name,
			d.HINC150_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC150_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC150_FY on med_HINC150_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC150_FY_P) as med_HINC150_FY_P
	from
	(
		select
			d.company_name,
			d.HINC150_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC150_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC150_FY_P on med_HINC150_FY_P.company_name = c.name

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
		AVG(t.HINC200_CY_P) as med_HINC200_CY_P
	from
	(
		select
			d.company_name,
			d.HINC200_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC200_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC200_CY_P on med_HINC200_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC200_FY) as med_HINC200_FY
	from
	(
		select
			d.company_name,
			d.HINC200_FY,
			ROW_NUMBER() over( partition by company_name order by d.HINC200_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC200_FY on med_HINC200_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HINC200_FY_P) as med_HINC200_FY_P
	from
	(
		select
			d.company_name,
			d.HINC200_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.HINC200_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HINC200_FY_P on med_HINC200_FY_P.company_name = c.name

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
		AVG(t.MEDHINC_FY) as med_MEDHINC_FY
	from
	(
		select
			d.company_name,
			d.MEDHINC_FY,
			ROW_NUMBER() over( partition by company_name order by d.MEDHINC_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MEDHINC_FY on med_MEDHINC_FY.company_name = c.name

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
		AVG(t.AVGHINC_FY) as med_AVGHINC_FY
	from
	(
		select
			d.company_name,
			d.AVGHINC_FY,
			ROW_NUMBER() over( partition by company_name order by d.AVGHINC_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AVGHINC_FY on med_AVGHINC_FY.company_name = c.name

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
		AVG(t.PCI_FY) as med_PCI_FY
	from
	(
		select
			d.company_name,
			d.PCI_FY,
			ROW_NUMBER() over( partition by company_name order by d.PCI_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_PCI_FY on med_PCI_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP0C10) as med_POP0C10
	from
	(
		select
			d.company_name,
			d.POP0C10,
			ROW_NUMBER() over( partition by company_name order by d.POP0C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP0C10 on med_POP0C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP0C10_P) as med_POP0C10_P
	from
	(
		select
			d.company_name,
			d.POP0C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP0C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP0C10_P on med_POP0C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP0_CY_P) as med_POP0_CY_P
	from
	(
		select
			d.company_name,
			d.POP0_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP0_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP0_CY_P on med_POP0_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP0_FY) as med_POP0_FY
	from
	(
		select
			d.company_name,
			d.POP0_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP0_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP0_FY on med_POP0_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP0_FY_P) as med_POP0_FY_P
	from
	(
		select
			d.company_name,
			d.POP0_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP0_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP0_FY_P on med_POP0_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5C10) as med_POP5C10
	from
	(
		select
			d.company_name,
			d.POP5C10,
			ROW_NUMBER() over( partition by company_name order by d.POP5C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5C10 on med_POP5C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5C10_P) as med_POP5C10_P
	from
	(
		select
			d.company_name,
			d.POP5C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP5C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5C10_P on med_POP5C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP5_CY_P) as med_POP5_CY_P
	from
	(
		select
			d.company_name,
			d.POP5_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP5_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5_CY_P on med_POP5_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5_FY) as med_POP5_FY
	from
	(
		select
			d.company_name,
			d.POP5_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP5_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5_FY on med_POP5_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5_FY_P) as med_POP5_FY_P
	from
	(
		select
			d.company_name,
			d.POP5_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP5_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5_FY_P on med_POP5_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP10C10) as med_POP10C10
	from
	(
		select
			d.company_name,
			d.POP10C10,
			ROW_NUMBER() over( partition by company_name order by d.POP10C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP10C10 on med_POP10C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP10C10_P) as med_POP10C10_P
	from
	(
		select
			d.company_name,
			d.POP10C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP10C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP10C10_P on med_POP10C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP10_CY_P) as med_POP10_CY_P
	from
	(
		select
			d.company_name,
			d.POP10_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP10_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP10_CY_P on med_POP10_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP10_FY) as med_POP10_FY
	from
	(
		select
			d.company_name,
			d.POP10_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP10_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP10_FY on med_POP10_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP10_FY_P) as med_POP10_FY_P
	from
	(
		select
			d.company_name,
			d.POP10_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP10_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP10_FY_P on med_POP10_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP15C10) as med_POP15C10
	from
	(
		select
			d.company_name,
			d.POP15C10,
			ROW_NUMBER() over( partition by company_name order by d.POP15C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP15C10 on med_POP15C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP15C10_P) as med_POP15C10_P
	from
	(
		select
			d.company_name,
			d.POP15C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP15C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP15C10_P on med_POP15C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP15_CY_P) as med_POP15_CY_P
	from
	(
		select
			d.company_name,
			d.POP15_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP15_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP15_CY_P on med_POP15_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP15_FY) as med_POP15_FY
	from
	(
		select
			d.company_name,
			d.POP15_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP15_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP15_FY on med_POP15_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP15_FY_P) as med_POP15_FY_P
	from
	(
		select
			d.company_name,
			d.POP15_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP15_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP15_FY_P on med_POP15_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP20C10) as med_POP20C10
	from
	(
		select
			d.company_name,
			d.POP20C10,
			ROW_NUMBER() over( partition by company_name order by d.POP20C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP20C10 on med_POP20C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP20C10_P) as med_POP20C10_P
	from
	(
		select
			d.company_name,
			d.POP20C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP20C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP20C10_P on med_POP20C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP20_CY_P) as med_POP20_CY_P
	from
	(
		select
			d.company_name,
			d.POP20_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP20_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP20_CY_P on med_POP20_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP20_FY) as med_POP20_FY
	from
	(
		select
			d.company_name,
			d.POP20_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP20_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP20_FY on med_POP20_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP20_FY_P) as med_POP20_FY_P
	from
	(
		select
			d.company_name,
			d.POP20_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP20_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP20_FY_P on med_POP20_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP2534C10) as med_POP2534C10
	from
	(
		select
			d.company_name,
			d.POP2534C10,
			ROW_NUMBER() over( partition by company_name order by d.POP2534C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP2534C10 on med_POP2534C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP2534C10_P) as med_POP2534C10_P
	from
	(
		select
			d.company_name,
			d.POP2534C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP2534C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP2534C10_P on med_POP2534C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP2534_CY_P) as med_POP2534_CY_P
	from
	(
		select
			d.company_name,
			d.POP2534_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP2534_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP2534_CY_P on med_POP2534_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP2534_FY) as med_POP2534_FY
	from
	(
		select
			d.company_name,
			d.POP2534_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP2534_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP2534_FY on med_POP2534_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP2534_FY_P) as med_POP2534_FY_P
	from
	(
		select
			d.company_name,
			d.POP2534_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP2534_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP2534_FY_P on med_POP2534_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP3544C10) as med_POP3544C10
	from
	(
		select
			d.company_name,
			d.POP3544C10,
			ROW_NUMBER() over( partition by company_name order by d.POP3544C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP3544C10 on med_POP3544C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP3544C10_P) as med_POP3544C10_P
	from
	(
		select
			d.company_name,
			d.POP3544C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP3544C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP3544C10_P on med_POP3544C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP3544_CY_P) as med_POP3544_CY_P
	from
	(
		select
			d.company_name,
			d.POP3544_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP3544_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP3544_CY_P on med_POP3544_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP3544_FY) as med_POP3544_FY
	from
	(
		select
			d.company_name,
			d.POP3544_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP3544_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP3544_FY on med_POP3544_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP3544_FY_P) as med_POP3544_FY_P
	from
	(
		select
			d.company_name,
			d.POP3544_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP3544_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP3544_FY_P on med_POP3544_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP4554C10) as med_POP4554C10
	from
	(
		select
			d.company_name,
			d.POP4554C10,
			ROW_NUMBER() over( partition by company_name order by d.POP4554C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP4554C10 on med_POP4554C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP4554C10_P) as med_POP4554C10_P
	from
	(
		select
			d.company_name,
			d.POP4554C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP4554C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP4554C10_P on med_POP4554C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP4554_CY_P) as med_POP4554_CY_P
	from
	(
		select
			d.company_name,
			d.POP4554_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP4554_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP4554_CY_P on med_POP4554_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP4554_FY) as med_POP4554_FY
	from
	(
		select
			d.company_name,
			d.POP4554_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP4554_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP4554_FY on med_POP4554_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP4554_FY_P) as med_POP4554_FY_P
	from
	(
		select
			d.company_name,
			d.POP4554_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP4554_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP4554_FY_P on med_POP4554_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5564C10) as med_POP5564C10
	from
	(
		select
			d.company_name,
			d.POP5564C10,
			ROW_NUMBER() over( partition by company_name order by d.POP5564C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5564C10 on med_POP5564C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5564C10_P) as med_POP5564C10_P
	from
	(
		select
			d.company_name,
			d.POP5564C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP5564C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5564C10_P on med_POP5564C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP5564_CY_P) as med_POP5564_CY_P
	from
	(
		select
			d.company_name,
			d.POP5564_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP5564_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5564_CY_P on med_POP5564_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5564_FY) as med_POP5564_FY
	from
	(
		select
			d.company_name,
			d.POP5564_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP5564_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5564_FY on med_POP5564_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP5564_FY_P) as med_POP5564_FY_P
	from
	(
		select
			d.company_name,
			d.POP5564_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP5564_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP5564_FY_P on med_POP5564_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP6574C10) as med_POP6574C10
	from
	(
		select
			d.company_name,
			d.POP6574C10,
			ROW_NUMBER() over( partition by company_name order by d.POP6574C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP6574C10 on med_POP6574C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP6574C10_P) as med_POP6574C10_P
	from
	(
		select
			d.company_name,
			d.POP6574C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP6574C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP6574C10_P on med_POP6574C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP6574_CY_P) as med_POP6574_CY_P
	from
	(
		select
			d.company_name,
			d.POP6574_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP6574_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP6574_CY_P on med_POP6574_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP6574_FY) as med_POP6574_FY
	from
	(
		select
			d.company_name,
			d.POP6574_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP6574_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP6574_FY on med_POP6574_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP6574_FY_P) as med_POP6574_FY_P
	from
	(
		select
			d.company_name,
			d.POP6574_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP6574_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP6574_FY_P on med_POP6574_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP7584C10) as med_POP7584C10
	from
	(
		select
			d.company_name,
			d.POP7584C10,
			ROW_NUMBER() over( partition by company_name order by d.POP7584C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP7584C10 on med_POP7584C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP7584C10_P) as med_POP7584C10_P
	from
	(
		select
			d.company_name,
			d.POP7584C10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP7584C10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP7584C10_P on med_POP7584C10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP7584_CY_P) as med_POP7584_CY_P
	from
	(
		select
			d.company_name,
			d.POP7584_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP7584_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP7584_CY_P on med_POP7584_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP7584_FY) as med_POP7584_FY
	from
	(
		select
			d.company_name,
			d.POP7584_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP7584_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP7584_FY on med_POP7584_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP7584_FY_P) as med_POP7584_FY_P
	from
	(
		select
			d.company_name,
			d.POP7584_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP7584_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP7584_FY_P on med_POP7584_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP85C10) as med_POP85C10
	from
	(
		select
			d.company_name,
			d.POP85C10,
			ROW_NUMBER() over( partition by company_name order by d.POP85C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP85C10 on med_POP85C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP85PC10_P) as med_POP85PC10_P
	from
	(
		select
			d.company_name,
			d.POP85PC10_P,
			ROW_NUMBER() over( partition by company_name order by d.POP85PC10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP85PC10_P on med_POP85PC10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.POP85P_CY_P) as med_POP85P_CY_P
	from
	(
		select
			d.company_name,
			d.POP85P_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP85P_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP85P_CY_P on med_POP85P_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP85_FY) as med_POP85_FY
	from
	(
		select
			d.company_name,
			d.POP85_FY,
			ROW_NUMBER() over( partition by company_name order by d.POP85_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP85_FY on med_POP85_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POP85P_FY_P) as med_POP85P_FY_P
	from
	(
		select
			d.company_name,
			d.POP85P_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.POP85P_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POP85P_FY_P on med_POP85P_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.WHITE10) as med_WHITE10
	from
	(
		select
			d.company_name,
			d.WHITE10,
			ROW_NUMBER() over( partition by company_name order by d.WHITE10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_WHITE10 on med_WHITE10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.WHITE10_P) as med_WHITE10_P
	from
	(
		select
			d.company_name,
			d.WHITE10_P,
			ROW_NUMBER() over( partition by company_name order by d.WHITE10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_WHITE10_P on med_WHITE10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.WHITE_CY_P) as med_WHITE_CY_P
	from
	(
		select
			d.company_name,
			d.WHITE_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.WHITE_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_WHITE_CY_P on med_WHITE_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.WHITE_FY) as med_WHITE_FY
	from
	(
		select
			d.company_name,
			d.WHITE_FY,
			ROW_NUMBER() over( partition by company_name order by d.WHITE_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_WHITE_FY on med_WHITE_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.WHITE_FY_P) as med_WHITE_FY_P
	from
	(
		select
			d.company_name,
			d.WHITE_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.WHITE_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_WHITE_FY_P on med_WHITE_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.BLACK10) as med_BLACK10
	from
	(
		select
			d.company_name,
			d.BLACK10,
			ROW_NUMBER() over( partition by company_name order by d.BLACK10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_BLACK10 on med_BLACK10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.BLACK10_P) as med_BLACK10_P
	from
	(
		select
			d.company_name,
			d.BLACK10_P,
			ROW_NUMBER() over( partition by company_name order by d.BLACK10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_BLACK10_P on med_BLACK10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.BLACK_CY_P) as med_BLACK_CY_P
	from
	(
		select
			d.company_name,
			d.BLACK_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.BLACK_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_BLACK_CY_P on med_BLACK_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.BLACK_FY) as med_BLACK_FY
	from
	(
		select
			d.company_name,
			d.BLACK_FY,
			ROW_NUMBER() over( partition by company_name order by d.BLACK_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_BLACK_FY on med_BLACK_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.BLACK_FY_P) as med_BLACK_FY_P
	from
	(
		select
			d.company_name,
			d.BLACK_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.BLACK_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_BLACK_FY_P on med_BLACK_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AMERIND10) as med_AMERIND10
	from
	(
		select
			d.company_name,
			d.AMERIND10,
			ROW_NUMBER() over( partition by company_name order by d.AMERIND10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AMERIND10 on med_AMERIND10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AMERIND10_P) as med_AMERIND10_P
	from
	(
		select
			d.company_name,
			d.AMERIND10_P,
			ROW_NUMBER() over( partition by company_name order by d.AMERIND10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AMERIND10_P on med_AMERIND10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.AMERIND_CY_P) as med_AMERIND_CY_P
	from
	(
		select
			d.company_name,
			d.AMERIND_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.AMERIND_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AMERIND_CY_P on med_AMERIND_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AMERIND_FY) as med_AMERIND_FY
	from
	(
		select
			d.company_name,
			d.AMERIND_FY,
			ROW_NUMBER() over( partition by company_name order by d.AMERIND_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AMERIND_FY on med_AMERIND_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.AMERIND_FY_P) as med_AMERIND_FY_P
	from
	(
		select
			d.company_name,
			d.AMERIND_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.AMERIND_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_AMERIND_FY_P on med_AMERIND_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ASIAN10) as med_ASIAN10
	from
	(
		select
			d.company_name,
			d.ASIAN10,
			ROW_NUMBER() over( partition by company_name order by d.ASIAN10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ASIAN10 on med_ASIAN10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ASIAN10_P) as med_ASIAN10_P
	from
	(
		select
			d.company_name,
			d.ASIAN10_P,
			ROW_NUMBER() over( partition by company_name order by d.ASIAN10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ASIAN10_P on med_ASIAN10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.ASIAN_CY_P) as med_ASIAN_CY_P
	from
	(
		select
			d.company_name,
			d.ASIAN_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.ASIAN_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ASIAN_CY_P on med_ASIAN_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ASIAN_FY) as med_ASIAN_FY
	from
	(
		select
			d.company_name,
			d.ASIAN_FY,
			ROW_NUMBER() over( partition by company_name order by d.ASIAN_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ASIAN_FY on med_ASIAN_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.ASIAN_FY_P) as med_ASIAN_FY_P
	from
	(
		select
			d.company_name,
			d.ASIAN_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.ASIAN_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_ASIAN_FY_P on med_ASIAN_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.PACIFIC10) as med_PACIFIC10
	from
	(
		select
			d.company_name,
			d.PACIFIC10,
			ROW_NUMBER() over( partition by company_name order by d.PACIFIC10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_PACIFIC10 on med_PACIFIC10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.PACIFIC10_P) as med_PACIFIC10_P
	from
	(
		select
			d.company_name,
			d.PACIFIC10_P,
			ROW_NUMBER() over( partition by company_name order by d.PACIFIC10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_PACIFIC10_P on med_PACIFIC10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.PACIFIC_CY_P) as med_PACIFIC_CY_P
	from
	(
		select
			d.company_name,
			d.PACIFIC_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.PACIFIC_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_PACIFIC_CY_P on med_PACIFIC_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.PACIFIC_FY) as med_PACIFIC_FY
	from
	(
		select
			d.company_name,
			d.PACIFIC_FY,
			ROW_NUMBER() over( partition by company_name order by d.PACIFIC_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_PACIFIC_FY on med_PACIFIC_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.PACIFIC_FY_P) as med_PACIFIC_FY_P
	from
	(
		select
			d.company_name,
			d.PACIFIC_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.PACIFIC_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_PACIFIC_FY_P on med_PACIFIC_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OTHRACE10) as med_OTHRACE10
	from
	(
		select
			d.company_name,
			d.OTHRACE10,
			ROW_NUMBER() over( partition by company_name order by d.OTHRACE10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OTHRACE10 on med_OTHRACE10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OTHRACE10_P) as med_OTHRACE10_P
	from
	(
		select
			d.company_name,
			d.OTHRACE10_P,
			ROW_NUMBER() over( partition by company_name order by d.OTHRACE10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OTHRACE10_P on med_OTHRACE10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.OTHRACE_CY_P) as med_OTHRACE_CY_P
	from
	(
		select
			d.company_name,
			d.OTHRACE_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.OTHRACE_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OTHRACE_CY_P on med_OTHRACE_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OTHRACE_FY) as med_OTHRACE_FY
	from
	(
		select
			d.company_name,
			d.OTHRACE_FY,
			ROW_NUMBER() over( partition by company_name order by d.OTHRACE_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OTHRACE_FY on med_OTHRACE_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OTHRACE_FY_P) as med_OTHRACE_FY_P
	from
	(
		select
			d.company_name,
			d.OTHRACE_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.OTHRACE_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OTHRACE_FY_P on med_OTHRACE_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.RACE2UP10) as med_RACE2UP10
	from
	(
		select
			d.company_name,
			d.RACE2UP10,
			ROW_NUMBER() over( partition by company_name order by d.RACE2UP10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RACE2UP10 on med_RACE2UP10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.RACE2UP10_P) as med_RACE2UP10_P
	from
	(
		select
			d.company_name,
			d.RACE2UP10_P,
			ROW_NUMBER() over( partition by company_name order by d.RACE2UP10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RACE2UP10_P on med_RACE2UP10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.RACE2UP_CY_P) as med_RACE2UP_CY_P
	from
	(
		select
			d.company_name,
			d.RACE2UP_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.RACE2UP_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RACE2UP_CY_P on med_RACE2UP_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.RACE2UP_FY) as med_RACE2UP_FY
	from
	(
		select
			d.company_name,
			d.RACE2UP_FY,
			ROW_NUMBER() over( partition by company_name order by d.RACE2UP_FY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RACE2UP_FY on med_RACE2UP_FY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.RACE2UP_FY_P) as med_RACE2UP_FY_P
	from
	(
		select
			d.company_name,
			d.RACE2UP_FY_P,
			ROW_NUMBER() over( partition by company_name order by d.RACE2UP_FY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_RACE2UP_FY_P on med_RACE2UP_FY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HISPPOP10) as med_HISPPOP10
	from
	(
		select
			d.company_name,
			d.HISPPOP10,
			ROW_NUMBER() over( partition by company_name order by d.HISPPOP10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HISPPOP10 on med_HISPPOP10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HISPPOP10_P) as med_HISPPOP10_P
	from
	(
		select
			d.company_name,
			d.HISPPOP10_P,
			ROW_NUMBER() over( partition by company_name order by d.HISPPOP10_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HISPPOP10_P on med_HISPPOP10_P.company_name = c.name

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
		from demographics_denorm_10_mile d
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
		AVG(t.HISPPOP_CY_P) as med_HISPPOP_CY_P
	from
	(
		select
			d.company_name,
			d.HISPPOP_CY_P,
			ROW_NUMBER() over( partition by company_name order by d.HISPPOP_CY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HISPPOP_CY_P on med_HISPPOP_CY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HISPPOPFY) as med_HISPPOPFY
	from
	(
		select
			d.company_name,
			d.HISPPOPFY,
			ROW_NUMBER() over( partition by company_name order by d.HISPPOPFY asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HISPPOPFY on med_HISPPOPFY.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HISPPOPFY_P) as med_HISPPOPFY_P
	from
	(
		select
			d.company_name,
			d.HISPPOPFY_P,
			ROW_NUMBER() over( partition by company_name order by d.HISPPOPFY_P asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HISPPOPFY_P on med_HISPPOPFY_P.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.POPRATE) as med_POPRATE
	from
	(
		select
			d.company_name,
			d.POPRATE,
			ROW_NUMBER() over( partition by company_name order by d.POPRATE asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_POPRATE on med_POPRATE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.HHRATE) as med_HHRATE
	from
	(
		select
			d.company_name,
			d.HHRATE,
			ROW_NUMBER() over( partition by company_name order by d.HHRATE asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_HHRATE on med_HHRATE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FAMRATE) as med_FAMRATE
	from
	(
		select
			d.company_name,
			d.FAMRATE,
			ROW_NUMBER() over( partition by company_name order by d.FAMRATE asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FAMRATE on med_FAMRATE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.OWNRATE) as med_OWNRATE
	from
	(
		select
			d.company_name,
			d.OWNRATE,
			ROW_NUMBER() over( partition by company_name order by d.OWNRATE asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_OWNRATE on med_OWNRATE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.INCRATE) as med_INCRATE
	from
	(
		select
			d.company_name,
			d.INCRATE,
			ROW_NUMBER() over( partition by company_name order by d.INCRATE asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_INCRATE on med_INCRATE.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE0C10) as med_MALE0C10
	from
	(
		select
			d.company_name,
			d.MALE0C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE0C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE0C10 on med_MALE0C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE5C10) as med_MALE5C10
	from
	(
		select
			d.company_name,
			d.MALE5C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE5C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE5C10 on med_MALE5C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE10C10) as med_MALE10C10
	from
	(
		select
			d.company_name,
			d.MALE10C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE10C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE10C10 on med_MALE10C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE15C10) as med_MALE15C10
	from
	(
		select
			d.company_name,
			d.MALE15C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE15C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE15C10 on med_MALE15C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE20C10) as med_MALE20C10
	from
	(
		select
			d.company_name,
			d.MALE20C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE20C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE20C10 on med_MALE20C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE25C10) as med_MALE25C10
	from
	(
		select
			d.company_name,
			d.MALE25C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE25C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE25C10 on med_MALE25C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE30C10) as med_MALE30C10
	from
	(
		select
			d.company_name,
			d.MALE30C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE30C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE30C10 on med_MALE30C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE35C10) as med_MALE35C10
	from
	(
		select
			d.company_name,
			d.MALE35C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE35C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE35C10 on med_MALE35C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE40C10) as med_MALE40C10
	from
	(
		select
			d.company_name,
			d.MALE40C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE40C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE40C10 on med_MALE40C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE45C10) as med_MALE45C10
	from
	(
		select
			d.company_name,
			d.MALE45C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE45C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE45C10 on med_MALE45C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE50C10) as med_MALE50C10
	from
	(
		select
			d.company_name,
			d.MALE50C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE50C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE50C10 on med_MALE50C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE55C10) as med_MALE55C10
	from
	(
		select
			d.company_name,
			d.MALE55C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE55C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE55C10 on med_MALE55C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE60C10) as med_MALE60C10
	from
	(
		select
			d.company_name,
			d.MALE60C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE60C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE60C10 on med_MALE60C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE65C10) as med_MALE65C10
	from
	(
		select
			d.company_name,
			d.MALE65C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE65C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE65C10 on med_MALE65C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE70C10) as med_MALE70C10
	from
	(
		select
			d.company_name,
			d.MALE70C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE70C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE70C10 on med_MALE70C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE75C10) as med_MALE75C10
	from
	(
		select
			d.company_name,
			d.MALE75C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE75C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE75C10 on med_MALE75C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE80C10) as med_MALE80C10
	from
	(
		select
			d.company_name,
			d.MALE80C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE80C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE80C10 on med_MALE80C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MALE85C10) as med_MALE85C10
	from
	(
		select
			d.company_name,
			d.MALE85C10,
			ROW_NUMBER() over( partition by company_name order by d.MALE85C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MALE85C10 on med_MALE85C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MAL18UP10) as med_MAL18UP10
	from
	(
		select
			d.company_name,
			d.MAL18UP10,
			ROW_NUMBER() over( partition by company_name order by d.MAL18UP10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MAL18UP10 on med_MAL18UP10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MAL21UP10) as med_MAL21UP10
	from
	(
		select
			d.company_name,
			d.MAL21UP10,
			ROW_NUMBER() over( partition by company_name order by d.MAL21UP10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MAL21UP10 on med_MAL21UP10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MEDMAGE10) as med_MEDMAGE10
	from
	(
		select
			d.company_name,
			d.MEDMAGE10,
			ROW_NUMBER() over( partition by company_name order by d.MEDMAGE10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MEDMAGE10 on med_MEDMAGE10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM0C10) as med_FEM0C10
	from
	(
		select
			d.company_name,
			d.FEM0C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM0C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM0C10 on med_FEM0C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM5C10) as med_FEM5C10
	from
	(
		select
			d.company_name,
			d.FEM5C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM5C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM5C10 on med_FEM5C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM10C10) as med_FEM10C10
	from
	(
		select
			d.company_name,
			d.FEM10C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM10C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM10C10 on med_FEM10C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM15C10) as med_FEM15C10
	from
	(
		select
			d.company_name,
			d.FEM15C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM15C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM15C10 on med_FEM15C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM20C10) as med_FEM20C10
	from
	(
		select
			d.company_name,
			d.FEM20C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM20C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM20C10 on med_FEM20C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM25C10) as med_FEM25C10
	from
	(
		select
			d.company_name,
			d.FEM25C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM25C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM25C10 on med_FEM25C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM30C10) as med_FEM30C10
	from
	(
		select
			d.company_name,
			d.FEM30C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM30C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM30C10 on med_FEM30C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM35C10) as med_FEM35C10
	from
	(
		select
			d.company_name,
			d.FEM35C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM35C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM35C10 on med_FEM35C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM40C10) as med_FEM40C10
	from
	(
		select
			d.company_name,
			d.FEM40C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM40C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM40C10 on med_FEM40C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM45C10) as med_FEM45C10
	from
	(
		select
			d.company_name,
			d.FEM45C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM45C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM45C10 on med_FEM45C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM50C10) as med_FEM50C10
	from
	(
		select
			d.company_name,
			d.FEM50C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM50C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM50C10 on med_FEM50C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM55C10) as med_FEM55C10
	from
	(
		select
			d.company_name,
			d.FEM55C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM55C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM55C10 on med_FEM55C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM60C10) as med_FEM60C10
	from
	(
		select
			d.company_name,
			d.FEM60C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM60C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM60C10 on med_FEM60C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM65C10) as med_FEM65C10
	from
	(
		select
			d.company_name,
			d.FEM65C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM65C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM65C10 on med_FEM65C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM70C10) as med_FEM70C10
	from
	(
		select
			d.company_name,
			d.FEM70C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM70C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM70C10 on med_FEM70C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM75C10) as med_FEM75C10
	from
	(
		select
			d.company_name,
			d.FEM75C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM75C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM75C10 on med_FEM75C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM80C10) as med_FEM80C10
	from
	(
		select
			d.company_name,
			d.FEM80C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM80C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM80C10 on med_FEM80C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM85C10) as med_FEM85C10
	from
	(
		select
			d.company_name,
			d.FEM85C10,
			ROW_NUMBER() over( partition by company_name order by d.FEM85C10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM85C10 on med_FEM85C10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM18UP10) as med_FEM18UP10
	from
	(
		select
			d.company_name,
			d.FEM18UP10,
			ROW_NUMBER() over( partition by company_name order by d.FEM18UP10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM18UP10 on med_FEM18UP10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.FEM21UP10) as med_FEM21UP10
	from
	(
		select
			d.company_name,
			d.FEM21UP10,
			ROW_NUMBER() over( partition by company_name order by d.FEM21UP10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_FEM21UP10 on med_FEM21UP10.company_name = c.name

left join
(
	select
		t.company_name,
		AVG(t.MEDFAGE10) as med_MEDFAGE10
	from
	(
		select
			d.company_name,
			d.MEDFAGE10,
			ROW_NUMBER() over( partition by company_name order by d.MEDFAGE10 asc) as row_num,
			count(*) over (partition by company_name) as count
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_MEDFAGE10 on med_MEDFAGE10.company_name = c.name

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
		from demographics_denorm_10_mile d
		-- join on comps to filter by period
		inner join @comps c on c.store_id = d.store_id and c.period = @period
	) t
	where row_num in (count/2+1, (count+1)/2)
	group by company_name
) med_agg_income on med_agg_income.company_name = c.name

order by c.name



