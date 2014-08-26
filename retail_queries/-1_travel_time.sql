select * from competitive_stores 
where travel_time < 0
and home_store_id = 2370 and away_store_id = 76;

select * from companies where company_id in (15,20);

select * from stores where store_id in (2370, 76);
select * from addresses where address_id in (2367, 92);

select count(*) from competitive_stores where travel_time = -1 --5599
select count(*) from competitive_stores where travel_time > -1 --76755

select 5599.0 / 76755.0 --0.07294638



select cs.*
from competitive_stores cs 
inner join stores s with (nolock) on s.store_id = cs.home_store_id
inner join addresses_vw a with (nolock) on a.address_id = s.address_id
inner join stores s2 with (nolock) on s2.store_id = cs.away_store_id
inner join addresses_vw a2 with (nolock) on a.address_id = s.address_id
where cs.travel_time = -1 --5599




with busts as (
	select distinct 
		NTILE(10) over (order by trig_distance_miles) as tile
		,[trig_distance_miles]
		,[latitude]
		,[longitude]
		,[away_latitude]
		,[away_longitude]
		,[company_id]
		,[company_name]
		,[store_id]
		,[fulladdress]
		,[fulladdress_normalized]
		,[opened_date]
		,[closed_date]
		,[assumed_opened_date]
		,[assumed_closed_date]
		,[away_store_id]
		,[away_company_id]
		,[away_company_name]
		,[away_fulladdress]
		,[away_opened_date]
		,[away_closed_date]
		,[away_assumed_opened_date]
		,[away_assumed_closed_date]
		,[competitive_store_id]
		,[competition_start_date]
		,[competition_end_date]
		,[competition_travel_time]
	from [retaildb_timeseries_dev].[dbo].[qa_report_new_vw]
	where competition_travel_time = -1
)
select tile, count(*) cnt, min(trig_distance_miles) as min_trig_distance_miles, max(trig_distance_miles) as max_trig_distance_miles
from busts
group by tile
order by tile
; 
--5599 rows


select distinct 
		NTILE(10) over (order by trig_distance_miles) as tile
		,[trig_distance_miles]
		,[latitude]
		,[longitude]
		,[away_latitude]
		,[away_longitude]
		,[competition_travel_time]
		,[company_id]
		,[company_name]
		,[store_id]
		,[fulladdress]
		,[fulladdress_normalized]
		,[opened_date]
		,[closed_date]
		,[assumed_opened_date]
		,[assumed_closed_date]
		,[away_store_id]
		,[away_company_id]
		,[away_company_name]
		,[away_fulladdress]
		,[away_opened_date]
		,[away_closed_date]
		,[away_assumed_opened_date]
		,[away_assumed_closed_date]
		,[competitive_store_id]
		,[competition_start_date]
		,[competition_end_date]
from [retaildb_timeseries_dev].[dbo].[qa_report_new_vw]
where competition_travel_time = -1
order by [trig_distance_miles] desc




create view busted_home_vw as
select distinct 
		[store_id]
		, street_number
		, street
		, municipality
		, governing_district
		, postal_area
		,[longitude]
		,[latitude]
from [retaildb_timeseries_dev].[dbo].[qa_report_new_vw]
where competition_travel_time = -1;	

GO	

create view busted_away_vw as
select distinct 
		[away_store_id]
		, away_street_number
		, away_street
		, away_municipality
		, away_governing_district
		, away_postal_area
		,[away_longitude]
		,[away_latitude]
from [retaildb_timeseries_dev].[dbo].[qa_report_new_vw]
where competition_travel_time = -1;
GO	






select distinct 
		[latitude]
		,[longitude]
		,[away_latitude]
		,[away_longitude]
		,[competition_travel_time]
		,[company_id]
		,[company_name]
		,[store_id]
		,[fulladdress]
		,[away_store_id]
		,[away_company_id]
		,[away_company_name]
		,[away_fulladdress]
from [qa_report_new_vw] 
where store_id = 76
order by longitude;	



select distinct 
		[latitude]
		,[longitude]
		,[away_latitude]
		,[away_longitude]
		,[competition_travel_time]
		,[company_id]
		,[company_name]
		,[store_id]
		,[fulladdress]
		,[away_store_id]
		,[away_company_id]
		,[away_company_name]
		,[away_fulladdress]
from [qa_report_new_vw] 
where store_id = 2370
order by longitude;	

