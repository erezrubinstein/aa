use DOLLFULL_JUN13_CMA_062313
go

--declare @threshold_id int = 5
declare @threshold_id int = 8

insert into [demographics_denorm_3_mile] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
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
ACSFEMPBAS,
ACSKDSLT6O,
ACSLT6FLF,
ACSLT6FNLF,
ACSKIDS,
ACSKDSFLF,
ACSKDSFNLF,
ACSKDS617O,
ACS617FLF,
ACS617FNLF,
ACSNOKIDS,
ACSNKDFLF,
ACSNKDFNLF,
ACSHPOVBAS,
ACSHHBPOV,
ACSBPOVMCF,
ACSBPOVOFM,
ACSBPOVOFF,
ACSBPOVNFM,
ACSBPOVNFF,
ACSHHAPOV,
ACSAPOVMCF,
ACSAPOVOFM,
ACSAPOVOFF,
ACSAPOVNFM,
ACSAPOVNFF,
X5001_X,
X5066_X,
X1002_X,
X4028_X,
X10002_X,
X12002_X,
X12005_X,
	agg_income,
	less_than_50K_HH,
	less_than_75K_HH,
	pct_black,
	pct_hispanic,
	femHH)

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
dn_ACSFEMPBAS.value as ACSFEMPBAS,
dn_ACSKDSLT6O.value as ACSKDSLT6O,
dn_ACSLT6FLF.value as ACSLT6FLF,
dn_ACSLT6FNLF.value as ACSLT6FNLF,
dn_ACSKIDS.value as ACSKIDS,
dn_ACSKDSFLF.value as ACSKDSFLF,
dn_ACSKDSFNLF.value as ACSKDSFNLF,
dn_ACSKDS617O.value as ACSKDS617O,
dn_ACS617FLF.value as ACS617FLF,
dn_ACS617FNLF.value as ACS617FNLF,
dn_ACSNOKIDS.value as ACSNOKIDS,
dn_ACSNKDFLF.value as ACSNKDFLF,
dn_ACSNKDFNLF.value as ACSNKDFNLF,
dn_ACSHPOVBAS.value as ACSHPOVBAS,
dn_ACSHHBPOV.value as ACSHHBPOV,
dn_ACSBPOVMCF.value as ACSBPOVMCF,
dn_ACSBPOVOFM.value as ACSBPOVOFM,
dn_ACSBPOVOFF.value as ACSBPOVOFF,
dn_ACSBPOVNFM.value as ACSBPOVNFM,
dn_ACSBPOVNFF.value as ACSBPOVNFF,
dn_ACSHHAPOV.value as ACSHHAPOV,
dn_ACSAPOVMCF.value as ACSAPOVMCF,
dn_ACSAPOVOFM.value as ACSAPOVOFM,
dn_ACSAPOVOFF.value as ACSAPOVOFF,
dn_ACSAPOVNFM.value as ACSAPOVNFM,
dn_ACSAPOVNFF.value as ACSAPOVNFF,
dn_X5001_X.value as X5001_X,
dn_X5066_X.value as X5066_X,
dn_X1002_X.value as X1002_X,
dn_X4028_X.value as X4028_X,
dn_X10002_X.value as X10002_X,
dn_X12002_X.value as X12002_X,
dn_X12005_X.value as X12005_X,
	(dn_TOTPOP_CY.value * dn_PCI_CY.value) as agg_income,
	dn_HINC0_CY.value + dn_HINC15_CY.value + dn_HINC25_CY.value + dn_HINC35_CY.value as less_than_50K_HH,
	dn_HINC0_CY.value + dn_HINC15_CY.value + dn_HINC25_CY.value + dn_HINC35_CY.value + dn_HINC50_CY.value as less_than_75K_HH,
	dn_BLACK_CY.value / dn_TOTPOP_CY.value as pct_black,
	dn_HISPPOPCY.value / dn_TOTPOP_CY.value as pct_hispanic,
	dn_ACSAPOVOFF.value + dn_ACSBPOVOFF.value as femHH
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13 and dn_TOTPOP_CY.template_name = 'DollarStores_APR13'
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
left join demographic_numvalues dn_ACSFEMPBAS on dn_ACSFEMPBAS.trade_area_id = t.trade_area_id and dn_ACSFEMPBAS.data_item_id = 1466
left join demographic_numvalues dn_ACSKDSLT6O on dn_ACSKDSLT6O.trade_area_id = t.trade_area_id and dn_ACSKDSLT6O.data_item_id = 1469
left join demographic_numvalues dn_ACSLT6FLF on dn_ACSLT6FLF.trade_area_id = t.trade_area_id and dn_ACSLT6FLF.data_item_id = 1472
left join demographic_numvalues dn_ACSLT6FNLF on dn_ACSLT6FNLF.trade_area_id = t.trade_area_id and dn_ACSLT6FNLF.data_item_id = 1475
left join demographic_numvalues dn_ACSKIDS on dn_ACSKIDS.trade_area_id = t.trade_area_id and dn_ACSKIDS.data_item_id = 1478
left join demographic_numvalues dn_ACSKDSFLF on dn_ACSKDSFLF.trade_area_id = t.trade_area_id and dn_ACSKDSFLF.data_item_id = 1481
left join demographic_numvalues dn_ACSKDSFNLF on dn_ACSKDSFNLF.trade_area_id = t.trade_area_id and dn_ACSKDSFNLF.data_item_id = 1484
left join demographic_numvalues dn_ACSKDS617O on dn_ACSKDS617O.trade_area_id = t.trade_area_id and dn_ACSKDS617O.data_item_id = 1487
left join demographic_numvalues dn_ACS617FLF on dn_ACS617FLF.trade_area_id = t.trade_area_id and dn_ACS617FLF.data_item_id = 1490
left join demographic_numvalues dn_ACS617FNLF on dn_ACS617FNLF.trade_area_id = t.trade_area_id and dn_ACS617FNLF.data_item_id = 1493
left join demographic_numvalues dn_ACSNOKIDS on dn_ACSNOKIDS.trade_area_id = t.trade_area_id and dn_ACSNOKIDS.data_item_id = 1496
left join demographic_numvalues dn_ACSNKDFLF on dn_ACSNKDFLF.trade_area_id = t.trade_area_id and dn_ACSNKDFLF.data_item_id = 1499
left join demographic_numvalues dn_ACSNKDFNLF on dn_ACSNKDFNLF.trade_area_id = t.trade_area_id and dn_ACSNKDFNLF.data_item_id = 1502
left join demographic_numvalues dn_ACSHPOVBAS on dn_ACSHPOVBAS.trade_area_id = t.trade_area_id and dn_ACSHPOVBAS.data_item_id = 1529
left join demographic_numvalues dn_ACSHHBPOV on dn_ACSHHBPOV.trade_area_id = t.trade_area_id and dn_ACSHHBPOV.data_item_id = 1532
left join demographic_numvalues dn_ACSBPOVMCF on dn_ACSBPOVMCF.trade_area_id = t.trade_area_id and dn_ACSBPOVMCF.data_item_id = 1535
left join demographic_numvalues dn_ACSBPOVOFM on dn_ACSBPOVOFM.trade_area_id = t.trade_area_id and dn_ACSBPOVOFM.data_item_id = 1538
left join demographic_numvalues dn_ACSBPOVOFF on dn_ACSBPOVOFF.trade_area_id = t.trade_area_id and dn_ACSBPOVOFF.data_item_id = 1541
left join demographic_numvalues dn_ACSBPOVNFM on dn_ACSBPOVNFM.trade_area_id = t.trade_area_id and dn_ACSBPOVNFM.data_item_id = 1544
left join demographic_numvalues dn_ACSBPOVNFF on dn_ACSBPOVNFF.trade_area_id = t.trade_area_id and dn_ACSBPOVNFF.data_item_id = 1547
left join demographic_numvalues dn_ACSHHAPOV on dn_ACSHHAPOV.trade_area_id = t.trade_area_id and dn_ACSHHAPOV.data_item_id = 1550
left join demographic_numvalues dn_ACSAPOVMCF on dn_ACSAPOVMCF.trade_area_id = t.trade_area_id and dn_ACSAPOVMCF.data_item_id = 1553
left join demographic_numvalues dn_ACSAPOVOFM on dn_ACSAPOVOFM.trade_area_id = t.trade_area_id and dn_ACSAPOVOFM.data_item_id = 1556
left join demographic_numvalues dn_ACSAPOVOFF on dn_ACSAPOVOFF.trade_area_id = t.trade_area_id and dn_ACSAPOVOFF.data_item_id = 1559
left join demographic_numvalues dn_ACSAPOVNFM on dn_ACSAPOVNFM.trade_area_id = t.trade_area_id and dn_ACSAPOVNFM.data_item_id = 1562
left join demographic_numvalues dn_ACSAPOVNFF on dn_ACSAPOVNFF.trade_area_id = t.trade_area_id and dn_ACSAPOVNFF.data_item_id = 1565
left join demographic_numvalues dn_X5001_X on dn_X5001_X.trade_area_id = t.trade_area_id and dn_X5001_X.data_item_id = 2451
left join demographic_numvalues dn_X5066_X on dn_X5066_X.trade_area_id = t.trade_area_id and dn_X5066_X.data_item_id = 2469
left join demographic_numvalues dn_X1002_X on dn_X1002_X.trade_area_id = t.trade_area_id and dn_X1002_X.data_item_id = 2559
left join demographic_numvalues dn_X4028_X on dn_X4028_X.trade_area_id = t.trade_area_id and dn_X4028_X.data_item_id = 2646
left join demographic_numvalues dn_X10002_X on dn_X10002_X.trade_area_id = t.trade_area_id and dn_X10002_X.data_item_id = 2661
left join demographic_numvalues dn_X12002_X on dn_X12002_X.trade_area_id = t.trade_area_id and dn_X12002_X.data_item_id = 2732
left join demographic_numvalues dn_X12005_X on dn_X12005_X.trade_area_id = t.trade_area_id and dn_X12005_X.data_item_id = 2733