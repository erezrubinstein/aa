use ULTA_OCT13_20MSQWHSPC_100213
go

declare @threshold_id int = 1

insert into [demographics_denorm] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
	TOTPOP_CY,
TOTHH_CY,
HINC_50KPLUS_CY,
HINC_75KPLUS_CY,
AGG_INCOME,
X10003_X,
X10008_X,
X10012_X,
FEMALE_15PLUS)

	select
		c.name as company_name,
		s.store_id,
		s.assumed_opened_date,
		s.assumed_closed_date,
		t.trade_area_id,
		dn_TOTPOP_CY.value as TOTPOP_CY,
dn_TOTHH_CY.value as TOTHH_CY,
dn_HINC_50KPLUS_CY.value as HINC_50KPLUS_CY,
dn_HINC_75KPLUS_CY.value as HINC_75KPLUS_CY,
dn_AGG_INCOME.value as AGG_INCOME,
dn_X10003_X.value as X10003_X,
dn_X10008_X.value as X10008_X,
dn_X10012_X.value as X10012_X,
dn_FEMALE_15PLUS.value as FEMALE_15PLUS
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13 and dn_TOTPOP_CY.template_name = 'cosmetics_sep13'
left join demographic_numvalues dn_TOTHH_CY on dn_TOTHH_CY.trade_area_id = t.trade_area_id and dn_TOTHH_CY.data_item_id = 16 and dn_TOTHH_CY.template_name = 'cosmetics_sep13'
left join demographic_numvalues dn_HINC_50KPLUS_CY on dn_HINC_50KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_50KPLUS_CY.data_item_id = 2805 and dn_HINC_50KPLUS_CY.template_name = 'cosmetics_sep13'
left join demographic_numvalues dn_HINC_75KPLUS_CY on dn_HINC_75KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_75KPLUS_CY.data_item_id = 2806 and dn_HINC_75KPLUS_CY.template_name = 'cosmetics_sep13'
left join demographic_numvalues dn_AGG_INCOME on dn_AGG_INCOME.trade_area_id = t.trade_area_id and dn_AGG_INCOME.data_item_id = 2810 and dn_AGG_INCOME.template_name = 'cosmetics_sep13'
left join demographic_numvalues dn_X10003_X on dn_X10003_X.trade_area_id = t.trade_area_id and dn_X10003_X.data_item_id = 2927
left join demographic_numvalues dn_X10008_X on dn_X10008_X.trade_area_id = t.trade_area_id and dn_X10008_X.data_item_id = 2928
left join demographic_numvalues dn_X10012_X on dn_X10012_X.trade_area_id = t.trade_area_id and dn_X10012_X.data_item_id = 2929
left join demographic_numvalues dn_FEMALE_15PLUS on dn_FEMALE_15PLUS.trade_area_id = t.trade_area_id and dn_FEMALE_15PLUS.data_item_id = 2943