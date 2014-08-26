use SCSS_10MSQWHSPC_091316
go

declare @threshold_id int = 1

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
	ACSA25I50,
	ACSA25I60,
	ACSA25I75,
	ACSA25I100,
	ACSA25I125,
	ACSA25I150,
	ACSA25I200,
	ACSA45I50,
	ACSA45I60,
	ACSA45I75,
	ACSA45I100,
	ACSA45I125,
	ACSA45I150,
	ACSA45I200,
	ACSA65I50,
	ACSA65I60,
	ACSA65I75,
	ACSA65I100,
	ACSA65I125,
	ACSA65I150,
	ACSA65I200,
	X4048_X,
	HINC_50KPLUS_CY,
	HINC_75KPLUS_CY,
	HINC_100KPLUS,
	POP_25PLUS_CY,
	POP_30PLUS_CY,
	AGG_INCOME)

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
	dn_ACSA25I50.value as ACSA25I50,
	dn_ACSA25I60.value as ACSA25I60,
	dn_ACSA25I75.value as ACSA25I75,
	dn_ACSA25I100.value as ACSA25I100,
	dn_ACSA25I125.value as ACSA25I125,
	dn_ACSA25I150.value as ACSA25I150,
	dn_ACSA25I200.value as ACSA25I200,
	dn_ACSA45I50.value as ACSA45I50,
	dn_ACSA45I60.value as ACSA45I60,
	dn_ACSA45I75.value as ACSA45I75,
	dn_ACSA45I100.value as ACSA45I100,
	dn_ACSA45I125.value as ACSA45I125,
	dn_ACSA45I150.value as ACSA45I150,
	dn_ACSA45I200.value as ACSA45I200,
	dn_ACSA65I50.value as ACSA65I50,
	dn_ACSA65I60.value as ACSA65I60,
	dn_ACSA65I75.value as ACSA65I75,
	dn_ACSA65I100.value as ACSA65I100,
	dn_ACSA65I125.value as ACSA65I125,
	dn_ACSA65I150.value as ACSA65I150,
	dn_ACSA65I200.value as ACSA65I200,
	dn_X4048_X.value as X4048_X,
	dn_HINC_50KPLUS_CY.value as HINC_50KPLUS_CY,
	dn_HINC_75KPLUS_CY.value as HINC_75KPLUS_CY,
	dn_HINC_100KPLUS.value as HINC_100KPLUS,
	dn_POP_25PLUS_CY.value as POP_25PLUS_CY,
	dn_POP_30PLUS_CY.value as POP_30PLUS_CY,
	dn_AGG_INCOME.value as AGG_INCOME
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13 and dn_TOTPOP_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_TOTHH_CY on dn_TOTHH_CY.trade_area_id = t.trade_area_id and dn_TOTHH_CY.data_item_id = 16 and dn_TOTHH_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_MEDAGE_CY on dn_MEDAGE_CY.trade_area_id = t.trade_area_id and dn_MEDAGE_CY.data_item_id = 31 and dn_MEDAGE_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC0_CY on dn_HINC0_CY.trade_area_id = t.trade_area_id and dn_HINC0_CY.data_item_id = 48 and dn_HINC0_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC15_CY on dn_HINC15_CY.trade_area_id = t.trade_area_id and dn_HINC15_CY.data_item_id = 52 and dn_HINC15_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC25_CY on dn_HINC25_CY.trade_area_id = t.trade_area_id and dn_HINC25_CY.data_item_id = 56 and dn_HINC25_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC35_CY on dn_HINC35_CY.trade_area_id = t.trade_area_id and dn_HINC35_CY.data_item_id = 60 and dn_HINC35_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC50_CY on dn_HINC50_CY.trade_area_id = t.trade_area_id and dn_HINC50_CY.data_item_id = 64 and dn_HINC50_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC75_CY on dn_HINC75_CY.trade_area_id = t.trade_area_id and dn_HINC75_CY.data_item_id = 68 and dn_HINC75_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC100_CY on dn_HINC100_CY.trade_area_id = t.trade_area_id and dn_HINC100_CY.data_item_id = 72 and dn_HINC100_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC150_CY on dn_HINC150_CY.trade_area_id = t.trade_area_id and dn_HINC150_CY.data_item_id = 76 and dn_HINC150_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HINC200_CY on dn_HINC200_CY.trade_area_id = t.trade_area_id and dn_HINC200_CY.data_item_id = 80 and dn_HINC200_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_PCI_CY on dn_PCI_CY.trade_area_id = t.trade_area_id and dn_PCI_CY.data_item_id = 88 and dn_PCI_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP0_CY on dn_POP0_CY.trade_area_id = t.trade_area_id and dn_POP0_CY.data_item_id = 92 and dn_POP0_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP5_CY on dn_POP5_CY.trade_area_id = t.trade_area_id and dn_POP5_CY.data_item_id = 98 and dn_POP5_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP10_CY on dn_POP10_CY.trade_area_id = t.trade_area_id and dn_POP10_CY.data_item_id = 104 and dn_POP10_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP15_CY on dn_POP15_CY.trade_area_id = t.trade_area_id and dn_POP15_CY.data_item_id = 110 and dn_POP15_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP20_CY on dn_POP20_CY.trade_area_id = t.trade_area_id and dn_POP20_CY.data_item_id = 116 and dn_POP20_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP2534_CY on dn_POP2534_CY.trade_area_id = t.trade_area_id and dn_POP2534_CY.data_item_id = 122 and dn_POP2534_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP3544_CY on dn_POP3544_CY.trade_area_id = t.trade_area_id and dn_POP3544_CY.data_item_id = 128 and dn_POP3544_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP4554_CY on dn_POP4554_CY.trade_area_id = t.trade_area_id and dn_POP4554_CY.data_item_id = 134 and dn_POP4554_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP5564_CY on dn_POP5564_CY.trade_area_id = t.trade_area_id and dn_POP5564_CY.data_item_id = 140 and dn_POP5564_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP6574_CY on dn_POP6574_CY.trade_area_id = t.trade_area_id and dn_POP6574_CY.data_item_id = 146 and dn_POP6574_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP7584_CY on dn_POP7584_CY.trade_area_id = t.trade_area_id and dn_POP7584_CY.data_item_id = 152 and dn_POP7584_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_POP85_CY on dn_POP85_CY.trade_area_id = t.trade_area_id and dn_POP85_CY.data_item_id = 158 and dn_POP85_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_WHITE_CY on dn_WHITE_CY.trade_area_id = t.trade_area_id and dn_WHITE_CY.data_item_id = 164 and dn_WHITE_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_BLACK_CY on dn_BLACK_CY.trade_area_id = t.trade_area_id and dn_BLACK_CY.data_item_id = 170 and dn_BLACK_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_AMERIND_CY on dn_AMERIND_CY.trade_area_id = t.trade_area_id and dn_AMERIND_CY.data_item_id = 176 and dn_AMERIND_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_ASIAN_CY on dn_ASIAN_CY.trade_area_id = t.trade_area_id and dn_ASIAN_CY.data_item_id = 182 and dn_ASIAN_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_PACIFIC_CY on dn_PACIFIC_CY.trade_area_id = t.trade_area_id and dn_PACIFIC_CY.data_item_id = 188 and dn_PACIFIC_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_OTHRACE_CY on dn_OTHRACE_CY.trade_area_id = t.trade_area_id and dn_OTHRACE_CY.data_item_id = 194 and dn_OTHRACE_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_RACE2UP_CY on dn_RACE2UP_CY.trade_area_id = t.trade_area_id and dn_RACE2UP_CY.data_item_id = 200 and dn_RACE2UP_CY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_HISPPOPCY on dn_HISPPOPCY.trade_area_id = t.trade_area_id and dn_HISPPOPCY.data_item_id = 206 and dn_HISPPOPCY.template_name = 'Mattress_June13'
left join demographic_numvalues dn_ACSA25I50 on dn_ACSA25I50.trade_area_id = t.trade_area_id and dn_ACSA25I50.data_item_id = 1715
left join demographic_numvalues dn_ACSA25I60 on dn_ACSA25I60.trade_area_id = t.trade_area_id and dn_ACSA25I60.data_item_id = 1718
left join demographic_numvalues dn_ACSA25I75 on dn_ACSA25I75.trade_area_id = t.trade_area_id and dn_ACSA25I75.data_item_id = 1721
left join demographic_numvalues dn_ACSA25I100 on dn_ACSA25I100.trade_area_id = t.trade_area_id and dn_ACSA25I100.data_item_id = 1724
left join demographic_numvalues dn_ACSA25I125 on dn_ACSA25I125.trade_area_id = t.trade_area_id and dn_ACSA25I125.data_item_id = 1727
left join demographic_numvalues dn_ACSA25I150 on dn_ACSA25I150.trade_area_id = t.trade_area_id and dn_ACSA25I150.data_item_id = 1730
left join demographic_numvalues dn_ACSA25I200 on dn_ACSA25I200.trade_area_id = t.trade_area_id and dn_ACSA25I200.data_item_id = 1733
left join demographic_numvalues dn_ACSA45I50 on dn_ACSA45I50.trade_area_id = t.trade_area_id and dn_ACSA45I50.data_item_id = 1772
left join demographic_numvalues dn_ACSA45I60 on dn_ACSA45I60.trade_area_id = t.trade_area_id and dn_ACSA45I60.data_item_id = 1775
left join demographic_numvalues dn_ACSA45I75 on dn_ACSA45I75.trade_area_id = t.trade_area_id and dn_ACSA45I75.data_item_id = 1778
left join demographic_numvalues dn_ACSA45I100 on dn_ACSA45I100.trade_area_id = t.trade_area_id and dn_ACSA45I100.data_item_id = 1781
left join demographic_numvalues dn_ACSA45I125 on dn_ACSA45I125.trade_area_id = t.trade_area_id and dn_ACSA45I125.data_item_id = 1784
left join demographic_numvalues dn_ACSA45I150 on dn_ACSA45I150.trade_area_id = t.trade_area_id and dn_ACSA45I150.data_item_id = 1787
left join demographic_numvalues dn_ACSA45I200 on dn_ACSA45I200.trade_area_id = t.trade_area_id and dn_ACSA45I200.data_item_id = 1790
left join demographic_numvalues dn_ACSA65I50 on dn_ACSA65I50.trade_area_id = t.trade_area_id and dn_ACSA65I50.data_item_id = 1829
left join demographic_numvalues dn_ACSA65I60 on dn_ACSA65I60.trade_area_id = t.trade_area_id and dn_ACSA65I60.data_item_id = 1832
left join demographic_numvalues dn_ACSA65I75 on dn_ACSA65I75.trade_area_id = t.trade_area_id and dn_ACSA65I75.data_item_id = 1835
left join demographic_numvalues dn_ACSA65I100 on dn_ACSA65I100.trade_area_id = t.trade_area_id and dn_ACSA65I100.data_item_id = 1838
left join demographic_numvalues dn_ACSA65I125 on dn_ACSA65I125.trade_area_id = t.trade_area_id and dn_ACSA65I125.data_item_id = 1841
left join demographic_numvalues dn_ACSA65I150 on dn_ACSA65I150.trade_area_id = t.trade_area_id and dn_ACSA65I150.data_item_id = 1844
left join demographic_numvalues dn_ACSA65I200 on dn_ACSA65I200.trade_area_id = t.trade_area_id and dn_ACSA65I200.data_item_id = 1847
left join demographic_numvalues dn_X4048_X on dn_X4048_X.trade_area_id = t.trade_area_id and dn_X4048_X.data_item_id = 2797
left join demographic_numvalues dn_HINC_50KPLUS_CY on dn_HINC_50KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_50KPLUS_CY.data_item_id = 2805
left join demographic_numvalues dn_HINC_75KPLUS_CY on dn_HINC_75KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_75KPLUS_CY.data_item_id = 2806
left join demographic_numvalues dn_HINC_100KPLUS on dn_HINC_100KPLUS.trade_area_id = t.trade_area_id and dn_HINC_100KPLUS.data_item_id = 2807
left join demographic_numvalues dn_POP_25PLUS_CY on dn_POP_25PLUS_CY.trade_area_id = t.trade_area_id and dn_POP_25PLUS_CY.data_item_id = 2808
left join demographic_numvalues dn_POP_30PLUS_CY on dn_POP_30PLUS_CY.trade_area_id = t.trade_area_id and dn_POP_30PLUS_CY.data_item_id = 2809
left join demographic_numvalues dn_AGG_INCOME on dn_AGG_INCOME.trade_area_id = t.trade_area_id and dn_AGG_INCOME.data_item_id = 2810