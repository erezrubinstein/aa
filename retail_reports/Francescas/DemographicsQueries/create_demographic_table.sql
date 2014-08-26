use FRAN_JUN13_CMA_062113
go

select *,
	case	
		when dems.count > 435 then 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + ' and dn_' + dems.name + '.template_name = ''FRAN_JUN13'''
		else 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + '' 
	end as join_sql,
	'dn_' + dems.name + '.value as ' + dems.name + ',' as select_sql,
	dems.name + ' [decimal](19, 4) NULL,' as create_table_sql,
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
where dems.data_item_id in (13, 16, 31, 48, 52, 56, 60, 64, 68, 72, 76, 80, 88, 92, 98, 104, 110, 116, 122, 128, 134, 140, 146, 152, 158, 164, 170, 176, 182, 188, 194, 200, 206, 653, 660, 667, 674, 681, 688, 695, 702, 709, 716, 723, 730, 737, 744, 751, 758, 765, 772, 779, 786, 793, 800, 807, 814, 821, 828, 835, 842, 849, 856, 1334, 2443, 2457, 2798, 2805, 2806, 2807, 2808, 2809, 2810, 2812, 2813)
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
where data_item_id = 1620
*/

--select count(*) from trade_areas where threshold_id <> 4

--select * from data_items where name in ('TOTPOP_CY', 'TOTHH_CY', 'MEDAGE_CY', 'HINC0_CY', 'HINC15_CY', 'HINC25_CY', 'HINC35_CY', 'HINC50_CY', 'HINC75_CY', 'HINC100_CY', 'HINC150_CY', 'HINC200_CY', 'PCI_CY', 'POP0_CY', 'POP5_CY', 'POP10_CY', 'POP15_CY', 'POP20_CY', 'POP2534_CY', 'POP3544_CY', 'POP4554_CY', 'POP5564_CY', 'POP6574_CY', 'POP7584_CY', 'POP85_CY', 'WHITE_CY', 'BLACK_CY', 'AMERIND_CY', 'ASIAN_CY', 'PACIFIC_CY', 'OTHRACE_CY', 'RACE2UP_CY', 'HISPPOPCY', 'HINC_50KPLUS_CY', 'HINC_75KPLUS_CY', 'HINC_100KPLUS', 'POP_25PLUS_CY', 'POP_30PLUS_CY', 'AGG_INCOME', 'FEMALE_18TO34', 'X5015_X', 'X5077_X', 'PROX_WAPP_JEW', 'COUNT_1', 'COUNT_2', 'COUNT_3', 'COUNT_4', 'COUNT_5', 'COUNT_6', 'COUNT_7', 'COUNT_8', 'COUNT_9', 'COUNT_10', 'COUNT_11', 'COUNT_12', 'COUNT_13', 'COUNT_14', 'COUNT_15', 'COUNT_16', 'COUNT_17', 'COUNT_18', 'COUNT_19', 'COUNT_20', 'COUNT_21', 'COUNT_22', 'COUNT_23', 'COUNT_24', 'COUNT_25', 'COUNT_26', 'COUNT_27', 'COUNT_28', 'COUNT_29', 'COUNT_30', 'ACSOCCBASE')