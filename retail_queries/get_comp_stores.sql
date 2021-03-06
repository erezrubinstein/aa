create procedure CompetitorReportBasic_prc 
  @company_id1 int
  , @company_id2 int
  , @driving_time int = 10
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
	c.name as home_company_name
	, a.street_number as home_street_number
	, a.street as home_street
	, a.municipality as home_municipality
	, a.governing_district as home_governing_district
	, c2.name as away_copmpany_name 
	, s2.note as away_store_note
	, a2.street_number as away_street_number 
	, a2.street as away_street
	, a2.municipality as away_municipality
	, a2.governing_district as away_governing_district
	, cm.driving_time 
	, ISNULL((
		select count(*) as competitors
		from competition_instances ci2
		inner join stores ss on ss.company_id = @company_id2 and ci2.away_store_id = ss.id
		where ci2.home_store_id = ci.away_store_id
		group by ci2.home_store_id
	,0)) as competitor_count
	, ISNULL(
		select count(*) as competitors from competition_instances ci3
		inner join competition_measurements cm2 on cm2.competition_instance_id = ci3.id
		inner join stores ss on ss.company_id = @company_id2 and ci3.away_store_id = ss.id
		where ci3.home_store_id = ci.away_store_id and cm2.driving_time > 0 and cm2.driving_time <= @driving_time
		group by ci3.home_store_id
	,0)) as competitor_count_within_driving_time
	, dp.population
	--jsternberg 2012-09-25:
	--opulation_men_age_15_34 is kind of an arbitrary population demographic segment to pull here
	--this comes from the original report (JOSB vs MW) in Sept 2012.
	--To make this more generic, we may want to have a few more "basic" population segments defined
	--Or better, create a mapping between company industries and "significant" demo segments
	--, and pull the most significant segment here...
	, (
		select sum(dpsv.value) from demographic_profile_segment_values dpsv
		inner join demographic_profiles dp on dpsv.demographic_profile_id = dp.id
		inner join trade_areas ta on dp.trade_area_id = ta.id
		inner join stores ss on ss.company_id = @company_id2 and ta.store_id = ss.id
		where ta.store_id = ci.away_store_id
		and dpsv.demographic_segment_id in (4,5,6,7) and dpsv.demographic_measurement_type = 'population'
	) as population_men_age_15_34
	, dp.aggregate_income
into #r --throw this into a temp table so we can do per-competitor stats next 
from companies c
inner join stores s on s.company_id = c.id
inner join addresses a on a.store_id = s.id
inner join competition_instances ci on ci.home_store_id = s.store_id
inner join stores s2 on s2.id = ci.away_store_id
inner join addresses a2 on a2.store_id = s2.id
inner join companies c2 on c2.id = a2.company_id
inner join competition_measurements cm on cm.competition_instance_id = ci.id
inner join trade_areas ta on ta.store_id = ci.away_store_id
inner join demographic_profiles dp on dp.trade_area_id = ta.id
where c.id = @company_id1 
	and c2.id = @company_id2
	and s.company_id = @company_id1 --over-constrain to help indexes
	and s2.company_id = @company_id2 --over-constrain to help indexes
;

--return all of the data, plus columns that divide out stats by competitors in range
select *
	, competitor_count + 1 as competitor_count_other_company
	, competitor_count_within_driving_time + 1 as competitor_count_in_range_other_company
	, population / (competitor_count_within_driving_time + 1) as population_per_competitor_in_range
	, population_men_age_15_34 / (competitor_count_within_driving_time + 1) as population_men_age_15_34_per_competitor_in_range
	, aggregate_income / (competitor_count_within_driving_time + 1) as aggregate_income_per_competitor_in_range
from #r
order by home_company_name, home_governing_district, home_municipality, home_street_number, home_street
;
