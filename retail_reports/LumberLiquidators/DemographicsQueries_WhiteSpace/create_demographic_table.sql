use LL_OCT13_CMA_100213
go

declare @dis table (name varchar(1000) primary key)
insert into @dis
SELECT 'TOTPOP_CY' UNION ALL
SELECT 'TOTHH_CY' UNION ALL
SELECT 'PCI_CY' UNION ALL
SELECT 'HINC_50KPLUS_CY' UNION ALL
SELECT 'HINC_75KPLUS_CY' UNION ALL
SELECT 'AGG_INCOME' UNION ALL
SELECT 'ACSUNT1DET' UNION ALL
SELECT 'ACSUNT1ATT' UNION ALL
SELECT 'ACSUNT2' UNION ALL
SELECT 'ACSUNT3' UNION ALL
SELECT 'ACSUNT5' UNION ALL
SELECT 'ACSUNT10' UNION ALL
SELECT 'ACSUNT20' UNION ALL
SELECT 'ACSUNT50UP' UNION ALL
SELECT 'ACSUNTMOB' UNION ALL
SELECT 'ACSUNTOTH' UNION ALL
SELECT 'ACSBLT2005' UNION ALL
SELECT 'ACSBLT2000' UNION ALL
SELECT 'ACSBLT1990' UNION ALL
SELECT 'ACSBLT1980' UNION ALL
SELECT 'ACSBLT1970' UNION ALL
SELECT 'ACSBLT1960' UNION ALL
SELECT 'ACSBLT1950' UNION ALL
SELECT 'ACSBLT1940' UNION ALL
SELECT 'ACSBLT1939' UNION ALL
SELECT 'ACSOMV2005' UNION ALL
SELECT 'ACSOMV2000' UNION ALL
SELECT 'ACSOMV1990' UNION ALL
SELECT 'ACSOMV1980' UNION ALL
SELECT 'ACSOMV1970' UNION ALL
SELECT 'ACSOMV1969' UNION ALL
SELECT 'X3025_X' UNION ALL
SELECT 'TOTHU_CY' UNION ALL
SELECT 'OWNER_CY' UNION ALL
SELECT 'RENTER_CY' UNION ALL
SELECT 'VACANT_CY'

select *,
	case	
		when dems.count > 17577 then 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + ' and dn_' + dems.name + '.template_name = ''cosmetics_sep13'''
		else 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + '' 
	end as join_sql,
	'dn_' + dems.name + '.value as ' + dems.name + ',' as select_sql,
	dems.name + ' [decimal](19, 5) NULL,' as create_table_sql,
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