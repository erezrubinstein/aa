use JOSB_OCT13_CMA_102213
go

declare @threshold_id int = 5

insert into [demographics_denorm_5_mile] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
	TOTPOP_CY,
TOTHH_CY,
MEDAGE_CY,
HINC0_CY,
HINC15_CY,
HINC25_CY,
HINC35_CY,
HINC50_CY,
HINC75_CY,
HINC100_CY,
HINC150_CY,
HINC200_CY,
PCI_CY,
HINC_50KPLUS_CY,
HINC_75KPLUS_CY,
HINC_100KPLUS,
AGG_INCOME,
X5003_X,
X5004_X,
MEN_20PLUS,
MENS_SUITS_SPCOAT)

	select
		c.name as company_name,
		s.store_id,
		s.assumed_opened_date,
		s.assumed_closed_date,
		t.trade_area_id,
		dn_TOTPOP_CY.value as TOTPOP_CY,
dn_TOTHH_CY.value as TOTHH_CY,
dn_MEDAGE_CY.value as MEDAGE_CY,
dn_HINC0_CY.value as HINC0_CY,
dn_HINC15_CY.value as HINC15_CY,
dn_HINC25_CY.value as HINC25_CY,
dn_HINC35_CY.value as HINC35_CY,
dn_HINC50_CY.value as HINC50_CY,
dn_HINC75_CY.value as HINC75_CY,
dn_HINC100_CY.value as HINC100_CY,
dn_HINC150_CY.value as HINC150_CY,
dn_HINC200_CY.value as HINC200_CY,
dn_PCI_CY.value as PCI_CY,
dn_HINC_50KPLUS_CY.value as HINC_50KPLUS_CY,
dn_HINC_75KPLUS_CY.value as HINC_75KPLUS_CY,
dn_HINC_100KPLUS.value as HINC_100KPLUS,
dn_AGG_INCOME.value as AGG_INCOME,
dn_X5003_X.value as X5003_X,
dn_X5004_X.value as X5004_X,
dn_MEN_20PLUS.value as MEN_20PLUS,
dn_MENS_SUITS_SPCOAT.value as MENS_SUITS_SPCOAT
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13
left join demographic_numvalues dn_TOTHH_CY on dn_TOTHH_CY.trade_area_id = t.trade_area_id and dn_TOTHH_CY.data_item_id = 16
left join demographic_numvalues dn_MEDAGE_CY on dn_MEDAGE_CY.trade_area_id = t.trade_area_id and dn_MEDAGE_CY.data_item_id = 31
left join demographic_numvalues dn_HINC0_CY on dn_HINC0_CY.trade_area_id = t.trade_area_id and dn_HINC0_CY.data_item_id = 48
left join demographic_numvalues dn_HINC15_CY on dn_HINC15_CY.trade_area_id = t.trade_area_id and dn_HINC15_CY.data_item_id = 52
left join demographic_numvalues dn_HINC25_CY on dn_HINC25_CY.trade_area_id = t.trade_area_id and dn_HINC25_CY.data_item_id = 56
left join demographic_numvalues dn_HINC35_CY on dn_HINC35_CY.trade_area_id = t.trade_area_id and dn_HINC35_CY.data_item_id = 60
left join demographic_numvalues dn_HINC50_CY on dn_HINC50_CY.trade_area_id = t.trade_area_id and dn_HINC50_CY.data_item_id = 64
left join demographic_numvalues dn_HINC75_CY on dn_HINC75_CY.trade_area_id = t.trade_area_id and dn_HINC75_CY.data_item_id = 68
left join demographic_numvalues dn_HINC100_CY on dn_HINC100_CY.trade_area_id = t.trade_area_id and dn_HINC100_CY.data_item_id = 72
left join demographic_numvalues dn_HINC150_CY on dn_HINC150_CY.trade_area_id = t.trade_area_id and dn_HINC150_CY.data_item_id = 76
left join demographic_numvalues dn_HINC200_CY on dn_HINC200_CY.trade_area_id = t.trade_area_id and dn_HINC200_CY.data_item_id = 80
left join demographic_numvalues dn_PCI_CY on dn_PCI_CY.trade_area_id = t.trade_area_id and dn_PCI_CY.data_item_id = 88
left join demographic_numvalues dn_HINC_50KPLUS_CY on dn_HINC_50KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_50KPLUS_CY.data_item_id = 2805
left join demographic_numvalues dn_HINC_75KPLUS_CY on dn_HINC_75KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_75KPLUS_CY.data_item_id = 2806
left join demographic_numvalues dn_HINC_100KPLUS on dn_HINC_100KPLUS.trade_area_id = t.trade_area_id and dn_HINC_100KPLUS.data_item_id = 2807
left join demographic_numvalues dn_AGG_INCOME on dn_AGG_INCOME.trade_area_id = t.trade_area_id and dn_AGG_INCOME.data_item_id = 2810
left join demographic_numvalues dn_X5003_X on dn_X5003_X.trade_area_id = t.trade_area_id and dn_X5003_X.data_item_id = 3009
left join demographic_numvalues dn_X5004_X on dn_X5004_X.trade_area_id = t.trade_area_id and dn_X5004_X.data_item_id = 3010
left join demographic_numvalues dn_MEN_20PLUS on dn_MEN_20PLUS.trade_area_id = t.trade_area_id and dn_MEN_20PLUS.data_item_id = 3011
left join demographic_numvalues dn_MENS_SUITS_SPCOAT on dn_MENS_SUITS_SPCOAT.trade_area_id = t.trade_area_id and dn_MENS_SUITS_SPCOAT.data_item_id = 3012