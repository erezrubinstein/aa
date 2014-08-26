use SCSS_10MSQWHSPC_091316
go

declare @dis table (name varchar(1000) primary key)
insert into @dis
SELECT 'TOTPOP_CY' UNION ALL
SELECT 'TOTHH_CY' UNION ALL
SELECT 'MEDAGE_CY' UNION ALL
SELECT 'HINC0_CY' UNION ALL
SELECT 'HINC15_CY' UNION ALL
SELECT 'HINC25_CY' UNION ALL
SELECT 'HINC35_CY' UNION ALL
SELECT 'HINC50_CY' UNION ALL
SELECT 'HINC75_CY' UNION ALL
SELECT 'HINC100_CY' UNION ALL
SELECT 'HINC150_CY' UNION ALL
SELECT 'HINC200_CY' UNION ALL
SELECT 'PCI_CY' UNION ALL
SELECT 'POP0_CY' UNION ALL
SELECT 'POP5_CY' UNION ALL
SELECT 'POP10_CY' UNION ALL
SELECT 'POP15_CY' UNION ALL
SELECT 'POP20_CY' UNION ALL
SELECT 'POP2534_CY' UNION ALL
SELECT 'POP3544_CY' UNION ALL
SELECT 'POP4554_CY' UNION ALL
SELECT 'POP5564_CY' UNION ALL
SELECT 'POP6574_CY' UNION ALL
SELECT 'POP7584_CY' UNION ALL
SELECT 'POP85_CY' UNION ALL
SELECT 'WHITE_CY' UNION ALL
SELECT 'BLACK_CY' UNION ALL
SELECT 'AMERIND_CY' UNION ALL
SELECT 'ASIAN_CY' UNION ALL
SELECT 'PACIFIC_CY' UNION ALL
SELECT 'OTHRACE_CY' UNION ALL
SELECT 'RACE2UP_CY' UNION ALL
SELECT 'HISPPOPCY' UNION ALL
SELECT 'HINC_50KPLUS_CY' UNION ALL
SELECT 'HINC_75KPLUS_CY' UNION ALL
SELECT 'HINC_100KPLUS' UNION ALL
SELECT 'POP_25PLUS_CY' UNION ALL
SELECT 'POP_30PLUS_CY' UNION ALL
SELECT 'AGG_INCOME' UNION ALL
SELECT 'X4048_X' UNION ALL
SELECT 'ACSA25I50' UNION ALL
SELECT 'ACSA25I60' UNION ALL
SELECT 'ACSA25I75' UNION ALL
SELECT 'ACSA25I100' UNION ALL
SELECT 'ACSA25I125' UNION ALL
SELECT 'ACSA25I150' UNION ALL
SELECT 'ACSA25I200' UNION ALL
SELECT 'ACSA45I50' UNION ALL
SELECT 'ACSA45I60' UNION ALL
SELECT 'ACSA45I75' UNION ALL
SELECT 'ACSA45I100' UNION ALL
SELECT 'ACSA45I125' UNION ALL
SELECT 'ACSA45I150' UNION ALL
SELECT 'ACSA45I200' UNION ALL
SELECT 'ACSA65I50' UNION ALL
SELECT 'ACSA65I60' UNION ALL
SELECT 'ACSA65I75' UNION ALL
SELECT 'ACSA65I100' UNION ALL
SELECT 'ACSA65I125' UNION ALL
SELECT 'ACSA65I150' UNION ALL
SELECT 'ACSA65I200'

select *,
	case	
		when dems.count > 71039 then 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + ' and dn_' + dems.name + '.template_name = ''Mattress_June13'''
		else 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + '' 
	end as join_sql,
	'dn_' + dems.name + '.value as ' + dems.name + ',' as select_sql,
	dems.name + ' [decimal](19, 9) NULL,' as create_table_sql,
	dems.name + ',' as select_value,
	dems.count
from @dis names
left join
(
	select 
		d.data_item_id, 
		di.name, 
		count(*) as count
	from demographic_numvalues d
	inner join data_items di on di.data_item_id = d.data_item_id
	where di.data_item_id > 10
	group by d.data_item_id, di.name
) dems on dems.name = names.name
where names.name is not null
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