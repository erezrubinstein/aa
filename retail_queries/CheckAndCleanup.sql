select count(*) as companies from companies with (nolock) --14
select count(*) as stores from stores with (nolock) --32507
select count(*) as competitions from competitions with (nolock) --182

--demographic load
select count(*) as trade_areas from trade_areas with (nolock) --303
select count(*) as demographic_profiles from demographic_profiles with (nolock) --303

--proximity load
select count(*) as competition_instances from competition_instances with (nolock) --12989
select count(*) as competition_measurements from competition_measurements with (nolock) --12989
select s.company_id, count(*) as count_competition_instances
from competition_instances ci with (nolock)
inner join stores s with (nolock) on s.id = ci.home_store_id 
group by s.company_id
-- company_id	count_competition_instances
-- ----------	---------------------------
-- 1				12989

--age by sex load
select count(*) as demographic_profile_segment_values from demographic_profile_segment_values with (nolock) --10908


--cleanup after arcpy, redo ruby part 2
--truncate table competition_instances
--truncate table trade_areas
--truncate table demographic_profiles
--truncate table competition_measurements



--set identity_insert demographic_segments on

--insert into demographic_segments (id, minimum_age, maximum_age, gender, created_at, updated_at)
--select id, minimum_age, maximum_age, gender, created_at, updated_at
--from retaildb_dev.dbo.demographic_segments

--set identity_insert demographic_segments off
