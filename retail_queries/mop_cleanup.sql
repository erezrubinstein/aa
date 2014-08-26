select * from retail_demographic_values_vw where store_id = 55730
select * from retail_demographic_values_vw where store_id = 50644

select * from retail_demographic_values_vw where store_id = 41118
select * from qa_report_new_vw where latitude between 47 and 48 and longitude between -69 and -68


select * from qa_report_new_vw where latitude between 30 and 31 and longitude between -78 and -77



--Shape:
--Point:
--X: -77.38192765635148 
--Y: 35.52468858329712 
--Score: 73.0 
--Address: 657 WORTHINGTON RD, WINTERVILLE, NC, 28590 


--corrected:
--35.525102,
---77.383032

select * from addresses where store_id = 42016
-- wrong geocodes: 
	-- latitude		longitude
	-- 30.508769	-77.383031
-- right geocodes:
	-- latitude		longitude
	-- 35.525102	-77.383032
	

select * from retaildb_test_june2011.dbo.addresses
where street_number = 4040 
and street = 'Market Street Northeast'
and municipality = 'Salem'
and governing_district = 'OR'
and postal_area = 97301

select * from stores where id = 101395
select * from trade_areas where store_id = 101395
select * from retail_demographic_basic_stats_vw where trade_area_id = 12150

37.2903925
select * from addresses where latitude between 37.29 and 37.30 order by latitude
select * from addresses where latitude between 37 and 38



use retaildb_test_june2011_moptest
select * from stores where id in (101395,116093)
select * from trade_areas where store_id in (101395,116093)
select * from retail_demographic_basic_stats_vw where trade_area_id in (6746,12150)
select * from retail_demographic_basic_stats_vw where population < 10




use retaildb_test_june2011
select * from stores where id in (101395,116093)
select * from trade_areas where store_id in (101395,116093)
select * from retail_demographic_basic_stats_vw where trade_area_id in (6746,12150)
select * from retail_demographic_basic_stats_vw where population < 10
