
--select data
declare @companies table(id int primary key)
insert into @companies
select company_id from companies where name like '%UNITTEST%'

declare @sectors table(id int primary key)
insert into @sectors
select id from sectors where name like '%UNITTEST%'

declare @stores table (id int primary key)
insert into @stores
select store_id from stores where company_id in (select id from @companies)

declare @addresses table (id int primary key)
insert into @addresses
select address_id from stores where store_id in (select id from @stores)
UNION
select address_id from addresses where street like '%UNITTEST%'

declare @address_history table (id int primary key)
insert into @address_history
select address_id from addresses where street like '%UNITTEST%'

declare @competitive_companies table (id int primary key)
insert into @competitive_companies
select competitive_company_id from competitive_companies c where c.away_company_id in (select id from @companies)

declare @segments table(id int primary key)
insert into @segments
select demographic_segment_id from demographic_segments where minimum_age = 400

declare @dataitems table(id int primary key)
insert into @dataitems
select data_item_id from data_items d where d.name like 'unittest%'

declare @tradeareas table(id int primary key)
insert into @tradeareas
select trade_area_id from trade_areas where store_id in (select id from @stores)

declare @source_files table(id int primary key)
insert into @source_files
select f.source_file_id from source_files f where f.full_path like '%UNITTEST%'

delete from zip_establishment_details where zip_code = '11111';
delete from zip_codes where zip_code = '11111';

--delete data
delete from stores_change_log where source_file_id in (select id from @source_files)
delete from source_file_records where source_file_id in (select id from @source_files)
delete from source_files where source_file_id in (select id from @source_files)
delete from monopolies where store_id in (select id from @stores)
delete from competitive_companies where competitive_company_id in (select id from @competitive_companies)
delete from competitive_stores where home_store_id in (select id from @stores)
delete from demographic_numvalues where trade_area_id in (select id from @tradeareas)
delete from demographic_strvalues where trade_area_id in (select id from @tradeareas)
delete from trade_area_shapes where trade_area_id in (select id from @tradeareas)
delete from trade_area_overlaps where home_trade_area_id in (select id from @tradeareas)
delete from trade_area_overlaps where away_trade_area_id in (select id from @tradeareas)
delete from trade_area_analytics where trade_area_id in (select id from @tradeareas)
delete from competitive_stores_postgis where trade_area_id in (select id from @tradeareas)
delete from monopolies_postgis where trade_area_id in (select id from @tradeareas)
delete from trade_areas where trade_area_id in (select id from @tradeareas)
delete from addresses_history where addresses_history_id in (select id from @address_history)
delete from stores where store_id in (select id from @stores)
delete from addresses where address_id in (select id from @addresses)
delete from companies_sectors where company_id in (select id from @companies)
delete from sectors where id in (select id from @sectors)
delete from companies where company_id in (select id from @companies)
delete from demographic_numvalues where segment_id in (select id from @segments)
delete from demographic_segments where demographic_segment_id in (select id from @segments)
delete from data_items where data_item_id in (select id from @dataitems)
delete from periods where duration_type_id = 1 and period_start_date = '20000101' and period_end_date='20900101'
delete from periods where duration_type_id = 1 and period_start_date='57660101'