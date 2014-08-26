use retaildb_timeseries_dollar_stores_white_space_10_mile
go

declare @threshold int = 1164

declare @companies table(company_id int primary key)
insert into @companies
select 2 UNION ALL --dollar general
select 3 UNION ALL -- fred's
select 5 UNION ALL -- family dollar
select 7 -- dollar tree

select 
	t.trade_area_id, 
	dn.less_than_50K_HH, 
	comp.count as comp_count,
	@threshold as threshold, 
	cast(dn.less_than_50K_HH / @threshold as int) as store_potential,
	(cast(dn.less_than_50K_HH / @threshold as int) - comp.count) as churn_potential
from trade_areas t
inner join demographics_denorm dn on dn.trade_area_id = t.trade_area_id
cross apply
(
	select count(*) as count
	from competitive_stores cs
	inner join stores away on away.store_id = cs.away_store_id
	where trade_area_id = t.trade_area_id
		and away.assumed_closed_date is null
		and away.company_id in (select company_id from @companies)
) comp
order by comp_count desc