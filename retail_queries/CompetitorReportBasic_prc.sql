USE [retaildb_dev]
GO
/****** Object:  StoredProcedure [dbo].[CompetitorReportBasic_prc]    Script Date: 09/26/2012 18:30:49 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER procedure [dbo].[CompetitorReportBasic_prc] 
  @company_id1 int
  , @company_id2 int
  , @driving_time int = 10
  , @home_governing_district nvarchar(255) = null
  , @debug_away_store_id int = null
as

--jsternberg2012-09-25
--Gets competitive stores for the two given companies.
--Restricts to competitive relationships where the drive time between stores is less than the supplied @driving_time param.
--Also gets store address data and selected demographic data for stores from company_id2 (the "affected" store)
--Notes:
--1. Is the limit on driving_time > 0 necessary?
--2. men age 15-34 probably doesn't work as the best population segment for all situations. See comment inline.
--3. Do we want any other columns to make this a bit more robust?

select 
	s.id as home_store_id
	, c.name as home_company_name
	, a.street_number as home_street_number
	, a.street as home_street
	, a.municipality as home_municipality
	, a.governing_district as home_governing_district
	, s2.id as away_store_id
	, c2.name as away_company_name
	, s2.note as away_store_note
	, a2.street_number as away_street_number
	, a2.street as away_street
	, a2.municipality as away_municipality
	, a2.governing_district as away_governing_district
	, cm.driving_time 
	--away store based fields:
	, ISNULL(
	  (
		select count(*)
		from competition_instances ci2
		inner join stores ss2 on ss2.id = ci2.away_store_id and ss2.company_id = @company_id1
		where ci2.home_store_id = ci.away_store_id
		group by ci2.home_store_id
	  )
	  ,0
	) as away_store_competitor_count
	, ISNULL(
	  (
		select count(*) 
		from competition_instances ci3
		inner join competition_measurements cm3 on cm3.competition_instance_id = ci3.id
		inner join stores ss3 on ss3.id = ci3.away_store_id and ss3.company_id = @company_id1
		where ci3.home_store_id = ci.away_store_id and cm3.driving_time > 0 and cm3.driving_time <= @driving_time
		group by ci3.home_store_id
      )
      ,0
    ) as away_store_competitor_count_in_range
	, dp.population as away_store_population
	--jsternberg 2012-09-25:
	--population_men_age_15_34 is kind of an arbitrary population demographic segment to pull here
	--this comes from the original report (JOSB vs MW) in Sept 2012.
	--To make this more generic, we may want to have a few more "basic" population segments defined
	--Or better, create a mapping between company industries and "significant" demo segments
	--, and pull the most significant segment here...
	, (
		select sum(dpsv.value) 
		from demographic_profile_segment_values dpsv
		inner join demographic_profiles dp on dp.id = dpsv.demographic_profile_id
		inner join trade_areas ta on ta.id = dp.trade_area_id
		inner join stores ss on ss.id = ta.store_id and ss.company_id = @company_id2
		where ta.store_id = ci.away_store_id
		and dpsv.demographic_segment_id in (4,5,6,7) and dpsv.demographic_measurement_type = 'population'
	) as away_store_population_men_age_15_34
	, dp.aggregate_income as away_store_aggregate_income
	--home store based fields:
	, ISNULL(
	  (
		select count(*)
		from competition_instances ci2
		inner join stores ss2 on ss2.id = ci2.away_store_id and ss2.company_id = @company_id2
		where ci2.home_store_id = ci.home_store_id
		group by ci2.home_store_id
	  )
	  ,0
	) as home_store_competitor_count
	, ISNULL(
		(
		select count(*)
		from competition_instances ci4
		inner join competition_measurements cm4 on cm4.competition_instance_id = ci4.id
		inner join stores ss4 on ss4.id = ci4.away_store_id and ss4.company_id = @company_id2
		where ci4.home_store_id = ci.home_store_id 
			and cm4.driving_time > 0 and cm4.driving_time <= @driving_time
		group by ci4.home_store_id
        )
        ,0
    ) as home_store_competitor_count_in_range
	, dp2.population as home_store_population
	, (
		select sum(dpsv.value) 
		from demographic_profile_segment_values dpsv
		inner join demographic_profiles dp on dpsv.demographic_profile_id = dp.id
		inner join trade_areas ta on dp.trade_area_id = ta.id
		inner join stores ss on ss.company_id = @company_id1 and ta.store_id = ss.id
		where ta.store_id = ci.home_store_id
		and dpsv.demographic_segment_id in (4,5,6,7) and dpsv.demographic_measurement_type = 'population'
	) as home_store_population_men_age_15_34
	, dp2.aggregate_income as home_store_aggregate_income
into #r --throw this into a temp table so we can do per-competitor stats next 
from companies c
inner join stores s on s.company_id = c.id
inner join addresses a on a.store_id = s.id
inner join competition_instances ci on ci.home_store_id = s.id
inner join stores s2 on s2.id = ci.away_store_id
inner join addresses a2 on a2.store_id = s2.id
inner join companies c2 on c2.id = s2.company_id
inner join competition_measurements cm on cm.competition_instance_id = ci.id
inner join trade_areas ta on ta.store_id = ci.away_store_id
inner join demographic_profiles dp on dp.trade_area_id = ta.id
inner join trade_areas ta2 on ta2.store_id = ci.home_store_id
inner join demographic_profiles dp2 on dp2.trade_area_id = ta2.id
where c.id = @company_id1 
	and c2.id = @company_id2
	and s.company_id = @company_id1 --over-constrain to help indexes
	and s2.company_id = @company_id2 --over-constrain to help indexes
	and a.governing_district = ISNULL(@home_governing_district, a.governing_district)
	and s2.id = ISNULL(@debug_away_store_id, s2.id)
	and exists (select 1 from AdHoc_JOSB_MW ah where ah.store_id = s.id)
;

--return all of the data, plus columns that divide out stats by competitors in range
select *
	, away_store_competitor_count + 1 as away_store_total_competitive_stores --i.e, including the anchor store
	, away_store_competitor_count_in_range + 1 as away_store_total_competitive_stores_in_range
	, away_store_population / (away_store_competitor_count_in_range + 1) as away_store_population_per_competitor_in_range
	, away_store_population_men_age_15_34 / (away_store_competitor_count_in_range + 1) as away_store_population_men_age_15_34_per_competitor_in_range
	, away_store_aggregate_income / (away_store_competitor_count_in_range + 1) as away_store_aggregate_income_per_competitor_in_range
	, home_store_competitor_count + 1 as home_store_total_competitive_stores --i.e, including the anchor store
	, home_store_competitor_count_in_range + 1 as home_store_total_competitive_stores_in_range
	, home_store_population / (home_store_competitor_count_in_range + 1) as home_store_population_per_competitor_in_range
	, home_store_population_men_age_15_34 / (home_store_competitor_count_in_range + 1) as home_store_population_men_age_15_34_per_competitor_in_range
	, home_store_aggregate_income / (home_store_competitor_count_in_range + 1) as home_store_aggregate_income_per_competitor_in_range
from #r
order by home_company_name, home_governing_district, home_municipality, home_street_number, home_street
;
