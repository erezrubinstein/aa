use retaildb_timeseries_dollar_stores
go

declare @thresold_id int = 5 -- 5 mile

declare @companies table (company_id int primary key)
insert into @companies
select 69 UNION ALL
select 74 UNION ALL
select 70 UNION ALL
select 72


--prior period
declare @demographics table(company varchar(100), store_id int, opened datetime, closed datetime, HINC0_CY float, HINC15_CY float, HINC25_CY float, HINC35_CY float,
							less_than_50K_HH float, competitions float)
insert into @demographics (company, store_id, opened, closed, HINC0_CY, HINC15_CY, HINC25_CY, HINC35_CY, less_than_50K_HH, competitions)
select 
	c.name, 
	s.store_id, 
	s.assumed_opened_date as opened, 
	s.assumed_closed_date as closed,
	d.HINC0_CY,
	d.HINC15_CY,
	d.HINC25_CY,
	d.HINC35_CY,
	d.less_than_50K_HH,
	comp.count
from stores s
inner join companies c on c.company_id = s.company_id
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @thresold_id
inner join demographics_denorm_5_mile d on d.trade_area_id = t.trade_area_id
cross apply
(
	select count(*) + 1 as count
	from competitive_stores cs
	inner join stores away on away.store_id = cs.away_store_id
	where away.company_id in (select company_id from @companies)
		and cs.home_store_id = s.store_id
		and cs.start_date = '19000101'
) comp
where s.company_id in (select company_id from @companies)
	and s.assumed_opened_date = '19000101'
	
	
	
select 
	d.company, 
	AVG(d.HINC0_CY / d.competitions) HINC0_CY, 
	AVG(d.HINC15_CY / d.competitions) HINC15_CY, 
	AVG(d.HINC25_CY / d.competitions) HINC25_CY,
	AVG(d.HINC35_CY / d.competitions) HINC35_CY,
	AVG(d.less_than_50K_HH / d.competitions) less_than_50K_HH
from @demographics d
group by d.company