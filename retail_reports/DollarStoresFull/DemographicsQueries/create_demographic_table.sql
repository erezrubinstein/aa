use DOLLFULL_JUN13_CMA_062313
go

select *,
	case	
		when dems.count > 54882 then 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + ' and dn_' + dems.name + '.template_name = ''DollarStores_APR13'''
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
where dems.data_item_id in (13, 16, 31, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 98, 104, 110, 116, 122, 128, 134, 140, 146, 152, 158, 164, 170, 176, 182, 188, 194, 200, 206, 1466, 1469, 1472, 1475, 1478, 1481, 1484, 1487, 1490, 1493, 1496, 1499, 1502, 1529, 1532, 1535, 1538, 1541, 1544, 1547, 1550, 1553, 1556, 1559, 1562, 1565, 2435, 2443, 2451, 2469, 2559, 2646, 2661, 2728, 2729, 2730, 2731, 2732, 2733)
order by dems.data_item_id


/*
select distinct
template_name
from demographic_numvalues 
*/

/*
select data_item_id, count(*)
from demographic_numvalues
group by data_item_id
order by count(*) asc
*/

/*
select distinct template_name 
from demographic_numvalues 
where data_item_id = 13
*/

--select count(*) from trade_areas where threshold_id <> 4