use retaildb_timeseries_dollar_stores
go

declare @thresold_id int = 5 -- 5 mile
--declare @thresold_id int = 8 -- 3 mile

declare @companies table (company_id int primary key)
insert into @companies
select 69 UNION ALL
select 74 UNION ALL
select 70 UNION ALL
select 72


declare @competitions table (store_id int)
insert into @competitions
select distinct store_id 
from stores 
where company_id in (select company_id from @companies)
	--and assumed_closed_date is null
	and assumed_opened_date > '19000101'
	
	
insert into @competitions
select cs.away_store_id
from competitive_stores cs
inner join trade_areas t on t.trade_area_id = cs.trade_area_id
inner join stores home_s on home_s.store_id = cs.home_store_id
inner join stores away_s on away_s.store_id = cs.away_store_id
where t.threshold_id = @thresold_id
	--and home_s.assumed_closed_date is null
	--and away_s.assumed_closed_date is null
	and home_s.assumed_opened_date > '19000101'
	--and cs.end_date is null
	and home_s.company_id in (select company_id from @companies)
	and away_s.company_id in (select company_id from @companies)
	
select count(distinct store_id) 
from @competitions

--233338
--select count(*) from stores where assumed_closed_date is null and company_id in  (select company_id from @companies)