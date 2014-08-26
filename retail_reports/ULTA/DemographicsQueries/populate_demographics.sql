use ULTA_OCT13_20MSQWHSPC_100213
go

declare @threshold_id int = 5

insert into [demographics_denorm_5_mile] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
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
MEDHINC_CY,
AVGHINC_CY,
PCI_CY,
POP0_CY,
POP5_CY,
POP10_CY,
POP15_CY,
POP20_CY,
POP2534_CY,
POP3544_CY,
POP4554_CY,
POP5564_CY,
POP6574_CY,
POP7584_CY,
POP85_CY,
WHITE_CY,
BLACK_CY,
AMERIND_CY,
ASIAN_CY,
PACIFIC_CY,
OTHRACE_CY,
RACE2UP_CY,
HISPPOPCY,
HINC_50KPLUS_CY,
HINC_75KPLUS_CY,
HINC_100KPLUS,
POP_25PLUS_CY,
POP_30PLUS_CY,
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
dn_MEDHINC_CY.value as MEDHINC_CY,
dn_AVGHINC_CY.value as AVGHINC_CY,
dn_PCI_CY.value as PCI_CY,
dn_POP0_CY.value as POP0_CY,
dn_POP5_CY.value as POP5_CY,
dn_POP10_CY.value as POP10_CY,
dn_POP15_CY.value as POP15_CY,
dn_POP20_CY.value as POP20_CY,
dn_POP2534_CY.value as POP2534_CY,
dn_POP3544_CY.value as POP3544_CY,
dn_POP4554_CY.value as POP4554_CY,
dn_POP5564_CY.value as POP5564_CY,
dn_POP6574_CY.value as POP6574_CY,
dn_POP7584_CY.value as POP7584_CY,
dn_POP85_CY.value as POP85_CY,
dn_WHITE_CY.value as WHITE_CY,
dn_BLACK_CY.value as BLACK_CY,
dn_AMERIND_CY.value as AMERIND_CY,
dn_ASIAN_CY.value as ASIAN_CY,
dn_PACIFIC_CY.value as PACIFIC_CY,
dn_OTHRACE_CY.value as OTHRACE_CY,
dn_RACE2UP_CY.value as RACE2UP_CY,
dn_HISPPOPCY.value as HISPPOPCY,
dn_HINC_50KPLUS_CY.value as HINC_50KPLUS_CY,
dn_HINC_75KPLUS_CY.value as HINC_75KPLUS_CY,
dn_HINC_100KPLUS.value as HINC_100KPLUS,
dn_POP_25PLUS_CY.value as POP_25PLUS_CY,
dn_POP_30PLUS_CY.value as POP_30PLUS_CY,
dn_AGG_INCOME.value as AGG_INCOME,
dn_X10003_X.value as X10003_X,
dn_X10008_X.value as X10008_X,
dn_X10012_X.value as X10012_X,
dn_FEMALE_15PLUS.value as FEMALE_15PLUS
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
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
left join demographic_numvalues dn_MEDHINC_CY on dn_MEDHINC_CY.trade_area_id = t.trade_area_id and dn_MEDHINC_CY.data_item_id = 84
left join demographic_numvalues dn_AVGHINC_CY on dn_AVGHINC_CY.trade_area_id = t.trade_area_id and dn_AVGHINC_CY.data_item_id = 86
left join demographic_numvalues dn_PCI_CY on dn_PCI_CY.trade_area_id = t.trade_area_id and dn_PCI_CY.data_item_id = 88
left join demographic_numvalues dn_POP0_CY on dn_POP0_CY.trade_area_id = t.trade_area_id and dn_POP0_CY.data_item_id = 92
left join demographic_numvalues dn_POP5_CY on dn_POP5_CY.trade_area_id = t.trade_area_id and dn_POP5_CY.data_item_id = 98
left join demographic_numvalues dn_POP10_CY on dn_POP10_CY.trade_area_id = t.trade_area_id and dn_POP10_CY.data_item_id = 104
left join demographic_numvalues dn_POP15_CY on dn_POP15_CY.trade_area_id = t.trade_area_id and dn_POP15_CY.data_item_id = 110
left join demographic_numvalues dn_POP20_CY on dn_POP20_CY.trade_area_id = t.trade_area_id and dn_POP20_CY.data_item_id = 116
left join demographic_numvalues dn_POP2534_CY on dn_POP2534_CY.trade_area_id = t.trade_area_id and dn_POP2534_CY.data_item_id = 122
left join demographic_numvalues dn_POP3544_CY on dn_POP3544_CY.trade_area_id = t.trade_area_id and dn_POP3544_CY.data_item_id = 128
left join demographic_numvalues dn_POP4554_CY on dn_POP4554_CY.trade_area_id = t.trade_area_id and dn_POP4554_CY.data_item_id = 134
left join demographic_numvalues dn_POP5564_CY on dn_POP5564_CY.trade_area_id = t.trade_area_id and dn_POP5564_CY.data_item_id = 140
left join demographic_numvalues dn_POP6574_CY on dn_POP6574_CY.trade_area_id = t.trade_area_id and dn_POP6574_CY.data_item_id = 146
left join demographic_numvalues dn_POP7584_CY on dn_POP7584_CY.trade_area_id = t.trade_area_id and dn_POP7584_CY.data_item_id = 152
left join demographic_numvalues dn_POP85_CY on dn_POP85_CY.trade_area_id = t.trade_area_id and dn_POP85_CY.data_item_id = 158
left join demographic_numvalues dn_WHITE_CY on dn_WHITE_CY.trade_area_id = t.trade_area_id and dn_WHITE_CY.data_item_id = 164
left join demographic_numvalues dn_BLACK_CY on dn_BLACK_CY.trade_area_id = t.trade_area_id and dn_BLACK_CY.data_item_id = 170
left join demographic_numvalues dn_AMERIND_CY on dn_AMERIND_CY.trade_area_id = t.trade_area_id and dn_AMERIND_CY.data_item_id = 176
left join demographic_numvalues dn_ASIAN_CY on dn_ASIAN_CY.trade_area_id = t.trade_area_id and dn_ASIAN_CY.data_item_id = 182
left join demographic_numvalues dn_PACIFIC_CY on dn_PACIFIC_CY.trade_area_id = t.trade_area_id and dn_PACIFIC_CY.data_item_id = 188
left join demographic_numvalues dn_OTHRACE_CY on dn_OTHRACE_CY.trade_area_id = t.trade_area_id and dn_OTHRACE_CY.data_item_id = 194
left join demographic_numvalues dn_RACE2UP_CY on dn_RACE2UP_CY.trade_area_id = t.trade_area_id and dn_RACE2UP_CY.data_item_id = 200
left join demographic_numvalues dn_HISPPOPCY on dn_HISPPOPCY.trade_area_id = t.trade_area_id and dn_HISPPOPCY.data_item_id = 206
left join demographic_numvalues dn_HINC_50KPLUS_CY on dn_HINC_50KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_50KPLUS_CY.data_item_id = 2805
left join demographic_numvalues dn_HINC_75KPLUS_CY on dn_HINC_75KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_75KPLUS_CY.data_item_id = 2806
left join demographic_numvalues dn_HINC_100KPLUS on dn_HINC_100KPLUS.trade_area_id = t.trade_area_id and dn_HINC_100KPLUS.data_item_id = 2807
left join demographic_numvalues dn_POP_25PLUS_CY on dn_POP_25PLUS_CY.trade_area_id = t.trade_area_id and dn_POP_25PLUS_CY.data_item_id = 2808
left join demographic_numvalues dn_POP_30PLUS_CY on dn_POP_30PLUS_CY.trade_area_id = t.trade_area_id and dn_POP_30PLUS_CY.data_item_id = 2809
left join demographic_numvalues dn_AGG_INCOME on dn_AGG_INCOME.trade_area_id = t.trade_area_id and dn_AGG_INCOME.data_item_id = 2810
left join demographic_numvalues dn_X10003_X on dn_X10003_X.trade_area_id = t.trade_area_id and dn_X10003_X.data_item_id = 2927
left join demographic_numvalues dn_X10008_X on dn_X10008_X.trade_area_id = t.trade_area_id and dn_X10008_X.data_item_id = 2928
left join demographic_numvalues dn_X10012_X on dn_X10012_X.trade_area_id = t.trade_area_id and dn_X10012_X.data_item_id = 2929
left join demographic_numvalues dn_FEMALE_15PLUS on dn_FEMALE_15PLUS.trade_area_id = t.trade_area_id and dn_FEMALE_15PLUS.data_item_id = 2943