use TTS_JUL13_CMA_070913
go

declare @threshold_id int = 1

insert into [demographics_denorm] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
	TOTPOP_CY,
TOTHH_CY,
OWNER_CY,
RENTER_CY,
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
WHITE_CY,
BLACK_CY,
AMERIND_CY,
ASIAN_CY,
PACIFIC_CY,
OTHRACE_CY,
RACE2UP_CY,
HISPPOPCY,
ACSUNT1DET,
ACSUNT1ATT,
ACSUNT2,
ACSUNT3,
ACSUNT5,
ACSUNT10,
ACSUNT20,
ACSUNT50UP,
ACSUNTMOB,
ACSUNTOTH,
ACSBLT2005,
ACSBLT2000,
ACSBLT1990,
ACSBLT1980,
ACSBLT1970,
ACSBLT1960,
ACSBLT1950,
ACSBLT1940,
ACSBLT1939,
ACSOMV2005,
ACSOMV2000,
ACSOMV1990,
ACSOMV1980,
ACSOMV1970,
ACSOMV1969,
ACSRMV2005,
ACSRMV2000,
ACSRMV1990,
ACSRMV1980,
ACSRMV1970,
ACSRMV1969,
ACSOCCBASE,
ACSA15I0,
ACSA15I10,
ACSA15I15,
ACSA15I20,
ACSA15I25,
ACSA15I30,
ACSA15I35,
ACSA15I40,
ACSA15I45,
ACSA15I50,
ACSA15I60,
ACSA15I75,
ACSA15I100,
ACSA15I125,
ACSA15I150,
ACSA15I200,
ACSA25I0,
ACSA25I10,
ACSA25I15,
ACSA25I20,
ACSA25I25,
ACSA25I30,
ACSA25I35,
ACSA25I40,
ACSA25I45,
ACSA25I50,
ACSA25I60,
ACSA25I75,
ACSA25I100,
ACSA25I125,
ACSA25I150,
ACSA25I200,
ACSA45I0,
ACSA45I10,
ACSA45I15,
ACSA45I20,
ACSA45I25,
ACSA45I30,
ACSA45I35,
ACSA45I40,
ACSA45I45,
ACSA45I50,
ACSA45I60,
ACSA45I75,
ACSA45I100,
ACSA45I125,
ACSA45I150,
ACSA45I200,
ACSA65I0,
ACSA65I10,
ACSA65I15,
ACSA65I20,
ACSA65I25,
ACSA65I30,
ACSA65I35,
ACSA65I40,
ACSA65I45,
ACSA65I50,
ACSA65I60,
ACSA65I75,
ACSA65I100,
ACSA65I125,
ACSA65I150,
ACSA65I200,
X3019_X,
X4057_X,
X4060_X,
X4080_X,
HINC_50KPLUS_CY,
HINC_75KPLUS_CY,
HINC_100KPLUS,
AGG_INCOME,
TOTHU_CY,
VACANT_CY,
X4082_X,
X4084_X,
X4085_X,
X4095_X,
X4096_X,
X4011_X,
X4012_X,
X4013_X,
X3025_X,
X3041_X,
X3047_X,
X3048_X,
HI_PROD_PROXY_CY)

select
	c.name as company_name,
	s.store_id,
	s.assumed_opened_date,
	s.assumed_closed_date,
	t.trade_area_id,
	dn_TOTPOP_CY.value as TOTPOP_CY,
