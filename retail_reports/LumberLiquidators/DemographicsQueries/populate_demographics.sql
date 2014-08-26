use LL_OCT13_CMA_100213
go

declare @threshold_id int = 1
--select distinct threshold_id from trade_areas


insert into [demographics_denorm] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
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
MEDHINC_CY,
AVGHINC_CY,
PCI_CY,
WHITE_CY,
BLACK_CY,
AMERIND_CY,
ASIAN_CY,
PACIFIC_CY,
OTHRACE_CY,
RACE2UP_CY,
HISPPOPCY,
ACSTOTPOP,
MOETOTPOP,
ACSTOTHH,
MOETOTHH,
ACSTOTHU,
MOETOTHU,
ACSVALBASE,
MOEVALBASE,
ACSVAL0,
MOEVAL0,
ACSVAL10K,
MOEVAL10K,
ACSVAL15K,
MOEVAL15K,
ACSVAL20K,
MOEVAL20K,
ACSVAL25K,
MOEVAL25K,
ACSVAL30K,
MOEVAL30K,
ACSVAL35K,
MOEVAL35K,
ACSVAL40K,
MOEVAL40K,
ACSVAL50K,
MOEVAL50K,
ACSVAL60K,
MOEVAL60K,
ACSVAL70K,
MOEVAL70K,
ACSVAL80K,
MOEVAL80K,
ACSVAL90K,
MOEVAL90K,
ACSVAL100K,
MOEVAL100K,
ACSVAL125K,
MOEVAL125K,
ACSVAL150K,
MOEVAL150K,
ACSVAL175K,
MOEVAL175K,
ACSVAL200K,
MOEVAL200K,
ACSVAL250K,
MOEVAL250K,
ACSVAL300K,
MOEVAL300K,
ACSVAL400K,
MOEVAL400K,
ACSVAL500K,
MOEVAL500K,
ACSVAL750K,
MOEVAL750K,
ACSVAL1M,
MOEVAL1M,
ACSMEDVAL,
MOEMEDVAL,
[TRIGGER],
ACSAVGVAL,
MOEAVGVAL,
TRIGGER3,
ACSMORTBAS,
MOEMORTBAS,
ACSMORT,
MOEMORT,
ACSM2ONLY,
MOEM2ONLY,
ACSMEQONLY,
MOEMEQONLY,
ACSM2ANDEQ,
MOEM2ANDEQ,
ACSM1ONLY,
MOEM1ONLY,
ACSNOMORT,
MOENOMORT,
ACSAVGVALM,
MOEAVGVALM,
TRIGGER7,
ACSAVGVALN,
MOEAVGVALN,
TRIGGER6,
ACSCRNTBAS,
MOECRNTBAS,
ACSPAYCRNT,
MOEPAYCRNT,
ACSRNT0,
MOERNT0,
ACSRNT100,
MOERNT100,
ACSRNT150,
MOERNT150,
ACSRNT200,
MOERNT200,
ACSRNT250,
MOERNT250,
ACSRNT300,
MOERNT300,
ACSRNT350,
MOERNT350,
ACSRNT400,
MOERNT400,
ACSRNT450,
MOERNT450,
ACSRNT500,
MOERNT500,
ACSRNT550,
MOERNT550,
ACSRNT600,
MOERNT600,
ACSRNT650,
MOERNT650,
ACSRNT700,
MOERNT700,
ACSRNT750,
MOERNT750,
ACSRNT800,
MOERNT800,
ACSRNT900,
MOERNT900,
ACSRNT1000,
MOERNT1000,
ACSRNT1250,
MOERNT1250,
ACSRNT1500,
MOERNT1500,
ACSRNT2000,
MOERNT2000,
ACSRNTNONE,
MOERNTNONE,
ACSMEDCRNT,
MOEMEDCRNT,
TRIGGER0,
ACSAVGCRNT,
MOEAVGCRNT,
TRIGGER4,
ACSUTLBASE,
MOEUTLBASE,
ACSUTLEXTR,
MOEUTLEXTR,
ACSUTLNRNT,
MOEUTLNRNT,
ACSUNTBASE,
MOEUNTBASE,
ACSUNT1DET,
MOEUNT1DET,
ACSUNT1ATT,
MOEUNT1ATT,
ACSUNT2,
MOEUNT2,
ACSUNT3,
MOEUNT3,
ACSUNT5,
MOEUNT5,
ACSUNT10,
MOEUNT10,
ACSUNT20,
MOEUNT20,
ACSUNT50UP,
MOEUNT50UP,
ACSUNTMOB,
MOEUNTMOB,
ACSUNTOTH,
MOEUNTOTH,
ACSYBLTBAS,
MOEYBLTBAS,
ACSBLT2005,
MOEBLT2005,
ACSBLT2000,
MOEBLT2000,
ACSBLT1990,
MOEBLT1990,
ACSBLT1980,
MOEBLT1980,
ACSBLT1970,
MOEBLT1970,
ACSBLT1960,
MOEBLT1960,
ACSBLT1950,
MOEBLT1950,
ACSBLT1940,
MOEBLT1940,
ACSBLT1939,
MOEBLT1939,
ACSMEDYBLT,
MOEMEDYBLT,
TRIGGER1,
ACSYRMVBAS,
MOEYRMVBAS,
ACSOMV2005,
MOEOMV2005,
ACSOMV2000,
MOEOMV2000,
ACSOMV1990,
MOEOMV1990,
ACSOMV1980,
MOEOMV1980,
ACSOMV1970,
MOEOMV1970,
ACSOMV1969,
MOEOMV1969,
ACSRMV2005,
MOERMV2005,
ACSRMV2000,
MOERMV2000,
ACSRMV1990,
MOERMV1990,
ACSRMV1980,
MOERMV1980,
ACSRMV1970,
MOERMV1970,
ACSRMV1969,
MOERMV1969,
ACSMEDYRMV,
MOEMEDYRMV,
TRIGGER2,
ACSHEATBAS,
MOEHEATBAS,
ACSUTLGAS,
MOEUTLGAS,
ACSLPGAS,
MOELPGAS,
ACSELEC,
MOEELEC,
ACSOILKER,
MOEOILKER,
ACSCOAL,
MOECOAL,
ACSWOOD,
MOEWOOD,
ACSSOLAR,
MOESOLAR,
ACSOTHFUEL,
MOEOTHFUEL,
ACSNOFUEL,
MOENOFUEL,
ACSVEHBASE,
MOEVEHBASE,
ACSOVEH0,
MOEOVEH0,
ACSOVEH1,
MOEOVEH1,
ACSOVEH2,
MOEOVEH2,
ACSOVEH3,
MOEOVEH3,
ACSOVEH4,
MOEOVEH4,
ACSOVEH5UP,
MOEOVEH5UP,
ACSRVEH0,
MOERVEH0,
ACSRVEH1,
MOERVEH1,
ACSRVEH2,
MOERVEH2,
ACSRVEH3,
MOERVEH3,
ACSRVEH4,
MOERVEH4,
ACSRVEH5UP,
MOERVEH5UP,
ACSAVGVEH,
MOEAVGVEH,
TRIGGER5,
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
OOHHR15C10,
OOHHR25C10,
OOHHR35C10,
OOHHR45C10,
OOHHR55C10,
OOHHR65C10,
OOHHR75C10,
OOHHR85C10,
ROHHR15C10,
ROHHR25C10,
ROHHR35C10,
ROHHR45C10,
ROHHR55C10,
ROHHR65C10,
ROHHR75C10,
ROHHR85C10,
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
dn_MEDHINC_CY.value as MEDHINC_CY,
dn_AVGHINC_CY.value as AVGHINC_CY,
dn_PCI_CY.value as PCI_CY,
dn_WHITE_CY.value as WHITE_CY,
dn_BLACK_CY.value as BLACK_CY,
dn_AMERIND_CY.value as AMERIND_CY,
dn_ASIAN_CY.value as ASIAN_CY,
dn_PACIFIC_CY.value as PACIFIC_CY,
dn_OTHRACE_CY.value as OTHRACE_CY,
dn_RACE2UP_CY.value as RACE2UP_CY,
dn_HISPPOPCY.value as HISPPOPCY,
dn_ACSTOTPOP.value as ACSTOTPOP,
dn_MOETOTPOP.value as MOETOTPOP,
dn_ACSTOTHH.value as ACSTOTHH,
dn_MOETOTHH.value as MOETOTHH,
dn_ACSTOTHU.value as ACSTOTHU,
dn_MOETOTHU.value as MOETOTHU,
dn_ACSVALBASE.value as ACSVALBASE,
dn_MOEVALBASE.value as MOEVALBASE,
dn_ACSVAL0.value as ACSVAL0,
dn_MOEVAL0.value as MOEVAL0,
dn_ACSVAL10K.value as ACSVAL10K,
dn_MOEVAL10K.value as MOEVAL10K,
dn_ACSVAL15K.value as ACSVAL15K,
dn_MOEVAL15K.value as MOEVAL15K,
dn_ACSVAL20K.value as ACSVAL20K,
dn_MOEVAL20K.value as MOEVAL20K,
dn_ACSVAL25K.value as ACSVAL25K,
dn_MOEVAL25K.value as MOEVAL25K,
dn_ACSVAL30K.value as ACSVAL30K,
dn_MOEVAL30K.value as MOEVAL30K,
dn_ACSVAL35K.value as ACSVAL35K,
dn_MOEVAL35K.value as MOEVAL35K,
dn_ACSVAL40K.value as ACSVAL40K,
dn_MOEVAL40K.value as MOEVAL40K,
dn_ACSVAL50K.value as ACSVAL50K,
dn_MOEVAL50K.value as MOEVAL50K,
dn_ACSVAL60K.value as ACSVAL60K,
dn_MOEVAL60K.value as MOEVAL60K,
dn_ACSVAL70K.value as ACSVAL70K,
dn_MOEVAL70K.value as MOEVAL70K,
dn_ACSVAL80K.value as ACSVAL80K,
dn_MOEVAL80K.value as MOEVAL80K,
dn_ACSVAL90K.value as ACSVAL90K,
dn_MOEVAL90K.value as MOEVAL90K,
dn_ACSVAL100K.value as ACSVAL100K,
dn_MOEVAL100K.value as MOEVAL100K,
dn_ACSVAL125K.value as ACSVAL125K,
dn_MOEVAL125K.value as MOEVAL125K,
dn_ACSVAL150K.value as ACSVAL150K,
dn_MOEVAL150K.value as MOEVAL150K,
dn_ACSVAL175K.value as ACSVAL175K,
dn_MOEVAL175K.value as MOEVAL175K,
dn_ACSVAL200K.value as ACSVAL200K,
dn_MOEVAL200K.value as MOEVAL200K,
dn_ACSVAL250K.value as ACSVAL250K,
dn_MOEVAL250K.value as MOEVAL250K,
dn_ACSVAL300K.value as ACSVAL300K,
dn_MOEVAL300K.value as MOEVAL300K,
dn_ACSVAL400K.value as ACSVAL400K,
dn_MOEVAL400K.value as MOEVAL400K,
dn_ACSVAL500K.value as ACSVAL500K,
dn_MOEVAL500K.value as MOEVAL500K,
dn_ACSVAL750K.value as ACSVAL750K,
dn_MOEVAL750K.value as MOEVAL750K,
dn_ACSVAL1M.value as ACSVAL1M,
dn_MOEVAL1M.value as MOEVAL1M,
dn_ACSMEDVAL.value as ACSMEDVAL,
dn_MOEMEDVAL.value as MOEMEDVAL,
dn_TRIGGER.value as [TRIGGER],
dn_ACSAVGVAL.value as ACSAVGVAL,
dn_MOEAVGVAL.value as MOEAVGVAL,
dn_TRIGGER3.value as TRIGGER3,
dn_ACSMORTBAS.value as ACSMORTBAS,
dn_MOEMORTBAS.value as MOEMORTBAS,
dn_ACSMORT.value as ACSMORT,
dn_MOEMORT.value as MOEMORT,
dn_ACSM2ONLY.value as ACSM2ONLY,
dn_MOEM2ONLY.value as MOEM2ONLY,
dn_ACSMEQONLY.value as ACSMEQONLY,
dn_MOEMEQONLY.value as MOEMEQONLY,
dn_ACSM2ANDEQ.value as ACSM2ANDEQ,
dn_MOEM2ANDEQ.value as MOEM2ANDEQ,
dn_ACSM1ONLY.value as ACSM1ONLY,
dn_MOEM1ONLY.value as MOEM1ONLY,
dn_ACSNOMORT.value as ACSNOMORT,
dn_MOENOMORT.value as MOENOMORT,
dn_ACSAVGVALM.value as ACSAVGVALM,
dn_MOEAVGVALM.value as MOEAVGVALM,
dn_TRIGGER7.value as TRIGGER7,
dn_ACSAVGVALN.value as ACSAVGVALN,
dn_MOEAVGVALN.value as MOEAVGVALN,
dn_TRIGGER6.value as TRIGGER6,
dn_ACSCRNTBAS.value as ACSCRNTBAS,
dn_MOECRNTBAS.value as MOECRNTBAS,
dn_ACSPAYCRNT.value as ACSPAYCRNT,
dn_MOEPAYCRNT.value as MOEPAYCRNT,
dn_ACSRNT0.value as ACSRNT0,
dn_MOERNT0.value as MOERNT0,
dn_ACSRNT100.value as ACSRNT100,
dn_MOERNT100.value as MOERNT100,
dn_ACSRNT150.value as ACSRNT150,
dn_MOERNT150.value as MOERNT150,
dn_ACSRNT200.value as ACSRNT200,
dn_MOERNT200.value as MOERNT200,
dn_ACSRNT250.value as ACSRNT250,
dn_MOERNT250.value as MOERNT250,
dn_ACSRNT300.value as ACSRNT300,
dn_MOERNT300.value as MOERNT300,
dn_ACSRNT350.value as ACSRNT350,
dn_MOERNT350.value as MOERNT350,
dn_ACSRNT400.value as ACSRNT400,
dn_MOERNT400.value as MOERNT400,
dn_ACSRNT450.value as ACSRNT450,
dn_MOERNT450.value as MOERNT450,
dn_ACSRNT500.value as ACSRNT500,
dn_MOERNT500.value as MOERNT500,
dn_ACSRNT550.value as ACSRNT550,
dn_MOERNT550.value as MOERNT550,
dn_ACSRNT600.value as ACSRNT600,
dn_MOERNT600.value as MOERNT600,
dn_ACSRNT650.value as ACSRNT650,
dn_MOERNT650.value as MOERNT650,
dn_ACSRNT700.value as ACSRNT700,
dn_MOERNT700.value as MOERNT700,
dn_ACSRNT750.value as ACSRNT750,
dn_MOERNT750.value as MOERNT750,
dn_ACSRNT800.value as ACSRNT800,
dn_MOERNT800.value as MOERNT800,
dn_ACSRNT900.value as ACSRNT900,
dn_MOERNT900.value as MOERNT900,
dn_ACSRNT1000.value as ACSRNT1000,
dn_MOERNT1000.value as MOERNT1000,
dn_ACSRNT1250.value as ACSRNT1250,
dn_MOERNT1250.value as MOERNT1250,
dn_ACSRNT1500.value as ACSRNT1500,
dn_MOERNT1500.value as MOERNT1500,
dn_ACSRNT2000.value as ACSRNT2000,
dn_MOERNT2000.value as MOERNT2000,
dn_ACSRNTNONE.value as ACSRNTNONE,
dn_MOERNTNONE.value as MOERNTNONE,
dn_ACSMEDCRNT.value as ACSMEDCRNT,
dn_MOEMEDCRNT.value as MOEMEDCRNT,
dn_TRIGGER0.value as TRIGGER0,
dn_ACSAVGCRNT.value as ACSAVGCRNT,
dn_MOEAVGCRNT.value as MOEAVGCRNT,
dn_TRIGGER4.value as TRIGGER4,
dn_ACSUTLBASE.value as ACSUTLBASE,
dn_MOEUTLBASE.value as MOEUTLBASE,
dn_ACSUTLEXTR.value as ACSUTLEXTR,
dn_MOEUTLEXTR.value as MOEUTLEXTR,
dn_ACSUTLNRNT.value as ACSUTLNRNT,
dn_MOEUTLNRNT.value as MOEUTLNRNT,
dn_ACSUNTBASE.value as ACSUNTBASE,
dn_MOEUNTBASE.value as MOEUNTBASE,
dn_ACSUNT1DET.value as ACSUNT1DET,
dn_MOEUNT1DET.value as MOEUNT1DET,
dn_ACSUNT1ATT.value as ACSUNT1ATT,
dn_MOEUNT1ATT.value as MOEUNT1ATT,
dn_ACSUNT2.value as ACSUNT2,
dn_MOEUNT2.value as MOEUNT2,
dn_ACSUNT3.value as ACSUNT3,
dn_MOEUNT3.value as MOEUNT3,
dn_ACSUNT5.value as ACSUNT5,
dn_MOEUNT5.value as MOEUNT5,
dn_ACSUNT10.value as ACSUNT10,
dn_MOEUNT10.value as MOEUNT10,
dn_ACSUNT20.value as ACSUNT20,
dn_MOEUNT20.value as MOEUNT20,
dn_ACSUNT50UP.value as ACSUNT50UP,
dn_MOEUNT50UP.value as MOEUNT50UP,
dn_ACSUNTMOB.value as ACSUNTMOB,
dn_MOEUNTMOB.value as MOEUNTMOB,
dn_ACSUNTOTH.value as ACSUNTOTH,
dn_MOEUNTOTH.value as MOEUNTOTH,
dn_ACSYBLTBAS.value as ACSYBLTBAS,
dn_MOEYBLTBAS.value as MOEYBLTBAS,
dn_ACSBLT2005.value as ACSBLT2005,
dn_MOEBLT2005.value as MOEBLT2005,
dn_ACSBLT2000.value as ACSBLT2000,
dn_MOEBLT2000.value as MOEBLT2000,
dn_ACSBLT1990.value as ACSBLT1990,
dn_MOEBLT1990.value as MOEBLT1990,
dn_ACSBLT1980.value as ACSBLT1980,
dn_MOEBLT1980.value as MOEBLT1980,
dn_ACSBLT1970.value as ACSBLT1970,
dn_MOEBLT1970.value as MOEBLT1970,
dn_ACSBLT1960.value as ACSBLT1960,
dn_MOEBLT1960.value as MOEBLT1960,
dn_ACSBLT1950.value as ACSBLT1950,
dn_MOEBLT1950.value as MOEBLT1950,
dn_ACSBLT1940.value as ACSBLT1940,
dn_MOEBLT1940.value as MOEBLT1940,
dn_ACSBLT1939.value as ACSBLT1939,
dn_MOEBLT1939.value as MOEBLT1939,
dn_ACSMEDYBLT.value as ACSMEDYBLT,
dn_MOEMEDYBLT.value as MOEMEDYBLT,
dn_TRIGGER1.value as TRIGGER1,
dn_ACSYRMVBAS.value as ACSYRMVBAS,
dn_MOEYRMVBAS.value as MOEYRMVBAS,
dn_ACSOMV2005.value as ACSOMV2005,
dn_MOEOMV2005.value as MOEOMV2005,
dn_ACSOMV2000.value as ACSOMV2000,
dn_MOEOMV2000.value as MOEOMV2000,
dn_ACSOMV1990.value as ACSOMV1990,
dn_MOEOMV1990.value as MOEOMV1990,
dn_ACSOMV1980.value as ACSOMV1980,
dn_MOEOMV1980.value as MOEOMV1980,
dn_ACSOMV1970.value as ACSOMV1970,
dn_MOEOMV1970.value as MOEOMV1970,
dn_ACSOMV1969.value as ACSOMV1969,
dn_MOEOMV1969.value as MOEOMV1969,
dn_ACSRMV2005.value as ACSRMV2005,
dn_MOERMV2005.value as MOERMV2005,
dn_ACSRMV2000.value as ACSRMV2000,
dn_MOERMV2000.value as MOERMV2000,
dn_ACSRMV1990.value as ACSRMV1990,
dn_MOERMV1990.value as MOERMV1990,
dn_ACSRMV1980.value as ACSRMV1980,
dn_MOERMV1980.value as MOERMV1980,
dn_ACSRMV1970.value as ACSRMV1970,
dn_MOERMV1970.value as MOERMV1970,
dn_ACSRMV1969.value as ACSRMV1969,
dn_MOERMV1969.value as MOERMV1969,
dn_ACSMEDYRMV.value as ACSMEDYRMV,
dn_MOEMEDYRMV.value as MOEMEDYRMV,
dn_TRIGGER2.value as TRIGGER2,
dn_ACSHEATBAS.value as ACSHEATBAS,
dn_MOEHEATBAS.value as MOEHEATBAS,
dn_ACSUTLGAS.value as ACSUTLGAS,
dn_MOEUTLGAS.value as MOEUTLGAS,
dn_ACSLPGAS.value as ACSLPGAS,
dn_MOELPGAS.value as MOELPGAS,
dn_ACSELEC.value as ACSELEC,
dn_MOEELEC.value as MOEELEC,
dn_ACSOILKER.value as ACSOILKER,
dn_MOEOILKER.value as MOEOILKER,
dn_ACSCOAL.value as ACSCOAL,
dn_MOECOAL.value as MOECOAL,
dn_ACSWOOD.value as ACSWOOD,
dn_MOEWOOD.value as MOEWOOD,
dn_ACSSOLAR.value as ACSSOLAR,
dn_MOESOLAR.value as MOESOLAR,
dn_ACSOTHFUEL.value as ACSOTHFUEL,
dn_MOEOTHFUEL.value as MOEOTHFUEL,
dn_ACSNOFUEL.value as ACSNOFUEL,
dn_MOENOFUEL.value as MOENOFUEL,
dn_ACSVEHBASE.value as ACSVEHBASE,
dn_MOEVEHBASE.value as MOEVEHBASE,
dn_ACSOVEH0.value as ACSOVEH0,
dn_MOEOVEH0.value as MOEOVEH0,
dn_ACSOVEH1.value as ACSOVEH1,
dn_MOEOVEH1.value as MOEOVEH1,
dn_ACSOVEH2.value as ACSOVEH2,
dn_MOEOVEH2.value as MOEOVEH2,
dn_ACSOVEH3.value as ACSOVEH3,
dn_MOEOVEH3.value as MOEOVEH3,
dn_ACSOVEH4.value as ACSOVEH4,
dn_MOEOVEH4.value as MOEOVEH4,
dn_ACSOVEH5UP.value as ACSOVEH5UP,
dn_MOEOVEH5UP.value as MOEOVEH5UP,
dn_ACSRVEH0.value as ACSRVEH0,
dn_MOERVEH0.value as MOERVEH0,
dn_ACSRVEH1.value as ACSRVEH1,
dn_MOERVEH1.value as MOERVEH1,
dn_ACSRVEH2.value as ACSRVEH2,
dn_MOERVEH2.value as MOERVEH2,
dn_ACSRVEH3.value as ACSRVEH3,
dn_MOERVEH3.value as MOERVEH3,
dn_ACSRVEH4.value as ACSRVEH4,
dn_MOERVEH4.value as MOERVEH4,
dn_ACSRVEH5UP.value as ACSRVEH5UP,
dn_MOERVEH5UP.value as MOERVEH5UP,
dn_ACSAVGVEH.value as ACSAVGVEH,
dn_MOEAVGVEH.value as MOEAVGVEH,
dn_TRIGGER5.value as TRIGGER5,
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
dn_OOHHR15C10.value as OOHHR15C10,
dn_OOHHR25C10.value as OOHHR25C10,
dn_OOHHR35C10.value as OOHHR35C10,
dn_OOHHR45C10.value as OOHHR45C10,
dn_OOHHR55C10.value as OOHHR55C10,
dn_OOHHR65C10.value as OOHHR65C10,
dn_OOHHR75C10.value as OOHHR75C10,
dn_OOHHR85C10.value as OOHHR85C10,
dn_ROHHR15C10.value as ROHHR15C10,
dn_ROHHR25C10.value as ROHHR25C10,
dn_ROHHR35C10.value as ROHHR35C10,
dn_ROHHR45C10.value as ROHHR45C10,
dn_ROHHR55C10.value as ROHHR55C10,
dn_ROHHR65C10.value as ROHHR65C10,
dn_ROHHR75C10.value as ROHHR75C10,
dn_ROHHR85C10.value as ROHHR85C10,
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
left join demographic_numvalues dn_MEDHINC_CY on dn_MEDHINC_CY.trade_area_id = t.trade_area_id and dn_MEDHINC_CY.data_item_id = 84
left join demographic_numvalues dn_AVGHINC_CY on dn_AVGHINC_CY.trade_area_id = t.trade_area_id and dn_AVGHINC_CY.data_item_id = 86
left join demographic_numvalues dn_PCI_CY on dn_PCI_CY.trade_area_id = t.trade_area_id and dn_PCI_CY.data_item_id = 88
left join demographic_numvalues dn_WHITE_CY on dn_WHITE_CY.trade_area_id = t.trade_area_id and dn_WHITE_CY.data_item_id = 164
left join demographic_numvalues dn_BLACK_CY on dn_BLACK_CY.trade_area_id = t.trade_area_id and dn_BLACK_CY.data_item_id = 170
left join demographic_numvalues dn_AMERIND_CY on dn_AMERIND_CY.trade_area_id = t.trade_area_id and dn_AMERIND_CY.data_item_id = 176
left join demographic_numvalues dn_ASIAN_CY on dn_ASIAN_CY.trade_area_id = t.trade_area_id and dn_ASIAN_CY.data_item_id = 182
left join demographic_numvalues dn_PACIFIC_CY on dn_PACIFIC_CY.trade_area_id = t.trade_area_id and dn_PACIFIC_CY.data_item_id = 188
left join demographic_numvalues dn_OTHRACE_CY on dn_OTHRACE_CY.trade_area_id = t.trade_area_id and dn_OTHRACE_CY.data_item_id = 194
left join demographic_numvalues dn_RACE2UP_CY on dn_RACE2UP_CY.trade_area_id = t.trade_area_id and dn_RACE2UP_CY.data_item_id = 200
left join demographic_numvalues dn_HISPPOPCY on dn_HISPPOPCY.trade_area_id = t.trade_area_id and dn_HISPPOPCY.data_item_id = 206
left join demographic_numvalues dn_ACSTOTPOP on dn_ACSTOTPOP.trade_area_id = t.trade_area_id and dn_ACSTOTPOP.data_item_id = 258
left join demographic_numvalues dn_MOETOTPOP on dn_MOETOTPOP.trade_area_id = t.trade_area_id and dn_MOETOTPOP.data_item_id = 259
left join demographic_numvalues dn_ACSTOTHH on dn_ACSTOTHH.trade_area_id = t.trade_area_id and dn_ACSTOTHH.data_item_id = 261
left join demographic_numvalues dn_MOETOTHH on dn_MOETOTHH.trade_area_id = t.trade_area_id and dn_MOETOTHH.data_item_id = 262
left join demographic_numvalues dn_ACSTOTHU on dn_ACSTOTHU.trade_area_id = t.trade_area_id and dn_ACSTOTHU.data_item_id = 264
left join demographic_numvalues dn_MOETOTHU on dn_MOETOTHU.trade_area_id = t.trade_area_id and dn_MOETOTHU.data_item_id = 265
left join demographic_numvalues dn_ACSVALBASE on dn_ACSVALBASE.trade_area_id = t.trade_area_id and dn_ACSVALBASE.data_item_id = 267
left join demographic_numvalues dn_MOEVALBASE on dn_MOEVALBASE.trade_area_id = t.trade_area_id and dn_MOEVALBASE.data_item_id = 268
left join demographic_numvalues dn_ACSVAL0 on dn_ACSVAL0.trade_area_id = t.trade_area_id and dn_ACSVAL0.data_item_id = 270
left join demographic_numvalues dn_MOEVAL0 on dn_MOEVAL0.trade_area_id = t.trade_area_id and dn_MOEVAL0.data_item_id = 271
left join demographic_numvalues dn_ACSVAL10K on dn_ACSVAL10K.trade_area_id = t.trade_area_id and dn_ACSVAL10K.data_item_id = 273
left join demographic_numvalues dn_MOEVAL10K on dn_MOEVAL10K.trade_area_id = t.trade_area_id and dn_MOEVAL10K.data_item_id = 274
left join demographic_numvalues dn_ACSVAL15K on dn_ACSVAL15K.trade_area_id = t.trade_area_id and dn_ACSVAL15K.data_item_id = 276
left join demographic_numvalues dn_MOEVAL15K on dn_MOEVAL15K.trade_area_id = t.trade_area_id and dn_MOEVAL15K.data_item_id = 277
left join demographic_numvalues dn_ACSVAL20K on dn_ACSVAL20K.trade_area_id = t.trade_area_id and dn_ACSVAL20K.data_item_id = 279
left join demographic_numvalues dn_MOEVAL20K on dn_MOEVAL20K.trade_area_id = t.trade_area_id and dn_MOEVAL20K.data_item_id = 280
left join demographic_numvalues dn_ACSVAL25K on dn_ACSVAL25K.trade_area_id = t.trade_area_id and dn_ACSVAL25K.data_item_id = 282
left join demographic_numvalues dn_MOEVAL25K on dn_MOEVAL25K.trade_area_id = t.trade_area_id and dn_MOEVAL25K.data_item_id = 283
left join demographic_numvalues dn_ACSVAL30K on dn_ACSVAL30K.trade_area_id = t.trade_area_id and dn_ACSVAL30K.data_item_id = 285
left join demographic_numvalues dn_MOEVAL30K on dn_MOEVAL30K.trade_area_id = t.trade_area_id and dn_MOEVAL30K.data_item_id = 286
left join demographic_numvalues dn_ACSVAL35K on dn_ACSVAL35K.trade_area_id = t.trade_area_id and dn_ACSVAL35K.data_item_id = 288
left join demographic_numvalues dn_MOEVAL35K on dn_MOEVAL35K.trade_area_id = t.trade_area_id and dn_MOEVAL35K.data_item_id = 289
left join demographic_numvalues dn_ACSVAL40K on dn_ACSVAL40K.trade_area_id = t.trade_area_id and dn_ACSVAL40K.data_item_id = 291
left join demographic_numvalues dn_MOEVAL40K on dn_MOEVAL40K.trade_area_id = t.trade_area_id and dn_MOEVAL40K.data_item_id = 292
left join demographic_numvalues dn_ACSVAL50K on dn_ACSVAL50K.trade_area_id = t.trade_area_id and dn_ACSVAL50K.data_item_id = 294
left join demographic_numvalues dn_MOEVAL50K on dn_MOEVAL50K.trade_area_id = t.trade_area_id and dn_MOEVAL50K.data_item_id = 295
left join demographic_numvalues dn_ACSVAL60K on dn_ACSVAL60K.trade_area_id = t.trade_area_id and dn_ACSVAL60K.data_item_id = 297
left join demographic_numvalues dn_MOEVAL60K on dn_MOEVAL60K.trade_area_id = t.trade_area_id and dn_MOEVAL60K.data_item_id = 298
left join demographic_numvalues dn_ACSVAL70K on dn_ACSVAL70K.trade_area_id = t.trade_area_id and dn_ACSVAL70K.data_item_id = 300
left join demographic_numvalues dn_MOEVAL70K on dn_MOEVAL70K.trade_area_id = t.trade_area_id and dn_MOEVAL70K.data_item_id = 301
left join demographic_numvalues dn_ACSVAL80K on dn_ACSVAL80K.trade_area_id = t.trade_area_id and dn_ACSVAL80K.data_item_id = 303
left join demographic_numvalues dn_MOEVAL80K on dn_MOEVAL80K.trade_area_id = t.trade_area_id and dn_MOEVAL80K.data_item_id = 304
left join demographic_numvalues dn_ACSVAL90K on dn_ACSVAL90K.trade_area_id = t.trade_area_id and dn_ACSVAL90K.data_item_id = 306
left join demographic_numvalues dn_MOEVAL90K on dn_MOEVAL90K.trade_area_id = t.trade_area_id and dn_MOEVAL90K.data_item_id = 307
left join demographic_numvalues dn_ACSVAL100K on dn_ACSVAL100K.trade_area_id = t.trade_area_id and dn_ACSVAL100K.data_item_id = 309
left join demographic_numvalues dn_MOEVAL100K on dn_MOEVAL100K.trade_area_id = t.trade_area_id and dn_MOEVAL100K.data_item_id = 310
left join demographic_numvalues dn_ACSVAL125K on dn_ACSVAL125K.trade_area_id = t.trade_area_id and dn_ACSVAL125K.data_item_id = 312
left join demographic_numvalues dn_MOEVAL125K on dn_MOEVAL125K.trade_area_id = t.trade_area_id and dn_MOEVAL125K.data_item_id = 313
left join demographic_numvalues dn_ACSVAL150K on dn_ACSVAL150K.trade_area_id = t.trade_area_id and dn_ACSVAL150K.data_item_id = 315
left join demographic_numvalues dn_MOEVAL150K on dn_MOEVAL150K.trade_area_id = t.trade_area_id and dn_MOEVAL150K.data_item_id = 316
left join demographic_numvalues dn_ACSVAL175K on dn_ACSVAL175K.trade_area_id = t.trade_area_id and dn_ACSVAL175K.data_item_id = 318
left join demographic_numvalues dn_MOEVAL175K on dn_MOEVAL175K.trade_area_id = t.trade_area_id and dn_MOEVAL175K.data_item_id = 319
left join demographic_numvalues dn_ACSVAL200K on dn_ACSVAL200K.trade_area_id = t.trade_area_id and dn_ACSVAL200K.data_item_id = 321
left join demographic_numvalues dn_MOEVAL200K on dn_MOEVAL200K.trade_area_id = t.trade_area_id and dn_MOEVAL200K.data_item_id = 322
left join demographic_numvalues dn_ACSVAL250K on dn_ACSVAL250K.trade_area_id = t.trade_area_id and dn_ACSVAL250K.data_item_id = 324
left join demographic_numvalues dn_MOEVAL250K on dn_MOEVAL250K.trade_area_id = t.trade_area_id and dn_MOEVAL250K.data_item_id = 325
left join demographic_numvalues dn_ACSVAL300K on dn_ACSVAL300K.trade_area_id = t.trade_area_id and dn_ACSVAL300K.data_item_id = 327
left join demographic_numvalues dn_MOEVAL300K on dn_MOEVAL300K.trade_area_id = t.trade_area_id and dn_MOEVAL300K.data_item_id = 328
left join demographic_numvalues dn_ACSVAL400K on dn_ACSVAL400K.trade_area_id = t.trade_area_id and dn_ACSVAL400K.data_item_id = 330
left join demographic_numvalues dn_MOEVAL400K on dn_MOEVAL400K.trade_area_id = t.trade_area_id and dn_MOEVAL400K.data_item_id = 331
left join demographic_numvalues dn_ACSVAL500K on dn_ACSVAL500K.trade_area_id = t.trade_area_id and dn_ACSVAL500K.data_item_id = 333
left join demographic_numvalues dn_MOEVAL500K on dn_MOEVAL500K.trade_area_id = t.trade_area_id and dn_MOEVAL500K.data_item_id = 334
left join demographic_numvalues dn_ACSVAL750K on dn_ACSVAL750K.trade_area_id = t.trade_area_id and dn_ACSVAL750K.data_item_id = 336
left join demographic_numvalues dn_MOEVAL750K on dn_MOEVAL750K.trade_area_id = t.trade_area_id and dn_MOEVAL750K.data_item_id = 337
left join demographic_numvalues dn_ACSVAL1M on dn_ACSVAL1M.trade_area_id = t.trade_area_id and dn_ACSVAL1M.data_item_id = 339
left join demographic_numvalues dn_MOEVAL1M on dn_MOEVAL1M.trade_area_id = t.trade_area_id and dn_MOEVAL1M.data_item_id = 340
left join demographic_numvalues dn_ACSMEDVAL on dn_ACSMEDVAL.trade_area_id = t.trade_area_id and dn_ACSMEDVAL.data_item_id = 342
left join demographic_numvalues dn_MOEMEDVAL on dn_MOEMEDVAL.trade_area_id = t.trade_area_id and dn_MOEMEDVAL.data_item_id = 343
left join demographic_numvalues dn_TRIGGER on dn_TRIGGER.trade_area_id = t.trade_area_id and dn_TRIGGER.data_item_id = 344
left join demographic_numvalues dn_ACSAVGVAL on dn_ACSAVGVAL.trade_area_id = t.trade_area_id and dn_ACSAVGVAL.data_item_id = 345
left join demographic_numvalues dn_MOEAVGVAL on dn_MOEAVGVAL.trade_area_id = t.trade_area_id and dn_MOEAVGVAL.data_item_id = 346
left join demographic_numvalues dn_TRIGGER3 on dn_TRIGGER3.trade_area_id = t.trade_area_id and dn_TRIGGER3.data_item_id = 347
left join demographic_numvalues dn_ACSMORTBAS on dn_ACSMORTBAS.trade_area_id = t.trade_area_id and dn_ACSMORTBAS.data_item_id = 348
left join demographic_numvalues dn_MOEMORTBAS on dn_MOEMORTBAS.trade_area_id = t.trade_area_id and dn_MOEMORTBAS.data_item_id = 349
left join demographic_numvalues dn_ACSMORT on dn_ACSMORT.trade_area_id = t.trade_area_id and dn_ACSMORT.data_item_id = 351
left join demographic_numvalues dn_MOEMORT on dn_MOEMORT.trade_area_id = t.trade_area_id and dn_MOEMORT.data_item_id = 352
left join demographic_numvalues dn_ACSM2ONLY on dn_ACSM2ONLY.trade_area_id = t.trade_area_id and dn_ACSM2ONLY.data_item_id = 354
left join demographic_numvalues dn_MOEM2ONLY on dn_MOEM2ONLY.trade_area_id = t.trade_area_id and dn_MOEM2ONLY.data_item_id = 355
left join demographic_numvalues dn_ACSMEQONLY on dn_ACSMEQONLY.trade_area_id = t.trade_area_id and dn_ACSMEQONLY.data_item_id = 357
left join demographic_numvalues dn_MOEMEQONLY on dn_MOEMEQONLY.trade_area_id = t.trade_area_id and dn_MOEMEQONLY.data_item_id = 358
left join demographic_numvalues dn_ACSM2ANDEQ on dn_ACSM2ANDEQ.trade_area_id = t.trade_area_id and dn_ACSM2ANDEQ.data_item_id = 360
left join demographic_numvalues dn_MOEM2ANDEQ on dn_MOEM2ANDEQ.trade_area_id = t.trade_area_id and dn_MOEM2ANDEQ.data_item_id = 361
left join demographic_numvalues dn_ACSM1ONLY on dn_ACSM1ONLY.trade_area_id = t.trade_area_id and dn_ACSM1ONLY.data_item_id = 363
left join demographic_numvalues dn_MOEM1ONLY on dn_MOEM1ONLY.trade_area_id = t.trade_area_id and dn_MOEM1ONLY.data_item_id = 364
left join demographic_numvalues dn_ACSNOMORT on dn_ACSNOMORT.trade_area_id = t.trade_area_id and dn_ACSNOMORT.data_item_id = 366
left join demographic_numvalues dn_MOENOMORT on dn_MOENOMORT.trade_area_id = t.trade_area_id and dn_MOENOMORT.data_item_id = 367
left join demographic_numvalues dn_ACSAVGVALM on dn_ACSAVGVALM.trade_area_id = t.trade_area_id and dn_ACSAVGVALM.data_item_id = 369
left join demographic_numvalues dn_MOEAVGVALM on dn_MOEAVGVALM.trade_area_id = t.trade_area_id and dn_MOEAVGVALM.data_item_id = 370
left join demographic_numvalues dn_TRIGGER7 on dn_TRIGGER7.trade_area_id = t.trade_area_id and dn_TRIGGER7.data_item_id = 371
left join demographic_numvalues dn_ACSAVGVALN on dn_ACSAVGVALN.trade_area_id = t.trade_area_id and dn_ACSAVGVALN.data_item_id = 372
left join demographic_numvalues dn_MOEAVGVALN on dn_MOEAVGVALN.trade_area_id = t.trade_area_id and dn_MOEAVGVALN.data_item_id = 373
left join demographic_numvalues dn_TRIGGER6 on dn_TRIGGER6.trade_area_id = t.trade_area_id and dn_TRIGGER6.data_item_id = 374
left join demographic_numvalues dn_ACSCRNTBAS on dn_ACSCRNTBAS.trade_area_id = t.trade_area_id and dn_ACSCRNTBAS.data_item_id = 375
left join demographic_numvalues dn_MOECRNTBAS on dn_MOECRNTBAS.trade_area_id = t.trade_area_id and dn_MOECRNTBAS.data_item_id = 376
left join demographic_numvalues dn_ACSPAYCRNT on dn_ACSPAYCRNT.trade_area_id = t.trade_area_id and dn_ACSPAYCRNT.data_item_id = 378
left join demographic_numvalues dn_MOEPAYCRNT on dn_MOEPAYCRNT.trade_area_id = t.trade_area_id and dn_MOEPAYCRNT.data_item_id = 379
left join demographic_numvalues dn_ACSRNT0 on dn_ACSRNT0.trade_area_id = t.trade_area_id and dn_ACSRNT0.data_item_id = 381
left join demographic_numvalues dn_MOERNT0 on dn_MOERNT0.trade_area_id = t.trade_area_id and dn_MOERNT0.data_item_id = 382
left join demographic_numvalues dn_ACSRNT100 on dn_ACSRNT100.trade_area_id = t.trade_area_id and dn_ACSRNT100.data_item_id = 384
left join demographic_numvalues dn_MOERNT100 on dn_MOERNT100.trade_area_id = t.trade_area_id and dn_MOERNT100.data_item_id = 385
left join demographic_numvalues dn_ACSRNT150 on dn_ACSRNT150.trade_area_id = t.trade_area_id and dn_ACSRNT150.data_item_id = 387
left join demographic_numvalues dn_MOERNT150 on dn_MOERNT150.trade_area_id = t.trade_area_id and dn_MOERNT150.data_item_id = 388
left join demographic_numvalues dn_ACSRNT200 on dn_ACSRNT200.trade_area_id = t.trade_area_id and dn_ACSRNT200.data_item_id = 390
left join demographic_numvalues dn_MOERNT200 on dn_MOERNT200.trade_area_id = t.trade_area_id and dn_MOERNT200.data_item_id = 391
left join demographic_numvalues dn_ACSRNT250 on dn_ACSRNT250.trade_area_id = t.trade_area_id and dn_ACSRNT250.data_item_id = 393
left join demographic_numvalues dn_MOERNT250 on dn_MOERNT250.trade_area_id = t.trade_area_id and dn_MOERNT250.data_item_id = 394
left join demographic_numvalues dn_ACSRNT300 on dn_ACSRNT300.trade_area_id = t.trade_area_id and dn_ACSRNT300.data_item_id = 396
left join demographic_numvalues dn_MOERNT300 on dn_MOERNT300.trade_area_id = t.trade_area_id and dn_MOERNT300.data_item_id = 397
left join demographic_numvalues dn_ACSRNT350 on dn_ACSRNT350.trade_area_id = t.trade_area_id and dn_ACSRNT350.data_item_id = 399
left join demographic_numvalues dn_MOERNT350 on dn_MOERNT350.trade_area_id = t.trade_area_id and dn_MOERNT350.data_item_id = 400
left join demographic_numvalues dn_ACSRNT400 on dn_ACSRNT400.trade_area_id = t.trade_area_id and dn_ACSRNT400.data_item_id = 402
left join demographic_numvalues dn_MOERNT400 on dn_MOERNT400.trade_area_id = t.trade_area_id and dn_MOERNT400.data_item_id = 403
left join demographic_numvalues dn_ACSRNT450 on dn_ACSRNT450.trade_area_id = t.trade_area_id and dn_ACSRNT450.data_item_id = 405
left join demographic_numvalues dn_MOERNT450 on dn_MOERNT450.trade_area_id = t.trade_area_id and dn_MOERNT450.data_item_id = 406
left join demographic_numvalues dn_ACSRNT500 on dn_ACSRNT500.trade_area_id = t.trade_area_id and dn_ACSRNT500.data_item_id = 408
left join demographic_numvalues dn_MOERNT500 on dn_MOERNT500.trade_area_id = t.trade_area_id and dn_MOERNT500.data_item_id = 409
left join demographic_numvalues dn_ACSRNT550 on dn_ACSRNT550.trade_area_id = t.trade_area_id and dn_ACSRNT550.data_item_id = 411
left join demographic_numvalues dn_MOERNT550 on dn_MOERNT550.trade_area_id = t.trade_area_id and dn_MOERNT550.data_item_id = 412
left join demographic_numvalues dn_ACSRNT600 on dn_ACSRNT600.trade_area_id = t.trade_area_id and dn_ACSRNT600.data_item_id = 414
left join demographic_numvalues dn_MOERNT600 on dn_MOERNT600.trade_area_id = t.trade_area_id and dn_MOERNT600.data_item_id = 415
left join demographic_numvalues dn_ACSRNT650 on dn_ACSRNT650.trade_area_id = t.trade_area_id and dn_ACSRNT650.data_item_id = 417
left join demographic_numvalues dn_MOERNT650 on dn_MOERNT650.trade_area_id = t.trade_area_id and dn_MOERNT650.data_item_id = 418
left join demographic_numvalues dn_ACSRNT700 on dn_ACSRNT700.trade_area_id = t.trade_area_id and dn_ACSRNT700.data_item_id = 420
left join demographic_numvalues dn_MOERNT700 on dn_MOERNT700.trade_area_id = t.trade_area_id and dn_MOERNT700.data_item_id = 421
left join demographic_numvalues dn_ACSRNT750 on dn_ACSRNT750.trade_area_id = t.trade_area_id and dn_ACSRNT750.data_item_id = 423
left join demographic_numvalues dn_MOERNT750 on dn_MOERNT750.trade_area_id = t.trade_area_id and dn_MOERNT750.data_item_id = 424
left join demographic_numvalues dn_ACSRNT800 on dn_ACSRNT800.trade_area_id = t.trade_area_id and dn_ACSRNT800.data_item_id = 426
left join demographic_numvalues dn_MOERNT800 on dn_MOERNT800.trade_area_id = t.trade_area_id and dn_MOERNT800.data_item_id = 427
left join demographic_numvalues dn_ACSRNT900 on dn_ACSRNT900.trade_area_id = t.trade_area_id and dn_ACSRNT900.data_item_id = 429
left join demographic_numvalues dn_MOERNT900 on dn_MOERNT900.trade_area_id = t.trade_area_id and dn_MOERNT900.data_item_id = 430
left join demographic_numvalues dn_ACSRNT1000 on dn_ACSRNT1000.trade_area_id = t.trade_area_id and dn_ACSRNT1000.data_item_id = 432
left join demographic_numvalues dn_MOERNT1000 on dn_MOERNT1000.trade_area_id = t.trade_area_id and dn_MOERNT1000.data_item_id = 433
left join demographic_numvalues dn_ACSRNT1250 on dn_ACSRNT1250.trade_area_id = t.trade_area_id and dn_ACSRNT1250.data_item_id = 435
left join demographic_numvalues dn_MOERNT1250 on dn_MOERNT1250.trade_area_id = t.trade_area_id and dn_MOERNT1250.data_item_id = 436
left join demographic_numvalues dn_ACSRNT1500 on dn_ACSRNT1500.trade_area_id = t.trade_area_id and dn_ACSRNT1500.data_item_id = 438
left join demographic_numvalues dn_MOERNT1500 on dn_MOERNT1500.trade_area_id = t.trade_area_id and dn_MOERNT1500.data_item_id = 439
left join demographic_numvalues dn_ACSRNT2000 on dn_ACSRNT2000.trade_area_id = t.trade_area_id and dn_ACSRNT2000.data_item_id = 441
left join demographic_numvalues dn_MOERNT2000 on dn_MOERNT2000.trade_area_id = t.trade_area_id and dn_MOERNT2000.data_item_id = 442
left join demographic_numvalues dn_ACSRNTNONE on dn_ACSRNTNONE.trade_area_id = t.trade_area_id and dn_ACSRNTNONE.data_item_id = 444
left join demographic_numvalues dn_MOERNTNONE on dn_MOERNTNONE.trade_area_id = t.trade_area_id and dn_MOERNTNONE.data_item_id = 445
left join demographic_numvalues dn_ACSMEDCRNT on dn_ACSMEDCRNT.trade_area_id = t.trade_area_id and dn_ACSMEDCRNT.data_item_id = 447
left join demographic_numvalues dn_MOEMEDCRNT on dn_MOEMEDCRNT.trade_area_id = t.trade_area_id and dn_MOEMEDCRNT.data_item_id = 448
left join demographic_numvalues dn_TRIGGER0 on dn_TRIGGER0.trade_area_id = t.trade_area_id and dn_TRIGGER0.data_item_id = 449
left join demographic_numvalues dn_ACSAVGCRNT on dn_ACSAVGCRNT.trade_area_id = t.trade_area_id and dn_ACSAVGCRNT.data_item_id = 450
left join demographic_numvalues dn_MOEAVGCRNT on dn_MOEAVGCRNT.trade_area_id = t.trade_area_id and dn_MOEAVGCRNT.data_item_id = 451
left join demographic_numvalues dn_TRIGGER4 on dn_TRIGGER4.trade_area_id = t.trade_area_id and dn_TRIGGER4.data_item_id = 452
left join demographic_numvalues dn_ACSUTLBASE on dn_ACSUTLBASE.trade_area_id = t.trade_area_id and dn_ACSUTLBASE.data_item_id = 453
left join demographic_numvalues dn_MOEUTLBASE on dn_MOEUTLBASE.trade_area_id = t.trade_area_id and dn_MOEUTLBASE.data_item_id = 454
left join demographic_numvalues dn_ACSUTLEXTR on dn_ACSUTLEXTR.trade_area_id = t.trade_area_id and dn_ACSUTLEXTR.data_item_id = 456
left join demographic_numvalues dn_MOEUTLEXTR on dn_MOEUTLEXTR.trade_area_id = t.trade_area_id and dn_MOEUTLEXTR.data_item_id = 457
left join demographic_numvalues dn_ACSUTLNRNT on dn_ACSUTLNRNT.trade_area_id = t.trade_area_id and dn_ACSUTLNRNT.data_item_id = 459
left join demographic_numvalues dn_MOEUTLNRNT on dn_MOEUTLNRNT.trade_area_id = t.trade_area_id and dn_MOEUTLNRNT.data_item_id = 460
left join demographic_numvalues dn_ACSUNTBASE on dn_ACSUNTBASE.trade_area_id = t.trade_area_id and dn_ACSUNTBASE.data_item_id = 462
left join demographic_numvalues dn_MOEUNTBASE on dn_MOEUNTBASE.trade_area_id = t.trade_area_id and dn_MOEUNTBASE.data_item_id = 463
left join demographic_numvalues dn_ACSUNT1DET on dn_ACSUNT1DET.trade_area_id = t.trade_area_id and dn_ACSUNT1DET.data_item_id = 465
left join demographic_numvalues dn_MOEUNT1DET on dn_MOEUNT1DET.trade_area_id = t.trade_area_id and dn_MOEUNT1DET.data_item_id = 466
left join demographic_numvalues dn_ACSUNT1ATT on dn_ACSUNT1ATT.trade_area_id = t.trade_area_id and dn_ACSUNT1ATT.data_item_id = 468
left join demographic_numvalues dn_MOEUNT1ATT on dn_MOEUNT1ATT.trade_area_id = t.trade_area_id and dn_MOEUNT1ATT.data_item_id = 469
left join demographic_numvalues dn_ACSUNT2 on dn_ACSUNT2.trade_area_id = t.trade_area_id and dn_ACSUNT2.data_item_id = 471
left join demographic_numvalues dn_MOEUNT2 on dn_MOEUNT2.trade_area_id = t.trade_area_id and dn_MOEUNT2.data_item_id = 472
left join demographic_numvalues dn_ACSUNT3 on dn_ACSUNT3.trade_area_id = t.trade_area_id and dn_ACSUNT3.data_item_id = 474
left join demographic_numvalues dn_MOEUNT3 on dn_MOEUNT3.trade_area_id = t.trade_area_id and dn_MOEUNT3.data_item_id = 475
left join demographic_numvalues dn_ACSUNT5 on dn_ACSUNT5.trade_area_id = t.trade_area_id and dn_ACSUNT5.data_item_id = 477
left join demographic_numvalues dn_MOEUNT5 on dn_MOEUNT5.trade_area_id = t.trade_area_id and dn_MOEUNT5.data_item_id = 478
left join demographic_numvalues dn_ACSUNT10 on dn_ACSUNT10.trade_area_id = t.trade_area_id and dn_ACSUNT10.data_item_id = 480
left join demographic_numvalues dn_MOEUNT10 on dn_MOEUNT10.trade_area_id = t.trade_area_id and dn_MOEUNT10.data_item_id = 481
left join demographic_numvalues dn_ACSUNT20 on dn_ACSUNT20.trade_area_id = t.trade_area_id and dn_ACSUNT20.data_item_id = 483
left join demographic_numvalues dn_MOEUNT20 on dn_MOEUNT20.trade_area_id = t.trade_area_id and dn_MOEUNT20.data_item_id = 484
left join demographic_numvalues dn_ACSUNT50UP on dn_ACSUNT50UP.trade_area_id = t.trade_area_id and dn_ACSUNT50UP.data_item_id = 486
left join demographic_numvalues dn_MOEUNT50UP on dn_MOEUNT50UP.trade_area_id = t.trade_area_id and dn_MOEUNT50UP.data_item_id = 487
left join demographic_numvalues dn_ACSUNTMOB on dn_ACSUNTMOB.trade_area_id = t.trade_area_id and dn_ACSUNTMOB.data_item_id = 489
left join demographic_numvalues dn_MOEUNTMOB on dn_MOEUNTMOB.trade_area_id = t.trade_area_id and dn_MOEUNTMOB.data_item_id = 490
left join demographic_numvalues dn_ACSUNTOTH on dn_ACSUNTOTH.trade_area_id = t.trade_area_id and dn_ACSUNTOTH.data_item_id = 492
left join demographic_numvalues dn_MOEUNTOTH on dn_MOEUNTOTH.trade_area_id = t.trade_area_id and dn_MOEUNTOTH.data_item_id = 493
left join demographic_numvalues dn_ACSYBLTBAS on dn_ACSYBLTBAS.trade_area_id = t.trade_area_id and dn_ACSYBLTBAS.data_item_id = 495
left join demographic_numvalues dn_MOEYBLTBAS on dn_MOEYBLTBAS.trade_area_id = t.trade_area_id and dn_MOEYBLTBAS.data_item_id = 496
left join demographic_numvalues dn_ACSBLT2005 on dn_ACSBLT2005.trade_area_id = t.trade_area_id and dn_ACSBLT2005.data_item_id = 498
left join demographic_numvalues dn_MOEBLT2005 on dn_MOEBLT2005.trade_area_id = t.trade_area_id and dn_MOEBLT2005.data_item_id = 499
left join demographic_numvalues dn_ACSBLT2000 on dn_ACSBLT2000.trade_area_id = t.trade_area_id and dn_ACSBLT2000.data_item_id = 501
left join demographic_numvalues dn_MOEBLT2000 on dn_MOEBLT2000.trade_area_id = t.trade_area_id and dn_MOEBLT2000.data_item_id = 502
left join demographic_numvalues dn_ACSBLT1990 on dn_ACSBLT1990.trade_area_id = t.trade_area_id and dn_ACSBLT1990.data_item_id = 504
left join demographic_numvalues dn_MOEBLT1990 on dn_MOEBLT1990.trade_area_id = t.trade_area_id and dn_MOEBLT1990.data_item_id = 505
left join demographic_numvalues dn_ACSBLT1980 on dn_ACSBLT1980.trade_area_id = t.trade_area_id and dn_ACSBLT1980.data_item_id = 507
left join demographic_numvalues dn_MOEBLT1980 on dn_MOEBLT1980.trade_area_id = t.trade_area_id and dn_MOEBLT1980.data_item_id = 508
left join demographic_numvalues dn_ACSBLT1970 on dn_ACSBLT1970.trade_area_id = t.trade_area_id and dn_ACSBLT1970.data_item_id = 510
left join demographic_numvalues dn_MOEBLT1970 on dn_MOEBLT1970.trade_area_id = t.trade_area_id and dn_MOEBLT1970.data_item_id = 511
left join demographic_numvalues dn_ACSBLT1960 on dn_ACSBLT1960.trade_area_id = t.trade_area_id and dn_ACSBLT1960.data_item_id = 513
left join demographic_numvalues dn_MOEBLT1960 on dn_MOEBLT1960.trade_area_id = t.trade_area_id and dn_MOEBLT1960.data_item_id = 514
left join demographic_numvalues dn_ACSBLT1950 on dn_ACSBLT1950.trade_area_id = t.trade_area_id and dn_ACSBLT1950.data_item_id = 516
left join demographic_numvalues dn_MOEBLT1950 on dn_MOEBLT1950.trade_area_id = t.trade_area_id and dn_MOEBLT1950.data_item_id = 517
left join demographic_numvalues dn_ACSBLT1940 on dn_ACSBLT1940.trade_area_id = t.trade_area_id and dn_ACSBLT1940.data_item_id = 519
left join demographic_numvalues dn_MOEBLT1940 on dn_MOEBLT1940.trade_area_id = t.trade_area_id and dn_MOEBLT1940.data_item_id = 520
left join demographic_numvalues dn_ACSBLT1939 on dn_ACSBLT1939.trade_area_id = t.trade_area_id and dn_ACSBLT1939.data_item_id = 522
left join demographic_numvalues dn_MOEBLT1939 on dn_MOEBLT1939.trade_area_id = t.trade_area_id and dn_MOEBLT1939.data_item_id = 523
left join demographic_numvalues dn_ACSMEDYBLT on dn_ACSMEDYBLT.trade_area_id = t.trade_area_id and dn_ACSMEDYBLT.data_item_id = 525
left join demographic_numvalues dn_MOEMEDYBLT on dn_MOEMEDYBLT.trade_area_id = t.trade_area_id and dn_MOEMEDYBLT.data_item_id = 526
left join demographic_numvalues dn_TRIGGER1 on dn_TRIGGER1.trade_area_id = t.trade_area_id and dn_TRIGGER1.data_item_id = 527
left join demographic_numvalues dn_ACSYRMVBAS on dn_ACSYRMVBAS.trade_area_id = t.trade_area_id and dn_ACSYRMVBAS.data_item_id = 528
left join demographic_numvalues dn_MOEYRMVBAS on dn_MOEYRMVBAS.trade_area_id = t.trade_area_id and dn_MOEYRMVBAS.data_item_id = 529
left join demographic_numvalues dn_ACSOMV2005 on dn_ACSOMV2005.trade_area_id = t.trade_area_id and dn_ACSOMV2005.data_item_id = 531
left join demographic_numvalues dn_MOEOMV2005 on dn_MOEOMV2005.trade_area_id = t.trade_area_id and dn_MOEOMV2005.data_item_id = 532
left join demographic_numvalues dn_ACSOMV2000 on dn_ACSOMV2000.trade_area_id = t.trade_area_id and dn_ACSOMV2000.data_item_id = 534
left join demographic_numvalues dn_MOEOMV2000 on dn_MOEOMV2000.trade_area_id = t.trade_area_id and dn_MOEOMV2000.data_item_id = 535
left join demographic_numvalues dn_ACSOMV1990 on dn_ACSOMV1990.trade_area_id = t.trade_area_id and dn_ACSOMV1990.data_item_id = 537
left join demographic_numvalues dn_MOEOMV1990 on dn_MOEOMV1990.trade_area_id = t.trade_area_id and dn_MOEOMV1990.data_item_id = 538
left join demographic_numvalues dn_ACSOMV1980 on dn_ACSOMV1980.trade_area_id = t.trade_area_id and dn_ACSOMV1980.data_item_id = 540
left join demographic_numvalues dn_MOEOMV1980 on dn_MOEOMV1980.trade_area_id = t.trade_area_id and dn_MOEOMV1980.data_item_id = 541
left join demographic_numvalues dn_ACSOMV1970 on dn_ACSOMV1970.trade_area_id = t.trade_area_id and dn_ACSOMV1970.data_item_id = 543
left join demographic_numvalues dn_MOEOMV1970 on dn_MOEOMV1970.trade_area_id = t.trade_area_id and dn_MOEOMV1970.data_item_id = 544
left join demographic_numvalues dn_ACSOMV1969 on dn_ACSOMV1969.trade_area_id = t.trade_area_id and dn_ACSOMV1969.data_item_id = 546
left join demographic_numvalues dn_MOEOMV1969 on dn_MOEOMV1969.trade_area_id = t.trade_area_id and dn_MOEOMV1969.data_item_id = 547
left join demographic_numvalues dn_ACSRMV2005 on dn_ACSRMV2005.trade_area_id = t.trade_area_id and dn_ACSRMV2005.data_item_id = 549
left join demographic_numvalues dn_MOERMV2005 on dn_MOERMV2005.trade_area_id = t.trade_area_id and dn_MOERMV2005.data_item_id = 550
left join demographic_numvalues dn_ACSRMV2000 on dn_ACSRMV2000.trade_area_id = t.trade_area_id and dn_ACSRMV2000.data_item_id = 552
left join demographic_numvalues dn_MOERMV2000 on dn_MOERMV2000.trade_area_id = t.trade_area_id and dn_MOERMV2000.data_item_id = 553
left join demographic_numvalues dn_ACSRMV1990 on dn_ACSRMV1990.trade_area_id = t.trade_area_id and dn_ACSRMV1990.data_item_id = 555
left join demographic_numvalues dn_MOERMV1990 on dn_MOERMV1990.trade_area_id = t.trade_area_id and dn_MOERMV1990.data_item_id = 556
left join demographic_numvalues dn_ACSRMV1980 on dn_ACSRMV1980.trade_area_id = t.trade_area_id and dn_ACSRMV1980.data_item_id = 558
left join demographic_numvalues dn_MOERMV1980 on dn_MOERMV1980.trade_area_id = t.trade_area_id and dn_MOERMV1980.data_item_id = 559
left join demographic_numvalues dn_ACSRMV1970 on dn_ACSRMV1970.trade_area_id = t.trade_area_id and dn_ACSRMV1970.data_item_id = 561
left join demographic_numvalues dn_MOERMV1970 on dn_MOERMV1970.trade_area_id = t.trade_area_id and dn_MOERMV1970.data_item_id = 562
left join demographic_numvalues dn_ACSRMV1969 on dn_ACSRMV1969.trade_area_id = t.trade_area_id and dn_ACSRMV1969.data_item_id = 564
left join demographic_numvalues dn_MOERMV1969 on dn_MOERMV1969.trade_area_id = t.trade_area_id and dn_MOERMV1969.data_item_id = 565
left join demographic_numvalues dn_ACSMEDYRMV on dn_ACSMEDYRMV.trade_area_id = t.trade_area_id and dn_ACSMEDYRMV.data_item_id = 567
left join demographic_numvalues dn_MOEMEDYRMV on dn_MOEMEDYRMV.trade_area_id = t.trade_area_id and dn_MOEMEDYRMV.data_item_id = 568
left join demographic_numvalues dn_TRIGGER2 on dn_TRIGGER2.trade_area_id = t.trade_area_id and dn_TRIGGER2.data_item_id = 569
left join demographic_numvalues dn_ACSHEATBAS on dn_ACSHEATBAS.trade_area_id = t.trade_area_id and dn_ACSHEATBAS.data_item_id = 570
left join demographic_numvalues dn_MOEHEATBAS on dn_MOEHEATBAS.trade_area_id = t.trade_area_id and dn_MOEHEATBAS.data_item_id = 571
left join demographic_numvalues dn_ACSUTLGAS on dn_ACSUTLGAS.trade_area_id = t.trade_area_id and dn_ACSUTLGAS.data_item_id = 573
left join demographic_numvalues dn_MOEUTLGAS on dn_MOEUTLGAS.trade_area_id = t.trade_area_id and dn_MOEUTLGAS.data_item_id = 574
left join demographic_numvalues dn_ACSLPGAS on dn_ACSLPGAS.trade_area_id = t.trade_area_id and dn_ACSLPGAS.data_item_id = 576
left join demographic_numvalues dn_MOELPGAS on dn_MOELPGAS.trade_area_id = t.trade_area_id and dn_MOELPGAS.data_item_id = 577
left join demographic_numvalues dn_ACSELEC on dn_ACSELEC.trade_area_id = t.trade_area_id and dn_ACSELEC.data_item_id = 579
left join demographic_numvalues dn_MOEELEC on dn_MOEELEC.trade_area_id = t.trade_area_id and dn_MOEELEC.data_item_id = 580
left join demographic_numvalues dn_ACSOILKER on dn_ACSOILKER.trade_area_id = t.trade_area_id and dn_ACSOILKER.data_item_id = 582
left join demographic_numvalues dn_MOEOILKER on dn_MOEOILKER.trade_area_id = t.trade_area_id and dn_MOEOILKER.data_item_id = 583
left join demographic_numvalues dn_ACSCOAL on dn_ACSCOAL.trade_area_id = t.trade_area_id and dn_ACSCOAL.data_item_id = 585
left join demographic_numvalues dn_MOECOAL on dn_MOECOAL.trade_area_id = t.trade_area_id and dn_MOECOAL.data_item_id = 586
left join demographic_numvalues dn_ACSWOOD on dn_ACSWOOD.trade_area_id = t.trade_area_id and dn_ACSWOOD.data_item_id = 588
left join demographic_numvalues dn_MOEWOOD on dn_MOEWOOD.trade_area_id = t.trade_area_id and dn_MOEWOOD.data_item_id = 589
left join demographic_numvalues dn_ACSSOLAR on dn_ACSSOLAR.trade_area_id = t.trade_area_id and dn_ACSSOLAR.data_item_id = 591
left join demographic_numvalues dn_MOESOLAR on dn_MOESOLAR.trade_area_id = t.trade_area_id and dn_MOESOLAR.data_item_id = 592
left join demographic_numvalues dn_ACSOTHFUEL on dn_ACSOTHFUEL.trade_area_id = t.trade_area_id and dn_ACSOTHFUEL.data_item_id = 594
left join demographic_numvalues dn_MOEOTHFUEL on dn_MOEOTHFUEL.trade_area_id = t.trade_area_id and dn_MOEOTHFUEL.data_item_id = 595
left join demographic_numvalues dn_ACSNOFUEL on dn_ACSNOFUEL.trade_area_id = t.trade_area_id and dn_ACSNOFUEL.data_item_id = 597
left join demographic_numvalues dn_MOENOFUEL on dn_MOENOFUEL.trade_area_id = t.trade_area_id and dn_MOENOFUEL.data_item_id = 598
left join demographic_numvalues dn_ACSVEHBASE on dn_ACSVEHBASE.trade_area_id = t.trade_area_id and dn_ACSVEHBASE.data_item_id = 600
left join demographic_numvalues dn_MOEVEHBASE on dn_MOEVEHBASE.trade_area_id = t.trade_area_id and dn_MOEVEHBASE.data_item_id = 601
left join demographic_numvalues dn_ACSOVEH0 on dn_ACSOVEH0.trade_area_id = t.trade_area_id and dn_ACSOVEH0.data_item_id = 603
left join demographic_numvalues dn_MOEOVEH0 on dn_MOEOVEH0.trade_area_id = t.trade_area_id and dn_MOEOVEH0.data_item_id = 604
left join demographic_numvalues dn_ACSOVEH1 on dn_ACSOVEH1.trade_area_id = t.trade_area_id and dn_ACSOVEH1.data_item_id = 606
left join demographic_numvalues dn_MOEOVEH1 on dn_MOEOVEH1.trade_area_id = t.trade_area_id and dn_MOEOVEH1.data_item_id = 607
left join demographic_numvalues dn_ACSOVEH2 on dn_ACSOVEH2.trade_area_id = t.trade_area_id and dn_ACSOVEH2.data_item_id = 609
left join demographic_numvalues dn_MOEOVEH2 on dn_MOEOVEH2.trade_area_id = t.trade_area_id and dn_MOEOVEH2.data_item_id = 610
left join demographic_numvalues dn_ACSOVEH3 on dn_ACSOVEH3.trade_area_id = t.trade_area_id and dn_ACSOVEH3.data_item_id = 612
left join demographic_numvalues dn_MOEOVEH3 on dn_MOEOVEH3.trade_area_id = t.trade_area_id and dn_MOEOVEH3.data_item_id = 613
left join demographic_numvalues dn_ACSOVEH4 on dn_ACSOVEH4.trade_area_id = t.trade_area_id and dn_ACSOVEH4.data_item_id = 615
left join demographic_numvalues dn_MOEOVEH4 on dn_MOEOVEH4.trade_area_id = t.trade_area_id and dn_MOEOVEH4.data_item_id = 616
left join demographic_numvalues dn_ACSOVEH5UP on dn_ACSOVEH5UP.trade_area_id = t.trade_area_id and dn_ACSOVEH5UP.data_item_id = 618
left join demographic_numvalues dn_MOEOVEH5UP on dn_MOEOVEH5UP.trade_area_id = t.trade_area_id and dn_MOEOVEH5UP.data_item_id = 619
left join demographic_numvalues dn_ACSRVEH0 on dn_ACSRVEH0.trade_area_id = t.trade_area_id and dn_ACSRVEH0.data_item_id = 621
left join demographic_numvalues dn_MOERVEH0 on dn_MOERVEH0.trade_area_id = t.trade_area_id and dn_MOERVEH0.data_item_id = 622
left join demographic_numvalues dn_ACSRVEH1 on dn_ACSRVEH1.trade_area_id = t.trade_area_id and dn_ACSRVEH1.data_item_id = 624
left join demographic_numvalues dn_MOERVEH1 on dn_MOERVEH1.trade_area_id = t.trade_area_id and dn_MOERVEH1.data_item_id = 625
left join demographic_numvalues dn_ACSRVEH2 on dn_ACSRVEH2.trade_area_id = t.trade_area_id and dn_ACSRVEH2.data_item_id = 627
left join demographic_numvalues dn_MOERVEH2 on dn_MOERVEH2.trade_area_id = t.trade_area_id and dn_MOERVEH2.data_item_id = 628
left join demographic_numvalues dn_ACSRVEH3 on dn_ACSRVEH3.trade_area_id = t.trade_area_id and dn_ACSRVEH3.data_item_id = 630
left join demographic_numvalues dn_MOERVEH3 on dn_MOERVEH3.trade_area_id = t.trade_area_id and dn_MOERVEH3.data_item_id = 631
left join demographic_numvalues dn_ACSRVEH4 on dn_ACSRVEH4.trade_area_id = t.trade_area_id and dn_ACSRVEH4.data_item_id = 633
left join demographic_numvalues dn_MOERVEH4 on dn_MOERVEH4.trade_area_id = t.trade_area_id and dn_MOERVEH4.data_item_id = 634
left join demographic_numvalues dn_ACSRVEH5UP on dn_ACSRVEH5UP.trade_area_id = t.trade_area_id and dn_ACSRVEH5UP.data_item_id = 636
left join demographic_numvalues dn_MOERVEH5UP on dn_MOERVEH5UP.trade_area_id = t.trade_area_id and dn_MOERVEH5UP.data_item_id = 637
left join demographic_numvalues dn_ACSAVGVEH on dn_ACSAVGVEH.trade_area_id = t.trade_area_id and dn_ACSAVGVEH.data_item_id = 639
left join demographic_numvalues dn_MOEAVGVEH on dn_MOEAVGVEH.trade_area_id = t.trade_area_id and dn_MOEAVGVEH.data_item_id = 640
left join demographic_numvalues dn_TRIGGER5 on dn_TRIGGER5.trade_area_id = t.trade_area_id and dn_TRIGGER5.data_item_id = 641
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
left join demographic_numvalues dn_OOHHR15C10 on dn_OOHHR15C10.trade_area_id = t.trade_area_id and dn_OOHHR15C10.data_item_id = 2850
left join demographic_numvalues dn_OOHHR25C10 on dn_OOHHR25C10.trade_area_id = t.trade_area_id and dn_OOHHR25C10.data_item_id = 2851
left join demographic_numvalues dn_OOHHR35C10 on dn_OOHHR35C10.trade_area_id = t.trade_area_id and dn_OOHHR35C10.data_item_id = 2852
left join demographic_numvalues dn_OOHHR45C10 on dn_OOHHR45C10.trade_area_id = t.trade_area_id and dn_OOHHR45C10.data_item_id = 2853
left join demographic_numvalues dn_OOHHR55C10 on dn_OOHHR55C10.trade_area_id = t.trade_area_id and dn_OOHHR55C10.data_item_id = 2854
left join demographic_numvalues dn_OOHHR65C10 on dn_OOHHR65C10.trade_area_id = t.trade_area_id and dn_OOHHR65C10.data_item_id = 2855
left join demographic_numvalues dn_OOHHR75C10 on dn_OOHHR75C10.trade_area_id = t.trade_area_id and dn_OOHHR75C10.data_item_id = 2856
left join demographic_numvalues dn_OOHHR85C10 on dn_OOHHR85C10.trade_area_id = t.trade_area_id and dn_OOHHR85C10.data_item_id = 2857
left join demographic_numvalues dn_ROHHR15C10 on dn_ROHHR15C10.trade_area_id = t.trade_area_id and dn_ROHHR15C10.data_item_id = 2858
left join demographic_numvalues dn_ROHHR25C10 on dn_ROHHR25C10.trade_area_id = t.trade_area_id and dn_ROHHR25C10.data_item_id = 2859
left join demographic_numvalues dn_ROHHR35C10 on dn_ROHHR35C10.trade_area_id = t.trade_area_id and dn_ROHHR35C10.data_item_id = 2860
left join demographic_numvalues dn_ROHHR45C10 on dn_ROHHR45C10.trade_area_id = t.trade_area_id and dn_ROHHR45C10.data_item_id = 2861
left join demographic_numvalues dn_ROHHR55C10 on dn_ROHHR55C10.trade_area_id = t.trade_area_id and dn_ROHHR55C10.data_item_id = 2862
left join demographic_numvalues dn_ROHHR65C10 on dn_ROHHR65C10.trade_area_id = t.trade_area_id and dn_ROHHR65C10.data_item_id = 2863
left join demographic_numvalues dn_ROHHR75C10 on dn_ROHHR75C10.trade_area_id = t.trade_area_id and dn_ROHHR75C10.data_item_id = 2864
left join demographic_numvalues dn_ROHHR85C10 on dn_ROHHR85C10.trade_area_id = t.trade_area_id and dn_ROHHR85C10.data_item_id = 2865
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