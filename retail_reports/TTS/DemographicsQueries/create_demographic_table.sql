use TTS_AUG13_20MSQWHSPC_080413
go

select *,
	case 
		when dems.count > 17577 then 'left join demographic_numvalues dn_' + dems.name + ' on dn_' + dems.name + '.trade_area_id = t.trade_area_id and dn_' + dems.name + '.data_item_id = ' + cast(dems.data_item_id as varchar(6)) + ' and dn_' + dems.name + '.template_name = ''Mattress_June13'''  
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
where dems.data_item_id in (1631, 1634, 1667, 1670, 1637, 1673, 1640, 1676, 1643, 1646, 1649, 1652, 1655, 1658, 1661, 1664, 1688, 1691, 1724, 1727, 1694, 1730, 1697, 1733, 1700, 1703, 1706, 1709, 1712, 1715, 1718, 1721, 1745, 1748, 1781, 1784, 1751, 1787, 1754, 1790, 1757, 1760, 1763, 1766, 1769, 1772, 1775, 1778, 1802, 1805, 1838, 1841, 1808, 1844, 1811, 1847, 1814, 1817, 1820, 1823, 1826, 1829, 1832, 1835, 522, 519, 516, 513, 510, 507, 504, 501, 498, 1334, 546, 543, 540, 537, 534, 531, 564, 561, 558, 555, 552, 549, 480, 468, 465, 471, 483, 474, 477, 486, 489, 492, 2810, 176, 182, 170, 2887, 2807, 2805, 2806, 48, 72, 52, 76, 80, 56, 60, 64, 68, 206, 31, 194, 25, 188, 88, 2808, 2809, 92, 104, 110, 116, 122, 128, 134, 98, 140, 146, 152, 158, 200, 28, 16, 2846, 13, 2849, 164, 2607, 2878, 2879, 2880, 2881, 2874, 2875, 2876, 2619, 2622, 2628, 2869, 2870, 2871, 2872, 2873)
order by dems.data_item_id


/*
select distinct
template_name
from demographic_numvalues 
*/

/*
select data_item_id, count(distinct template_name), count(*)
from demographic_numvalues
where data_item_id in (1631, 1634, 1667, 1670, 1637, 1673, 1640, 1676, 1643, 1646, 1649, 1652, 1655, 1658, 1661, 1664, 1688, 1691, 1724, 1727, 1694, 1730, 1697, 1733, 1700, 1703, 1706, 1709, 1712, 1715, 1718, 1721, 1745, 1748, 1781, 1784, 1751, 1787, 1754, 1790, 1757, 1760, 1763, 1766, 1769, 1772, 1775, 1778, 1802, 1805, 1838, 1841, 1808, 1844, 1811, 1847, 1814, 1817, 1820, 1823, 1826, 1829, 1832, 1835, 522, 519, 516, 513, 510, 507, 504, 501, 498, 1334, 546, 543, 540, 537, 534, 531, 564, 561, 558, 555, 552, 549, 480, 468, 465, 471, 483, 474, 477, 486, 489, 492, 2810, 176, 182, 170, 2887, 2807, 2805, 2806, 48, 72, 52, 76, 80, 56, 60, 64, 68, 206, 31, 194, 25, 188, 88, 2808, 2809, 92, 104, 110, 116, 122, 128, 134, 98, 140, 146, 152, 158, 200, 28, 16, 2846, 13, 2849, 164, 2607, 2878, 2879, 2880, 2881, 2874, 2875, 2876, 2619, 2622, 2628, 2869, 2870, 2871, 2872, 2873)
group by data_item_id
order by count(*) desc
*/

/*
select distinct template_name 
from demographic_numvalues 
where data_item_id = 2809
*/

/*
select * from data_items where data_item_id = 569
*/

--select count(*) from trade_areas where threshold_id <> 4

