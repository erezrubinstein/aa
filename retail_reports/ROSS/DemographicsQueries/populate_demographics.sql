use retaildb_timeseries_ROSS_20_mile_whitespace
go

declare @threshold_id int = 10


insert into [demographics_denorm] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
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
X5001_X,
X5066_X,
X1002_X,
X4028_X,
X10002_X,
X12002_X,
X12005_X,
M28001a_B,
M28003a_B,
M28004a_B,
M28005a_B,
M28006a_B,
M28007a_B,
M28009a_B,
M28010a_B,
M11013a_B,
M11017a_B,
	agg_income,
	less_than_35K_HH,
	less_than_50K_HH,
	less_than_75K_HH)

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
dn_X5001_X.value as X5001_X,
dn_X5066_X.value as X5066_X,
dn_X1002_X.value as X1002_X,
dn_X4028_X.value as X4028_X,
dn_X10002_X.value as X10002_X,
dn_X12002_X.value as X12002_X,
dn_X12005_X.value as X12005_X,
dn_M28001a_B.value as M28001a_B,
dn_M28003a_B.value as M28003a_B,
dn_M28004a_B.value as M28004a_B,
dn_M28005a_B.value as M28005a_B,
dn_M28006a_B.value as M28006a_B,
dn_M28007a_B.value as M28007a_B,
dn_M28009a_B.value as M28009a_B,
dn_M28010a_B.value as M28010a_B,
dn_M11013a_B.value as M11013a_B,
dn_M11017a_B.value as M11017a_B,
	(dn_TOTPOP_CY.value * dn_PCI_CY.value) as agg_income,
	dn_HINC0_CY.value + dn_HINC15_CY.value + dn_HINC25_CY.value as less_than_35K_HH,
	dn_HINC0_CY.value + dn_HINC15_CY.value + dn_HINC25_CY.value + dn_HINC35_CY.value as less_than_50K_HH,
	dn_HINC0_CY.value + dn_HINC15_CY.value + dn_HINC25_CY.value + dn_HINC35_CY.value + dn_HINC50_CY.value as less_than_75K_HH
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13 and dn_TOTPOP_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_TOTHH_CY on dn_TOTHH_CY.trade_area_id = t.trade_area_id and dn_TOTHH_CY.data_item_id = 16 and dn_TOTHH_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_MEDAGE_CY on dn_MEDAGE_CY.trade_area_id = t.trade_area_id and dn_MEDAGE_CY.data_item_id = 31 and dn_MEDAGE_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC0_CY on dn_HINC0_CY.trade_area_id = t.trade_area_id and dn_HINC0_CY.data_item_id = 48 and dn_HINC0_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC15_CY on dn_HINC15_CY.trade_area_id = t.trade_area_id and dn_HINC15_CY.data_item_id = 52 and dn_HINC15_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC25_CY on dn_HINC25_CY.trade_area_id = t.trade_area_id and dn_HINC25_CY.data_item_id = 56 and dn_HINC25_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC35_CY on dn_HINC35_CY.trade_area_id = t.trade_area_id and dn_HINC35_CY.data_item_id = 60 and dn_HINC35_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC50_CY on dn_HINC50_CY.trade_area_id = t.trade_area_id and dn_HINC50_CY.data_item_id = 64 and dn_HINC50_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC75_CY on dn_HINC75_CY.trade_area_id = t.trade_area_id and dn_HINC75_CY.data_item_id = 68 and dn_HINC75_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC100_CY on dn_HINC100_CY.trade_area_id = t.trade_area_id and dn_HINC100_CY.data_item_id = 72 and dn_HINC100_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC150_CY on dn_HINC150_CY.trade_area_id = t.trade_area_id and dn_HINC150_CY.data_item_id = 76 and dn_HINC150_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HINC200_CY on dn_HINC200_CY.trade_area_id = t.trade_area_id and dn_HINC200_CY.data_item_id = 80 and dn_HINC200_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_MEDHINC_CY on dn_MEDHINC_CY.trade_area_id = t.trade_area_id and dn_MEDHINC_CY.data_item_id = 84 and dn_MEDHINC_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_AVGHINC_CY on dn_AVGHINC_CY.trade_area_id = t.trade_area_id and dn_AVGHINC_CY.data_item_id = 86 and dn_AVGHINC_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_PCI_CY on dn_PCI_CY.trade_area_id = t.trade_area_id and dn_PCI_CY.data_item_id = 88 and dn_PCI_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP0_CY on dn_POP0_CY.trade_area_id = t.trade_area_id and dn_POP0_CY.data_item_id = 92 and dn_POP0_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP5_CY on dn_POP5_CY.trade_area_id = t.trade_area_id and dn_POP5_CY.data_item_id = 98 and dn_POP5_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP10_CY on dn_POP10_CY.trade_area_id = t.trade_area_id and dn_POP10_CY.data_item_id = 104 and dn_POP10_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP15_CY on dn_POP15_CY.trade_area_id = t.trade_area_id and dn_POP15_CY.data_item_id = 110 and dn_POP15_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP20_CY on dn_POP20_CY.trade_area_id = t.trade_area_id and dn_POP20_CY.data_item_id = 116 and dn_POP20_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP2534_CY on dn_POP2534_CY.trade_area_id = t.trade_area_id and dn_POP2534_CY.data_item_id = 122 and dn_POP2534_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP3544_CY on dn_POP3544_CY.trade_area_id = t.trade_area_id and dn_POP3544_CY.data_item_id = 128 and dn_POP3544_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP4554_CY on dn_POP4554_CY.trade_area_id = t.trade_area_id and dn_POP4554_CY.data_item_id = 134 and dn_POP4554_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP5564_CY on dn_POP5564_CY.trade_area_id = t.trade_area_id and dn_POP5564_CY.data_item_id = 140 and dn_POP5564_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP6574_CY on dn_POP6574_CY.trade_area_id = t.trade_area_id and dn_POP6574_CY.data_item_id = 146 and dn_POP6574_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP7584_CY on dn_POP7584_CY.trade_area_id = t.trade_area_id and dn_POP7584_CY.data_item_id = 152 and dn_POP7584_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_POP85_CY on dn_POP85_CY.trade_area_id = t.trade_area_id and dn_POP85_CY.data_item_id = 158 and dn_POP85_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_WHITE_CY on dn_WHITE_CY.trade_area_id = t.trade_area_id and dn_WHITE_CY.data_item_id = 164 and dn_WHITE_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_BLACK_CY on dn_BLACK_CY.trade_area_id = t.trade_area_id and dn_BLACK_CY.data_item_id = 170 and dn_BLACK_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_AMERIND_CY on dn_AMERIND_CY.trade_area_id = t.trade_area_id and dn_AMERIND_CY.data_item_id = 176 and dn_AMERIND_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_ASIAN_CY on dn_ASIAN_CY.trade_area_id = t.trade_area_id and dn_ASIAN_CY.data_item_id = 182 and dn_ASIAN_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_PACIFIC_CY on dn_PACIFIC_CY.trade_area_id = t.trade_area_id and dn_PACIFIC_CY.data_item_id = 188 and dn_PACIFIC_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_OTHRACE_CY on dn_OTHRACE_CY.trade_area_id = t.trade_area_id and dn_OTHRACE_CY.data_item_id = 194 and dn_OTHRACE_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_RACE2UP_CY on dn_RACE2UP_CY.trade_area_id = t.trade_area_id and dn_RACE2UP_CY.data_item_id = 200 and dn_RACE2UP_CY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_HISPPOPCY on dn_HISPPOPCY.trade_area_id = t.trade_area_id and dn_HISPPOPCY.data_item_id = 206 and dn_HISPPOPCY.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_X5001_X on dn_X5001_X.trade_area_id = t.trade_area_id and dn_X5001_X.data_item_id = 2451 and dn_X5001_X.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_X5066_X on dn_X5066_X.trade_area_id = t.trade_area_id and dn_X5066_X.data_item_id = 2469 and dn_X5066_X.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_X1002_X on dn_X1002_X.trade_area_id = t.trade_area_id and dn_X1002_X.data_item_id = 2559 and dn_X1002_X.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_X4028_X on dn_X4028_X.trade_area_id = t.trade_area_id and dn_X4028_X.data_item_id = 2646 and dn_X4028_X.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_X10002_X on dn_X10002_X.trade_area_id = t.trade_area_id and dn_X10002_X.data_item_id = 2661 and dn_X10002_X.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_X12002_X on dn_X12002_X.trade_area_id = t.trade_area_id and dn_X12002_X.data_item_id = 2732 and dn_X12002_X.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_X12005_X on dn_X12005_X.trade_area_id = t.trade_area_id and dn_X12005_X.data_item_id = 2733 and dn_X12005_X.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M28001a_B on dn_M28001a_B.trade_area_id = t.trade_area_id and dn_M28001a_B.data_item_id = 2734 and dn_M28001a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M28003a_B on dn_M28003a_B.trade_area_id = t.trade_area_id and dn_M28003a_B.data_item_id = 2735 and dn_M28003a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M28004a_B on dn_M28004a_B.trade_area_id = t.trade_area_id and dn_M28004a_B.data_item_id = 2736 and dn_M28004a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M28005a_B on dn_M28005a_B.trade_area_id = t.trade_area_id and dn_M28005a_B.data_item_id = 2737 and dn_M28005a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M28006a_B on dn_M28006a_B.trade_area_id = t.trade_area_id and dn_M28006a_B.data_item_id = 2738 and dn_M28006a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M28007a_B on dn_M28007a_B.trade_area_id = t.trade_area_id and dn_M28007a_B.data_item_id = 2739 and dn_M28007a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M28009a_B on dn_M28009a_B.trade_area_id = t.trade_area_id and dn_M28009a_B.data_item_id = 2740 and dn_M28009a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M28010a_B on dn_M28010a_B.trade_area_id = t.trade_area_id and dn_M28010a_B.data_item_id = 2741 and dn_M28010a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M11013a_B on dn_M11013a_B.trade_area_id = t.trade_area_id and dn_M11013a_B.data_item_id = 2742 and dn_M11013a_B.template_name = 'DollarStores_APR13'
left join demographic_numvalues dn_M11017a_B on dn_M11017a_B.trade_area_id = t.trade_area_id and dn_M11017a_B.data_item_id = 2743 and dn_M11017a_B.template_name = 'DollarStores_APR13'