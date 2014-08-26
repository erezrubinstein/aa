--gets counts of competitive store instances by date ranges
select c.name, convert(date, s.assumed_opened_date) as opened_date, cs.start_date, cs.end_date, convert(date, s.assumed_closed_date) as closed_date, count(*) cnt
from companies c 
inner join stores s on s.company_id = c.company_id
inner join competitive_stores cs on cs.home_store_id = s.store_id
inner join trade_areas t on t.store_id = s.store_id and t.trade_area_id = cs.trade_area_id
where t.threshold_id = 1
group by c.name,  s.assumed_opened_date, s.assumed_closed_date, cs.start_date, cs.end_date 
order by c.name,  s.assumed_opened_date, s.assumed_closed_date, cs.start_date, cs.end_date



--select sfr.note, a.address_id, a.fulladdress, a.longitude, a.latitude, sfr.source_file_record_id, sfr.source_file_id, sfr.street_number, sfr.street, sfr.city, sfr.state, sfr.zip, sfr.phone, sfr.longitude, sfr.latitude
select count(distinct sfr.source_file_record_id)
from addresses_vw a
inner join stores on stores.address_id = a.address_id
inner join source_file_records sfr on sfr.street_number = a.street_number and sfr.street = a.street
where stores.assumed_closed_date is not null 
	and not (sfr.note = 'Gap Outlet' or sfr.note ='Gap')
--order by sfr.note, sfr.source_file_id

select sfr.note, count(distinct sfr.source_file_record_id)
from addresses_vw a
inner join stores on stores.address_id = a.address_id
inner join source_file_records sfr on sfr.street_number = a.street_number and sfr.street = a.street
where stores.assumed_closed_date is not null 
	and not (sfr.note = 'Gap Outlet' or sfr.note ='Gap')
group by  sfr.note
order by  sfr.note

select * from addresses where address_id = 850








--changed long/lat > 0.1
--select * from addresses_change_log order by created_at desc

select substring(comment, patindex('%(''longitude''%', comment)+34, 1),
	case substring(comment, patindex('%(''longitude''%', comment)+34, 1)
		when '''' then substring(comment, patindex('%(''longitude''%', comment)+23, 11) -- longitude is 11 characters including negative sign and decimal point, eg: -118.604276
		when ')' then substring(comment, patindex('%(''longitude''%', comment)+23, 10) -- longitude is 10 characters including negative sign and decimal point, eg: -84.364642
		else NULL --not expected!
	end as parsed_old_longitude
	, substring(comment, patindex('%(''longitude''%', comment)+58, 1)
	, substring(comment, patindex('%(''longitude''%', comment)+59, 1)
	, substring(comment, patindex('%(''longitude''%', comment)+60, 1)
	, case substring(comment, patindex('%(''longitude''%', comment)+34, 1)
		when '''' then 
			case substring(comment, patindex('%(''longitude''%', comment)+58, 1)
				when '''' then substring(comment, patindex('%(''longitude''%', comment)+47, 11)
				when 
				else NULL
			end
	--, substring(comment, patindex('%(''longitude''%', comment)+46, 11) as parsed_new_longitude
	end as parsed_new_longitude
	, comment
from addresses_change_log 
where comment like '%long%'


--('longitude', Decimal('-84.364642'), Decimal('-84.363063'))


--drop table addresses_change_log_values

--create table addresses_change_log_values (
--	addresses_change_log_value_id int not null identity(1,1) constraint PK_addresses_change_log_values primary key clustered,
--	addresses_change_log_id int not null,
--	value_type varchar(250) not null,
--	from_value nvarchar(255) null,
--	to_value nvarchar(255) null,
--	created_at datetime not null constraint DF_addresses_change_log_values_created_at default (getutcdate()),
--	updated_at datetime not null constraint DF_addresses_change_log_values_updated_at default (getutcdate())
--)

--alter table addresses_change_log_values
--add constraint FK_addresses_change_log_values
--foreign key (addresses_change_log_id)
--references addresses_change_log (addresses_change_log_id);

--create nonclustered index IX_addresses_change_log_values_addresses_change_log_id on addresses_change_log_values (addresses_change_log_id);


--select value_type, count(*) from addresses_change_log_values group by value_type

select a.address_id, a.fulladdress, a.longitude, a.latitude
	, aclv.value_type, aclv.from_value, aclv.to_value
	, abs(cast(aclv.from_value as decimal(9,6)) - cast(aclv.to_value as decimal(9,6))) as diff
from addresses_vw a
inner join addresses_change_log acl on acl.address_id = a.address_id
inner join addresses_change_log_values aclv on aclv.addresses_change_log_id = acl.addresses_change_log_id
where aclv.value_type in ('longitude','latitude')
and abs(cast(aclv.from_value as decimal(9,6)) - cast(aclv.to_value as decimal(9,6))) > 0.1
order by diff desc

--select * from addresses




select a.address_id as id
from addresses a
inner join addresses_change_log acl on acl.address_id = a.address_id
inner join addresses_change_log_values aclv on aclv.addresses_change_log_id = acl.addresses_change_log_id
where aclv.value_type in ('longitude','latitude')
and abs(cast(aclv.from_value as decimal(9,6)) - cast(aclv.to_value as decimal(9,6))) > 0.1







--source file records that weren't processed

select sf.source_file_id
from source_files sf
inner join (
	select source_file_id, count(*) cnt
	from source_file_records
	group by source_file_id
) as source_record_counts on source_record_counts.source_file_id = sf.source_file_id 
left outer join (
	select source_file_id, count(*) cnt
	from stores_change_log 
	where change_type_id in (1, --opened
							2, --confirmed
							3) --updated
	group by source_file_id
) as scl_processed on scl_processed.source_file_id = source_record_counts.source_file_id
where coalesce(scl_processed.cnt,0) <> source_record_counts.cnt;


select sf.source_file_id
from source_files sf
inner join (
	select source_file_id, count(*) cnt
	from source_file_records
	group by source_file_id
) as source_record_counts on source_record_counts.source_file_id = sf.source_file_id 
left outer join (
	select source_file_id, count(*) cnt
	from addresses_change_log 
	where change_type_id in (1, --opened
							2, --confirmed
							3) --updated
	group by source_file_id
) as acl_processed on acl_processed.source_file_id = source_record_counts.source_file_id
where coalesce(acl_processed.cnt,0) <> source_record_counts.cnt;