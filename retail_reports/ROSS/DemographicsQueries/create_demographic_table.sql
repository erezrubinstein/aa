use retaildb_timeseries_ROSS
go

select *,
	case	
		when dems.count > 2463 then 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + ' and dn_' + dems.name + '.template_name = ''DollarStores_APR13'''
		else 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + '' 
	end as join_sql,
	'dn_' + dems.name + '.value as ' + dems.name + ',' as select_sql,
	dems.name + ' [decimal](19, 9) NULL,' as create_table_sql,
	dems.name + ',' as select_value,
	dems.count
from
(
	select 
		d.data_item_id, 
		di.name, 
		count(*) as count
	from demographic_numvalues d
	inner join data_items di on di.data_item_id = d.data_item_id
	where di.data_item_id > 10
	group by d.data_item_id, di.name
) dems
order by dems.data_item_id


--select distinct
--template_name
--from demographic_numvalues 



--select data_item_id, count(*)
--from demographic_numvalues 
--group by data_item_id 
--order by count(*) desc