dn_TOTHH_CY.value as TOTHH_CY,
dn_OWNER_CY.value as OWNER_CY,
dn_RENTER_CY.value as RENTER_CY,
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
dn_WHITE_CY.value as WHITE_CY,
dn_BLACK_CY.value as BLACK_CY,
dn_AMERIND_CY.value as AMERIND_CY,
dn_ASIAN_CY.value as ASIAN_CY,
dn_PACIFIC_CY.value as PACIFIC_CY,
dn_OTHRACE_CY.value as OTHRACE_CY,
dn_RACE2UP_CY.value as RACE2UP_CY,
dn_HISPPOPCY.value as HISPPOPCY,
dn_ACSUNT1DET.value as ACSUNT1DET,
dn_ACSUNT1ATT.value as ACSUNT1ATT,
dn_ACSUNT2.value as ACSUNT2,
dn_ACSUNT3.value as ACSUNT3,
dn_ACSUNT5.value as ACSUNT5,
dn_ACSUNT10.value as ACSUNT10,
dn_ACSUNT20.value as ACSUNT20,
dn_ACSUNT50UP.value as ACSUNT50UP,
dn_ACSUNTMOB.value as ACSUNTMOB,
dn_ACSUNTOTH.value as ACSUNTOTH,
dn_ACSBLT2005.value as ACSBLT2005,
dn_ACSBLT2000.value as ACSBLT2000,
dn_ACSBLT1990.value as ACSBLT1990,
dn_ACSBLT1980.value as ACSBLT1980,
dn_ACSBLT1970.value as ACSBLT1970,
dn_ACSBLT1960.value as ACSBLT1960,
dn_ACSBLT1950.value as ACSBLT1950,
dn_ACSBLT1940.value as ACSBLT1940,
dn_ACSBLT1939.value as ACSBLT1939,
dn_ACSOMV2005.value as ACSOMV2005,
dn_ACSOMV2000.value as ACSOMV2000,
dn_ACSOMV1990.value as ACSOMV1990,
dn_ACSOMV1980.value as ACSOMV1980,
dn_ACSOMV1970.value as ACSOMV1970,
dn_ACSOMV1969.value as ACSOMV1969,
dn_ACSRMV2005.value as ACSRMV2005,
dn_ACSRMV2000.value as ACSRMV2000,
dn_ACSRMV1990.value as ACSRMV1990,
dn_ACSRMV1980.value as ACSRMV1980,
dn_ACSRMV1970.value as ACSRMV1970,
dn_ACSRMV1969.value as ACSRMV1969,
dn_ACSOCCBASE.value as ACSOCCBASE,
dn_ACSA15I0.value as ACSA15I0,
dn_ACSA15I10.value as ACSA15I10,
dn_ACSA15I15.value as ACSA15I15,
dn_ACSA15I20.value as ACSA15I20,
dn_ACSA15I25.value as ACSA15I25,
dn_ACSA15I30.value as ACSA15I30,
dn_ACSA15I35.value as ACSA15I35,
dn_ACSA15I40.value as ACSA15I40,
dn_ACSA15I45.value as ACSA15I45,
dn_ACSA15I50.value as ACSA15I50,
dn_ACSA15I60.value as ACSA15I60,
dn_ACSA15I75.value as ACSA15I75,
dn_ACSA15I100.value as ACSA15I100,
dn_ACSA15I125.value as ACSA15I125,
dn_ACSA15I150.value as ACSA15I150,
dn_ACSA15I200.value as ACSA15I200,
dn_ACSA25I0.value as ACSA25I0,
dn_ACSA25I10.value as ACSA25I10,
dn_ACSA25I15.value as ACSA25I15,
dn_ACSA25I20.value as ACSA25I20,
dn_ACSA25I25.value as ACSA25I25,
dn_ACSA25I30.value as ACSA25I30,
dn_ACSA25I35.value as ACSA25I35,
dn_ACSA25I40.value as ACSA25I40,
dn_ACSA25I45.value as ACSA25I45,
dn_ACSA25I50.value as ACSA25I50,
dn_ACSA25I60.value as ACSA25I60,
dn_ACSA25I75.value as ACSA25I75,
dn_ACSA25I100.value as ACSA25I100,
dn_ACSA25I125.value as ACSA25I125,
dn_ACSA25I150.value as ACSA25I150,
dn_ACSA25I200.value as ACSA25I200,
dn_ACSA45I0.value as ACSA45I0,
dn_ACSA45I10.value as ACSA45I10,
dn_ACSA45I15.value as ACSA45I15,
dn_ACSA45I20.value as ACSA45I20,
dn_ACSA45I25.value as ACSA45I25,
dn_ACSA45I30.value as ACSA45I30,
dn_ACSA45I35.value as ACSA45I35,
dn_ACSA45I40.value as ACSA45I40,
dn_ACSA45I45.value as ACSA45I45,
dn_ACSA45I50.value as ACSA45I50,
dn_ACSA45I60.value as ACSA45I60,
dn_ACSA45I75.value as ACSA45I75,
dn_ACSA45I100.value as ACSA45I100,
dn_ACSA45I125.value as ACSA45I125,
dn_ACSA45I150.value as ACSA45I150,
dn_ACSA45I200.value as ACSA45I200,
dn_ACSA65I0.value as ACSA65I0,
dn_ACSA65I10.value as ACSA65I10,
dn_ACSA65I15.value as ACSA65I15,
dn_ACSA65I20.value as ACSA65I20,
dn_ACSA65I25.value as ACSA65I25,
dn_ACSA65I30.value as ACSA65I30,
dn_ACSA65I35.value as ACSA65I35,
dn_ACSA65I40.value as ACSA65I40,
dn_ACSA65I45.value as ACSA65I45,
dn_ACSA65I50.value as ACSA65I50,
dn_ACSA65I60.value as ACSA65I60,
dn_ACSA65I75.value as ACSA65I75,
dn_ACSA65I100.value as ACSA65I100,
dn_ACSA65I125.value as ACSA65I125,
dn_ACSA65I150.value as ACSA65I150,
dn_ACSA65I200.value as ACSA65I200,
dn_X3019_X.value as X3019_X,
dn_X4057_X.value as X4057_X,
dn_X4060_X.value as X4060_X,
dn_X4080_X.value as X4080_X,
dn_HINC_50KPLUS_CY.value as HINC_50KPLUS_CY,
dn_HINC_75KPLUS_CY.value as HINC_75KPLUS_CY,
dn_HINC_100KPLUS.value as HINC_100KPLUS,
dn_AGG_INCOME.value as AGG_INCOME,
dn_TOTHU_CY.value as TOTHU_CY,
dn_VACANT_CY.value as VACANT_CY,
dn_X4082_X.value as X4082_X,
dn_X4084_X.value as X4084_X,
dn_X4085_X.value as X4085_X,
dn_X4095_X.value as X4095_X,
dn_X4096_X.value as X4096_X,
dn_X4011_X.value as X4011_X,
dn_X4012_X.value as X4012_X,
dn_X4013_X.value as X4013_X,
dn_X3025_X.value as X3025_X,
dn_X3041_X.value as X3041_X,
dn_X3047_X.value as X3047_X,
dn_X3048_X.value as X3048_X,
dn_HI_PROD_PROXY_CY.value as HI_PROD_PROXY_CY
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13
left join demographic_numvalues dn_TOTHH_CY on dn_TOTHH_CY.trade_area_id = t.trade_area_id and dn_TOTHH_CY.data_item_id = 16
left join demographic_numvalues dn_OWNER_CY on dn_OWNER_CY.trade_area_id = t.trade_area_id and dn_OWNER_CY.data_item_id = 25
left join demographic_numvalues dn_RENTER_CY on dn_RENTER_CY.trade_area_id = t.trade_area_id and dn_RENTER_CY.data_item_id = 28
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
left join demographic_numvalues dn_WHITE_CY on dn_WHITE_CY.trade_area_id = t.trade_area_id and dn_WHITE_CY.data_item_id = 164
left join demographic_numvalues dn_BLACK_CY on dn_BLACK_CY.trade_area_id = t.trade_area_id and dn_BLACK_CY.data_item_id = 170
left join demographic_numvalues dn_AMERIND_CY on dn_AMERIND_CY.trade_area_id = t.trade_area_id and dn_AMERIND_CY.data_item_id = 176
left join demographic_numvalues dn_ASIAN_CY on dn_ASIAN_CY.trade_area_id = t.trade_area_id and dn_ASIAN_CY.data_item_id = 182
left join demographic_numvalues dn_PACIFIC_CY on dn_PACIFIC_CY.trade_area_id = t.trade_area_id and dn_PACIFIC_CY.data_item_id = 188
left join demographic_numvalues dn_OTHRACE_CY on dn_OTHRACE_CY.trade_area_id = t.trade_area_id and dn_OTHRACE_CY.data_item_id = 194
left join demographic_numvalues dn_RACE2UP_CY on dn_RACE2UP_CY.trade_area_id = t.trade_area_id and dn_RACE2UP_CY.data_item_id = 200
left join demographic_numvalues dn_HISPPOPCY on dn_HISPPOPCY.trade_area_id = t.trade_area_id and dn_HISPPOPCY.data_item_id = 206
left join demographic_numvalues dn_ACSUNT1DET on dn_ACSUNT1DET.trade_area_id = t.trade_area_id and dn_ACSUNT1DET.data_item_id = 465
left join demographic_numvalues dn_ACSUNT1ATT on dn_ACSUNT1ATT.trade_area_id = t.trade_area_id and dn_ACSUNT1ATT.data_item_id = 468
left join demographic_numvalues dn_ACSUNT2 on dn_ACSUNT2.trade_area_id = t.trade_area_id and dn_ACSUNT2.data_item_id = 471
left join demographic_numvalues dn_ACSUNT3 on dn_ACSUNT3.trade_area_id = t.trade_area_id and dn_ACSUNT3.data_item_id = 474
left join demographic_numvalues dn_ACSUNT5 on dn_ACSUNT5.trade_area_id = t.trade_area_id and dn_ACSUNT5.data_item_id = 477
left join demographic_numvalues dn_ACSUNT10 on dn_ACSUNT10.trade_area_id = t.trade_area_id and dn_ACSUNT10.data_item_id = 480
left join demographic_numvalues dn_ACSUNT20 on dn_ACSUNT20.trade_area_id = t.trade_area_id and dn_ACSUNT20.data_item_id = 483
left join demographic_numvalues dn_ACSUNT50UP on dn_ACSUNT50UP.trade_area_id = t.trade_area_id and dn_ACSUNT50UP.data_item_id = 486
left join demographic_numvalues dn_ACSUNTMOB on dn_ACSUNTMOB.trade_area_id = t.trade_area_id and dn_ACSUNTMOB.data_item_id = 489
left join demographic_numvalues dn_ACSUNTOTH on dn_ACSUNTOTH.trade_area_id = t.trade_area_id and dn_ACSUNTOTH.data_item_id = 492
left join demographic_numvalues dn_ACSBLT2005 on dn_ACSBLT2005.trade_area_id = t.trade_area_id and dn_ACSBLT2005.data_item_id = 498
left join demographic_numvalues dn_ACSBLT2000 on dn_ACSBLT2000.trade_area_id = t.trade_area_id and dn_ACSBLT2000.data_item_id = 501
left join demographic_numvalues dn_ACSBLT1990 on dn_ACSBLT1990.trade_area_id = t.trade_area_id and dn_ACSBLT1990.data_item_id = 504
left join demographic_numvalues dn_ACSBLT1980 on dn_ACSBLT1980.trade_area_id = t.trade_area_id and dn_ACSBLT1980.data_item_id = 507
left join demographic_numvalues dn_ACSBLT1970 on dn_ACSBLT1970.trade_area_id = t.trade_area_id and dn_ACSBLT1970.data_item_id = 510
left join demographic_numvalues dn_ACSBLT1960 on dn_ACSBLT1960.trade_area_id = t.trade_area_id and dn_ACSBLT1960.data_item_id = 513
left join demographic_numvalues dn_ACSBLT1950 on dn_ACSBLT1950.trade_area_id = t.trade_area_id and dn_ACSBLT1950.data_item_id = 516
left join demographic_numvalues dn_ACSBLT1940 on dn_ACSBLT1940.trade_area_id = t.trade_area_id and dn_ACSBLT1940.data_item_id = 519
left join demographic_numvalues dn_ACSBLT1939 on dn_ACSBLT1939.trade_area_id = t.trade_area_id and dn_ACSBLT1939.data_item_id = 522
left join demographic_numvalues dn_ACSOMV2005 on dn_ACSOMV2005.trade_area_id = t.trade_area_id and dn_ACSOMV2005.data_item_id = 531
left join demographic_numvalues dn_ACSOMV2000 on dn_ACSOMV2000.trade_area_id = t.trade_area_id and dn_ACSOMV2000.data_item_id = 534
left join demographic_numvalues dn_ACSOMV1990 on dn_ACSOMV1990.trade_area_id = t.trade_area_id and dn_ACSOMV1990.data_item_id = 537
left join demographic_numvalues dn_ACSOMV1980 on dn_ACSOMV1980.trade_area_id = t.trade_area_id and dn_ACSOMV1980.data_item_id = 540
left join demographic_numvalues dn_ACSOMV1970 on dn_ACSOMV1970.trade_area_id = t.trade_area_id and dn_ACSOMV1970.data_item_id = 543
left join demographic_numvalues dn_ACSOMV1969 on dn_ACSOMV1969.trade_area_id = t.trade_area_id and dn_ACSOMV1969.data_item_id = 546
left join demographic_numvalues dn_ACSRMV2005 on dn_ACSRMV2005.trade_area_id = t.trade_area_id and dn_ACSRMV2005.data_item_id = 549
left join demographic_numvalues dn_ACSRMV2000 on dn_ACSRMV2000.trade_area_id = t.trade_area_id and dn_ACSRMV2000.data_item_id = 552
left join demographic_numvalues dn_ACSRMV1990 on dn_ACSRMV1990.trade_area_id = t.trade_area_id and dn_ACSRMV1990.data_item_id = 555
left join demographic_numvalues dn_ACSRMV1980 on dn_ACSRMV1980.trade_area_id = t.trade_area_id and dn_ACSRMV1980.data_item_id = 558
left join demographic_numvalues dn_ACSRMV1970 on dn_ACSRMV1970.trade_area_id = t.trade_area_id and dn_ACSRMV1970.data_item_id = 561
left join demographic_numvalues dn_ACSRMV1969 on dn_ACSRMV1969.trade_area_id = t.trade_area_id and dn_ACSRMV1969.data_item_id = 564
left join demographic_numvalues dn_ACSOCCBASE on dn_ACSOCCBASE.trade_area_id = t.trade_area_id and dn_ACSOCCBASE.data_item_id = 1334
left join demographic_numvalues dn_ACSA15I0 on dn_ACSA15I0.trade_area_id = t.trade_area_id and dn_ACSA15I0.data_item_id = 1631
left join demographic_numvalues dn_ACSA15I10 on dn_ACSA15I10.trade_area_id = t.trade_area_id and dn_ACSA15I10.data_item_id = 1634
left join demographic_numvalues dn_ACSA15I15 on dn_ACSA15I15.trade_area_id = t.trade_area_id and dn_ACSA15I15.data_item_id = 1637
left join demographic_numvalues dn_ACSA15I20 on dn_ACSA15I20.trade_area_id = t.trade_area_id and dn_ACSA15I20.data_item_id = 1640
left join demographic_numvalues dn_ACSA15I25 on dn_ACSA15I25.trade_area_id = t.trade_area_id and dn_ACSA15I25.data_item_id = 1643
left join demographic_numvalues dn_ACSA15I30 on dn_ACSA15I30.trade_area_id = t.trade_area_id and dn_ACSA15I30.data_item_id = 1646
left join demographic_numvalues dn_ACSA15I35 on dn_ACSA15I35.trade_area_id = t.trade_area_id and dn_ACSA15I35.data_item_id = 1649
left join demographic_numvalues dn_ACSA15I40 on dn_ACSA15I40.trade_area_id = t.trade_area_id and dn_ACSA15I40.data_item_id = 1652
left join demographic_numvalues dn_ACSA15I45 on dn_ACSA15I45.trade_area_id = t.trade_area_id and dn_ACSA15I45.data_item_id = 1655
left join demographic_numvalues dn_ACSA15I50 on dn_ACSA15I50.trade_area_id = t.trade_area_id and dn_ACSA15I50.data_item_id = 1658
left join demographic_numvalues dn_ACSA15I60 on dn_ACSA15I60.trade_area_id = t.trade_area_id and dn_ACSA15I60.data_item_id = 1661
left join demographic_numvalues dn_ACSA15I75 on dn_ACSA15I75.trade_area_id = t.trade_area_id and dn_ACSA15I75.data_item_id = 1664
left join demographic_numvalues dn_ACSA15I100 on dn_ACSA15I100.trade_area_id = t.trade_area_id and dn_ACSA15I100.data_item_id = 1667
left join demographic_numvalues dn_ACSA15I125 on dn_ACSA15I125.trade_area_id = t.trade_area_id and dn_ACSA15I125.data_item_id = 1670
left join demographic_numvalues dn_ACSA15I150 on dn_ACSA15I150.trade_area_id = t.trade_area_id and dn_ACSA15I150.data_item_id = 1673
left join demographic_numvalues dn_ACSA15I200 on dn_ACSA15I200.trade_area_id = t.trade_area_id and dn_ACSA15I200.data_item_id = 1676
left join demographic_numvalues dn_ACSA25I0 on dn_ACSA25I0.trade_area_id = t.trade_area_id and dn_ACSA25I0.data_item_id = 1688
left join demographic_numvalues dn_ACSA25I10 on dn_ACSA25I10.trade_area_id = t.trade_area_id and dn_ACSA25I10.data_item_id = 1691
left join demographic_numvalues dn_ACSA25I15 on dn_ACSA25I15.trade_area_id = t.trade_area_id and dn_ACSA25I15.data_item_id = 1694
left join demographic_numvalues dn_ACSA25I20 on dn_ACSA25I20.trade_area_id = t.trade_area_id and dn_ACSA25I20.data_item_id = 1697
left join demographic_numvalues dn_ACSA25I25 on dn_ACSA25I25.trade_area_id = t.trade_area_id and dn_ACSA25I25.data_item_id = 1700
left join demographic_numvalues dn_ACSA25I30 on dn_ACSA25I30.trade_area_id = t.trade_area_id and dn_ACSA25I30.data_item_id = 1703
left join demographic_numvalues dn_ACSA25I35 on dn_ACSA25I35.trade_area_id = t.trade_area_id and dn_ACSA25I35.data_item_id = 1706
left join demographic_numvalues dn_ACSA25I40 on dn_ACSA25I40.trade_area_id = t.trade_area_id and dn_ACSA25I40.data_item_id = 1709
left join demographic_numvalues dn_ACSA25I45 on dn_ACSA25I45.trade_area_id = t.trade_area_id and dn_ACSA25I45.data_item_id = 1712
left join demographic_numvalues dn_ACSA25I50 on dn_ACSA25I50.trade_area_id = t.trade_area_id and dn_ACSA25I50.data_item_id = 1715
left join demographic_numvalues dn_ACSA25I60 on dn_ACSA25I60.trade_area_id = t.trade_area_id and dn_ACSA25I60.data_item_id = 1718
left join demographic_numvalues dn_ACSA25I75 on dn_ACSA25I75.trade_area_id = t.trade_area_id and dn_ACSA25I75.data_item_id = 1721
left join demographic_numvalues dn_ACSA25I100 on dn_ACSA25I100.trade_area_id = t.trade_area_id and dn_ACSA25I100.data_item_id = 1724
left join demographic_numvalues dn_ACSA25I125 on dn_ACSA25I125.trade_area_id = t.trade_area_id and dn_ACSA25I125.data_item_id = 1727
left join demographic_numvalues dn_ACSA25I150 on dn_ACSA25I150.trade_area_id = t.trade_area_id and dn_ACSA25I150.data_item_id = 1730
left join demographic_numvalues dn_ACSA25I200 on dn_ACSA25I200.trade_area_id = t.trade_area_id and dn_ACSA25I200.data_item_id = 1733
left join demographic_numvalues dn_ACSA45I0 on dn_ACSA45I0.trade_area_id = t.trade_area_id and dn_ACSA45I0.data_item_id = 1745
left join demographic_numvalues dn_ACSA45I10 on dn_ACSA45I10.trade_area_id = t.trade_area_id and dn_ACSA45I10.data_item_id = 1748
left join demographic_numvalues dn_ACSA45I15 on dn_ACSA45I15.trade_area_id = t.trade_area_id and dn_ACSA45I15.data_item_id = 1751
left join demographic_numvalues dn_ACSA45I20 on dn_ACSA45I20.trade_area_id = t.trade_area_id and dn_ACSA45I20.data_item_id = 1754
left join demographic_numvalues dn_ACSA45I25 on dn_ACSA45I25.trade_area_id = t.trade_area_id and dn_ACSA45I25.data_item_id = 1757
left join demographic_numvalues dn_ACSA45I30 on dn_ACSA45I30.trade_area_id = t.trade_area_id and dn_ACSA45I30.data_item_id = 1760
left join demographic_numvalues dn_ACSA45I35 on dn_ACSA45I35.trade_area_id = t.trade_area_id and dn_ACSA45I35.data_item_id = 1763
left join demographic_numvalues dn_ACSA45I40 on dn_ACSA45I40.trade_area_id = t.trade_area_id and dn_ACSA45I40.data_item_id = 1766
left join demographic_numvalues dn_ACSA45I45 on dn_ACSA45I45.trade_area_id = t.trade_area_id and dn_ACSA45I45.data_item_id = 1769
left join demographic_numvalues dn_ACSA45I50 on dn_ACSA45I50.trade_area_id = t.trade_area_id and dn_ACSA45I50.data_item_id = 1772
left join demographic_numvalues dn_ACSA45I60 on dn_ACSA45I60.trade_area_id = t.trade_area_id and dn_ACSA45I60.data_item_id = 1775
left join demographic_numvalues dn_ACSA45I75 on dn_ACSA45I75.trade_area_id = t.trade_area_id and dn_ACSA45I75.data_item_id = 1778
left join demographic_numvalues dn_ACSA45I100 on dn_ACSA45I100.trade_area_id = t.trade_area_id and dn_ACSA45I100.data_item_id = 1781
left join demographic_numvalues dn_ACSA45I125 on dn_ACSA45I125.trade_area_id = t.trade_area_id and dn_ACSA45I125.data_item_id = 1784
left join demographic_numvalues dn_ACSA45I150 on dn_ACSA45I150.trade_area_id = t.trade_area_id and dn_ACSA45I150.data_item_id = 1787
left join demographic_numvalues dn_ACSA45I200 on dn_ACSA45I200.trade_area_id = t.trade_area_id and dn_ACSA45I200.data_item_id = 1790
left join demographic_numvalues dn_ACSA65I0 on dn_ACSA65I0.trade_area_id = t.trade_area_id and dn_ACSA65I0.data_item_id = 1802
left join demographic_numvalues dn_ACSA65I10 on dn_ACSA65I10.trade_area_id = t.trade_area_id and dn_ACSA65I10.data_item_id = 1805
left join demographic_numvalues dn_ACSA65I15 on dn_ACSA65I15.trade_area_id = t.trade_area_id and dn_ACSA65I15.data_item_id = 1808
left join demographic_numvalues dn_ACSA65I20 on dn_ACSA65I20.trade_area_id = t.trade_area_id and dn_ACSA65I20.data_item_id = 1811
left join demographic_numvalues dn_ACSA65I25 on dn_ACSA65I25.trade_area_id = t.trade_area_id and dn_ACSA65I25.data_item_id = 1814
left join demographic_numvalues dn_ACSA65I30 on dn_ACSA65I30.trade_area_id = t.trade_area_id and dn_ACSA65I30.data_item_id = 1817
left join demographic_numvalues dn_ACSA65I35 on dn_ACSA65I35.trade_area_id = t.trade_area_id and dn_ACSA65I35.data_item_id = 1820
left join demographic_numvalues dn_ACSA65I40 on dn_ACSA65I40.trade_area_id = t.trade_area_id and dn_ACSA65I40.data_item_id = 1823
left join demographic_numvalues dn_ACSA65I45 on dn_ACSA65I45.trade_area_id = t.trade_area_id and dn_ACSA65I45.data_item_id = 1826
left join demographic_numvalues dn_ACSA65I50 on dn_ACSA65I50.trade_area_id = t.trade_area_id and dn_ACSA65I50.data_item_id = 1829
left join demographic_numvalues dn_ACSA65I60 on dn_ACSA65I60.trade_area_id = t.trade_area_id and dn_ACSA65I60.data_item_id = 1832
left join demographic_numvalues dn_ACSA65I75 on dn_ACSA65I75.trade_area_id = t.trade_area_id and dn_ACSA65I75.data_item_id = 1835
left join demographic_numvalues dn_ACSA65I100 on dn_ACSA65I100.trade_area_id = t.trade_area_id and dn_ACSA65I100.data_item_id = 1838
left join demographic_numvalues dn_ACSA65I125 on dn_ACSA65I125.trade_area_id = t.trade_area_id and dn_ACSA65I125.data_item_id = 1841
left join demographic_numvalues dn_ACSA65I150 on dn_ACSA65I150.trade_area_id = t.trade_area_id and dn_ACSA65I150.data_item_id = 1844
left join demographic_numvalues dn_ACSA65I200 on dn_ACSA65I200.trade_area_id = t.trade_area_id and dn_ACSA65I200.data_item_id = 1847
left join demographic_numvalues dn_X3019_X on dn_X3019_X.trade_area_id = t.trade_area_id and dn_X3019_X.data_item_id = 2607
left join demographic_numvalues dn_X4057_X on dn_X4057_X.trade_area_id = t.trade_area_id and dn_X4057_X.data_item_id = 2619
left join demographic_numvalues dn_X4060_X on dn_X4060_X.trade_area_id = t.trade_area_id and dn_X4060_X.data_item_id = 2622
left join demographic_numvalues dn_X4080_X on dn_X4080_X.trade_area_id = t.trade_area_id and dn_X4080_X.data_item_id = 2628
left join demographic_numvalues dn_HINC_50KPLUS_CY on dn_HINC_50KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_50KPLUS_CY.data_item_id = 2805
left join demographic_numvalues dn_HINC_75KPLUS_CY on dn_HINC_75KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_75KPLUS_CY.data_item_id = 2806
left join demographic_numvalues dn_HINC_100KPLUS on dn_HINC_100KPLUS.trade_area_id = t.trade_area_id and dn_HINC_100KPLUS.data_item_id = 2807
left join demographic_numvalues dn_AGG_INCOME on dn_AGG_INCOME.trade_area_id = t.trade_area_id and dn_AGG_INCOME.data_item_id = 2810
left join demographic_numvalues dn_TOTHU_CY on dn_TOTHU_CY.trade_area_id = t.trade_area_id and dn_TOTHU_CY.data_item_id = 2846
left join demographic_numvalues dn_VACANT_CY on dn_VACANT_CY.trade_area_id = t.trade_area_id and dn_VACANT_CY.data_item_id = 2849
left join demographic_numvalues dn_X4082_X on dn_X4082_X.trade_area_id = t.trade_area_id and dn_X4082_X.data_item_id = 2869
left join demographic_numvalues dn_X4084_X on dn_X4084_X.trade_area_id = t.trade_area_id and dn_X4084_X.data_item_id = 2870
left join demographic_numvalues dn_X4085_X on dn_X4085_X.trade_area_id = t.trade_area_id and dn_X4085_X.data_item_id = 2871
left join demographic_numvalues dn_X4095_X on dn_X4095_X.trade_area_id = t.trade_area_id and dn_X4095_X.data_item_id = 2872
left join demographic_numvalues dn_X4096_X on dn_X4096_X.trade_area_id = t.trade_area_id and dn_X4096_X.data_item_id = 2873
left join demographic_numvalues dn_X4011_X on dn_X4011_X.trade_area_id = t.trade_area_id and dn_X4011_X.data_item_id = 2874
left join demographic_numvalues dn_X4012_X on dn_X4012_X.trade_area_id = t.trade_area_id and dn_X4012_X.data_item_id = 2875
left join demographic_numvalues dn_X4013_X on dn_X4013_X.trade_area_id = t.trade_area_id and dn_X4013_X.data_item_id = 2876
left join demographic_numvalues dn_X3025_X on dn_X3025_X.trade_area_id = t.trade_area_id and dn_X3025_X.data_item_id = 2878
left join demographic_numvalues dn_X3041_X on dn_X3041_X.trade_area_id = t.trade_area_id and dn_X3041_X.data_item_id = 2879
left join demographic_numvalues dn_X3047_X on dn_X3047_X.trade_area_id = t.trade_area_id and dn_X3047_X.data_item_id = 2880
left join demographic_numvalues dn_X3048_X on dn_X3048_X.trade_area_id = t.trade_area_id and dn_X3048_X.data_item_id = 2881
left join demographic_numvalues dn_HI_PROD_PROXY_CY on dn_HI_PROD_PROXY_CY.trade_area_id = t.trade_area_id and dn_HI_PROD_PROXY_CY.data_item_id = 2887