use ULTA_OCT13_20MSQWHSPC_100213
go

select distinct threshold_id from trade_areas

select *,
	dems.name + ',' as insert_value,
	'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + '' as join_sql,
	'dn_' + dems.name + '.value as ' + dems.name + ',' as select_sql,
	dems.name + ' [decimal](19, 5) NULL,' as create_table_sql
from
(
	select 
		d.data_item_id, 
		di.name, 
		count(*) as count
	from demographic_numvalues d
	inner join data_items di on di.data_item_id = d.data_item_id
	where d.data_item_id > 13
	group by d.data_item_id, di.name
) dems
order by dems.data_item_id


/*
select template_name, count(distinct trade_area_id)
from demographic_numvalues 
group by template_name
*/

/*
select distinct di.name 
from demographic_numvalues d
inner join data_items di on di.data_item_id = d.data_item_id
where d.template_name = 'acs_housing'
*/

/*
select dn.data_item_id, di.name, di.description, count(*)
from demographic_numvalues dn
inner join data_items di on di.data_item_id = dn.data_item_id
group by dn.data_item_id, di.name, di.description
order by count(*) asc
*/

/*
select distinct template_name 
from demographic_numvalues 
where data_item_id = 152
*/


/*
select distinct d.template_name 
from demographic_numvalues d
inner join data_items di on di.data_item_id = d.data_item_id
where di.name = 'TRIGGER5'

TRIGGER5	TRIGGER5	34095
MOETOTPOP	MOE Total Population	34704
ACSTOTHU	ACS Total Housing Units	34704
MOETOTHH	MOE Total Households	34704
MOETOTHU	MOE Total Housing Units	34704
ACSTOTHH	ACS Total Households	34704
*/



--select count(*) from trade_areas where threshold_id <> 4