--select * from data_items where name in ('TOTPOP_CY', 'TOTHH_CY', 'MEDAGE_CY', 'HINC0_CY', 'HINC15_CY', 'HINC25_CY', 'HINC35_CY', 'HINC50_CY', 'HINC75_CY', 'HINC100_CY', 'HINC150_CY', 'HINC200_CY', 'PCI_CY', 'POP0_CY', 'POP5_CY', 'POP10_CY', 'POP15_CY', 'POP20_CY', 'POP2534_CY', 'POP3544_CY', 'POP4554_CY', 'POP5564_CY', 'POP6574_CY', 'POP7584_CY', 'POP85_CY', 'WHITE_CY', 'BLACK_CY', 'AMERIND_CY', 'ASIAN_CY', 'PACIFIC_CY', 'OTHRACE_CY', 'RACE2UP_CY', 'HISPPOPCY', 'HINC_50KPLUS_CY', 'HINC_75KPLUS_CY', 'HINC_100KPLUS', 'POP_25PLUS_CY', 'POP_30PLUS_CY', 'AGG_INCOME', 'ACSOCCBASE', 'ACSA15I0', 'ACSA15I10', 'ACSA15I15', 'ACSA15I20', 'ACSA15I25', 'ACSA15I30', 'ACSA15I35', 'ACSA15I40', 'ACSA15I45', 'ACSA15I50', 'ACSA15I60', 'ACSA15I75', 'ACSA15I100', 'ACSA15I125', 'ACSA15I150', 'ACSA15I200', 'ACSA25I0', 'ACSA25I10', 'ACSA25I15', 'ACSA25I20', 'ACSA25I25', 'ACSA25I30', 'ACSA25I35', 'ACSA25I40', 'ACSA25I45', 'ACSA25I50', 'ACSA25I60', 'ACSA25I75', 'ACSA25I100', 'ACSA25I125', 'ACSA25I150', 'ACSA25I200', 'ACSA45I0', 'ACSA45I10', 'ACSA45I15', 'ACSA45I20', 'ACSA45I25', 'ACSA45I30', 'ACSA45I35', 'ACSA45I40', 'ACSA45I45', 'ACSA45I50', 'ACSA45I60', 'ACSA45I75', 'ACSA45I100', 'ACSA45I125', 'ACSA45I150', 'ACSA45I200', 'ACSA65I0', 'ACSA65I10', 'ACSA65I15', 'ACSA65I20', 'ACSA65I25', 'ACSA65I30', 'ACSA65I35', 'ACSA65I40', 'ACSA65I45', 'ACSA65I50', 'ACSA65I60', 'ACSA65I75', 'ACSA65I100', 'ACSA65I125', 'ACSA65I150', 'ACSA65I200', 'ACSUNT1DET', 'ACSUNT1ATT', 'ACSUNT2', 'ACSUNT3', 'ACSUNT5', 'ACSUNT10', 'ACSUNT20', 'ACSUNT50UP', 'ACSUNTMOB', 'ACSUNTOTH', 'ACSBLT2005', 'ACSBLT2000', 'ACSBLT1990', 'ACSBLT1980', 'ACSBLT1970', 'ACSBLT1960', 'ACSBLT1950', 'ACSBLT1940', 'ACSBLT1939', 'ACSOMV2005', 'ACSOMV2000', 'ACSOMV1990', 'ACSOMV1980', 'ACSOMV1970', 'ACSOMV1969', 'ACSRMV2005', 'ACSRMV2000', 'ACSRMV1990', 'ACSRMV1980', 'ACSRMV1970', 'ACSRMV1969', 'X4060_X', 'X4080_X', 'X4084_X', 'X4095_X', 'X4096_X', 'X4085_X', 'X4082_X', 'X4057_X', 'X4011_X', 'X4012_X', 'X4013_X', 'X3019_X', 'X3041_X', 'X3048_X', 'X3047_X', 'X3025_X', 'HI_PROD_PROXY_CY', 'TOTHU_CY', 'OWNER_CY', 'RENTER_CY', 'VACANT_CY') and data_item_id not in (2435, 2443) order by name
--select * from data_items where name in ('ACSUNT1DET', 'ACSUNT1ATT', 'ACSUNT2', 'ACSUNT3', 'ACSUNT5', 'ACSUNT10', 'ACSUNT20', 'ACSUNT50UP') order by data_item_id
