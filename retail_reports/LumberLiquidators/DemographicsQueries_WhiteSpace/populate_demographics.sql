use LL_OCT13_CMA_100213
go

declare @threshold_id int = 1

insert into [demographics_denorm] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
	TOTPOP_CY,
TOTHH_CY,
OWNER_CY,
RENTER_CY,
PCI_CY,
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
HINC_50KPLUS_CY,
HINC_75KPLUS_CY,
AGG_INCOME,
TOTHU_CY,
VACANT_CY,
X3025_X)

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
dn_PCI_CY.value as PCI_CY,
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
dn_HINC_50KPLUS_CY.value as HINC_50KPLUS_CY,
dn_HINC_75KPLUS_CY.value as HINC_75KPLUS_CY,
dn_AGG_INCOME.value as AGG_INCOME,
dn_TOTHU_CY.value as TOTHU_CY,
dn_VACANT_CY.value as VACANT_CY,
dn_X3025_X.value as X3025_X
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13
left join demographic_numvalues dn_TOTHH_CY on dn_TOTHH_CY.trade_area_id = t.trade_area_id and dn_TOTHH_CY.data_item_id = 16
left join demographic_numvalues dn_OWNER_CY on dn_OWNER_CY.trade_area_id = t.trade_area_id and dn_OWNER_CY.data_item_id = 25
left join demographic_numvalues dn_RENTER_CY on dn_RENTER_CY.trade_area_id = t.trade_area_id and dn_RENTER_CY.data_item_id = 28
left join demographic_numvalues dn_PCI_CY on dn_PCI_CY.trade_area_id = t.trade_area_id and dn_PCI_CY.data_item_id = 88
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
left join demographic_numvalues dn_HINC_50KPLUS_CY on dn_HINC_50KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_50KPLUS_CY.data_item_id = 2805
left join demographic_numvalues dn_HINC_75KPLUS_CY on dn_HINC_75KPLUS_CY.trade_area_id = t.trade_area_id and dn_HINC_75KPLUS_CY.data_item_id = 2806
left join demographic_numvalues dn_AGG_INCOME on dn_AGG_INCOME.trade_area_id = t.trade_area_id and dn_AGG_INCOME.data_item_id = 2810
left join demographic_numvalues dn_TOTHU_CY on dn_TOTHU_CY.trade_area_id = t.trade_area_id and dn_TOTHU_CY.data_item_id = 2846
left join demographic_numvalues dn_VACANT_CY on dn_VACANT_CY.trade_area_id = t.trade_area_id and dn_VACANT_CY.data_item_id = 2849
left join demographic_numvalues dn_X3025_X on dn_X3025_X.trade_area_id = t.trade_area_id and dn_X3025_X.data_item_id = 2878