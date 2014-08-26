select * from companies where name in ('lululemon athletica Authorized Dealers','LORNA JANE','Calvin Klein PERFORMANCE')
--select * from stores where company_id in (99,108) and assumed_opened_date < '2012-03-01' and isnull(assumed_closed_date,'3000-01-01') > '2012-03-01'
select * from competitive_companies where home_company_id in (101,105,108) and away_company_id in (101,105,108) order by home_company_id, assumed_start_date
--select * from thresholds

select * from entity_types

update entity_types set name = 'Competitive Store' where entity_type_id = 5
update entity_types set name = 'Period' where entity_type_id = 6
update entity_types set name = 'Source File' where entity_type_id = 7
update entity_types set name = 'Source File Record' where entity_type_id = 8

select count(*) from competitive_stores  --70164

select cs1.competitive_store_id as id
from competitive_stores cs1
inner join trade_areas t on t.trade_area_id = cs1.trade_area_id
inner join stores s on s.store_id = cs1.home_store_id
inner join companies c on c.company_id = s.company_id
where t.threshold_id <> 2 --drive time minutes
	and not exists (
		select 1 from competitive_stores cs2 
		inner join trade_areas t2 on t2.trade_area_id = cs2.trade_area_id
		where cs2.away_store_id = cs1.home_store_id 
			and cs2.home_store_id = cs1.away_store_id
			and t2.threshold_id = t.threshold_id --same threshold
			and t2.threshold_id <> 2 --drive time minutes
	)



select *
from competitive_stores cs1
inner join trade_areas t on t.trade_area_id = cs1.trade_area_id
inner join stores s on s.store_id = cs1.home_store_id
inner join companies c on c.company_id = s.company_id
where t.threshold_id <> 2 --drive time minutes
	and not exists (
		select 1 from competitive_stores cs2 
		inner join trade_areas t2 on t2.trade_area_id = cs2.trade_area_id
		where cs2.away_store_id = cs1.home_store_id 
			and cs2.home_store_id = cs1.away_store_id
			and t2.threshold_id <> 2 --drive time minutes
	)

select * from competitive_stores where home_store_id = 2414 and away_store_id = 954
select * from stores where stores and 
select * from competitive_stores where away_store_id = 2414 and home_store_id = 954


select * from entity_types 

select * from data_check_types

insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (43, 'non reflexive competitive companies', 5, 'select cs1.competitive_store_id as id
from competitive_stores cs1
inner join trade_areas t on t.trade_area_id = cs1.trade_area_id
inner join stores s on s.store_id = cs1.home_store_id
inner join companies c on c.company_id = s.company_id
where t.threshold_id <> 2 --drive time minutes
	and not exists (
		select 1 from competitive_stores cs2 
		inner join trade_areas t2 on t2.trade_area_id = cs2.trade_area_id
		where cs2.away_store_id = cs1.home_store_id 
			and cs2.home_store_id = cs1.away_store_id
			and t2.threshold_id = t.threshold_id --same threshold
			and t2.threshold_id <> 2 --drive time minutes);', 2, 0);




select * 
from retaildb_lululemon_v16.dbo.competitive_companies cc
where not exists (
	select * from retaildb_lululemon_v15.dbo.competitive_companies cc2
	where cc2.home_company_id = cc.home_company_id
		and cc2.away_company_id = cc.away_company_id
		)



select * from source_file_records order by 1 desc

select * from countries where code = 'USA'

select * from addresses