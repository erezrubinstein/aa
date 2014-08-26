set xact_abort on

begin transaction

alter table data_checks
drop constraint FK_data_checks_data_check_types;

truncate table data_check_types;

-- insert the data check types
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (1, 'reverse geocoding (ESRI)',1, NULL, 2, 2);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (2, 'stores with neither competition relationships nor are flagged as monopolies', 2, 'select s1.store_id as id
from stores s1
where not exists (
		select 1 from competitive_stores cs where cs.home_store_id = s1.store_id
	)
	and not exists (
		select 1 from monopolies m where m.store_id = s1.store_id
	)', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (3, 'duplicate addresses', 1, 'with dupes as
(
select street_number, street, municipality, governing_district, postal_area, count(*) cnt
from addresses
group by street_number, street, municipality, governing_district, postal_area
having count(*) > 1)
select a.address_id as id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area, d.cnt 
from addresses a inner join dupes as d on 
a.street_number = d.street_number
and a.street = d.street
and a.municipality = d.municipality
and a.governing_district = d.governing_district
and a.postal_area = d.postal_area
;', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (4, 'stores with no basic demographic stats', 2, 'select s.store_id as id
from stores s
where not exists (select 1 from [retail_demographic_basic_stats_vw] b where b.store_id = s.store_id)', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (5, 'stores with NO demographic values', 2, 'select s.store_id as id
from stores s
inner join trade_areas t on t.store_id = s.store_id
where not exists (select 1 from demographic_numvalues nv where nv.trade_area_id = t.store_id)', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (6, 'stores with no trade areas', 2, 'select s.store_id as id
from stores s
where not exists (select 1 from trade_areas t where t.store_id = s.store_id)', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (7, 'stores with no address', 2, 'select store_id as id
from stores
where address_id is null', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (8, 'competitive_companies that point to missing home companies', 5, 'select cmp.competitive_company_id as id
from competitive_companies cmp
where not exists (select 1 from companies c where c.company_id = cmp.home_company_id)', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (9, 'competitive_companies that point to missing away companies', 5, 'select cmp.competitive_company_id as id
from competitive_companies cmp
where not exists (select 1 from companies c where c.company_id = cmp.away_company_id)', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (10, 'competitive_stores that point to missing home stores', 2, 'select cmp.away_store_id as id
from competitive_stores cmp
where not exists (select 1 from stores s where s.store_id = cmp.home_store_id)', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (11, 'competitive_stores that point to missing away stores', 2, 'select cmp.home_store_id as id
from competitive_stores cmp
where not exists (select 1 from stores s where s.store_id = cmp.away_store_id)', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (12, 'stores that have < 10 population (probably geocoded in the ocean)', 2, 
'select store_id as id from qa_report_demographics_vw where home_population < 10', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (13, 'addresses with leading/trailing spaces in the street', 1,
'select address_id as id from addresses where nullif(street, '''') is not null and (left(street,1) = '' '' or right(street,1) = '' '')', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (14, 'addresses with leading/trailing spaces in the municipality', 1,
'select address_id as id from addresses where nullif(municipality, '''') is not null and (left(municipality,1) = '' '' or right(municipality,1) = '' '')', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (15, 'addresses with leading/trailing spaces in the governing_district', 1,
'select address_id as id from addresses where nullif(governing_district, '''') is not null and (left(governing_district,1) = '' '' or right(governing_district,1) = '' '')', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (16, 'addresses with leading/trailing spaces in the postal_area', 1,
'select address_id as id from addresses where nullif(postal_area, '''') is not null and (LEFT(postal_area,1) = '' '' or right(postal_area,1) = '' '')', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (17, 'companies with leading/trailing spaces in the ticker', 3,
'select company_id as id from companies where nullif(ticker, '''') is not null and (LEFT(ticker,1) = '' '' or right(ticker,1) = '' '')', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (18, 'companies with leading/trailing spaces in the name', 3,
'select company_id as id from companies where nullif(name, '''') is not null and (LEFT(name,1) = '' '' or right(name,1) = '' '')', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (19, 'stores with leading/trailing spaces in the phone_number', 2,
'select store_id as id from stores where nullif(phone_number, '''') is not null and (LEFT(phone_number,1) = '' '' or right(phone_number,1) = '' '')', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (20, 'stores with leading/trailing spaces in the complex', 2,
'select store_id as id from stores where nullif(complex, '''') is not null and (LEFT(complex,1) = '' '' or right(complex,1) = '' '')', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (21, 'US addresses with less than 5 digit postal_areas', 1,
'select address_id as id from addresses where country_id = 840 and LEN(postal_area) < 5', 2, 0);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (22, 'reverse geocoding (Google)',1, NULL, 2, 2);
insert into data_check_types (data_check_type_id, name, entity_type_id, sql, severity_level, fail_threshold)
values (23, 'trade areas with duplicate demographic values', 4, 
'select t.trade_area_id as id from trade_areas t
left outer join (select trade_area_id, count(*) as cnt from retail_demographic_values_vw group by trade_area_id) as v
	on v.trade_area_id = t.trade_area_id
left outer join (select trade_area_id, count(*) as cnt from demographic_numvalues group by trade_area_id) as n
	on n.trade_area_id = t.trade_area_id
left outer join (select trade_area_id, count(*) as cnt from demographic_strvalues group by trade_area_id) as s
	on s.trade_area_id = t.trade_area_id
where coalesce(v.cnt, 0) <> coalesce(n.cnt, 0) + coalesce(s.cnt, 0);', 2, 0);


alter table dbo.data_checks
add constraint FK_data_checks_data_check_types
foreign key (data_check_type_id)
references data_check_types (data_check_type_id);

commit