use retaildb_timeseries_uggs
go


insert into [demographics_denorm_10_mile] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
	TOTPOP10,
	TOTPOP_CY,
	TOTPOP_FY,
	TOTHH10,
	TOTHH_CY,
	TOTHH_FY,
	FAMHH10,
	FAMHH_CY,
	FAMHH_FY,
	AVGHHSZ10,
	AVGHHSZ_CY,
	AVGHHSZ_FY,
	OWNER10,
	OWNER_CY,
	OWNER_FY,
	RENTER10,
	RENTER_CY,
	RENTER_FY,
	MEDAGE10,
	MEDAGE_CY,
	MEDAGE_FY,
	SCRIPT_ANU,
	POPRATE_S,
	TR_POP_NAT,
	SCRIPT_A_1,
	HHRATE_S,
	TR_HH_NAT,
	SCRIPT_A_2,
	FAMRATE_S,
	TR_FAM_NAT,
	SCRIPT_AN1,
	OWNRATE_S,
	TR_OWN_NAT,
	SCRIPT_AN0,
	INCRATE_S,
	TR_MHI_NAT,
	HINC0_CY,
	HINC0_CY_P,
	HINC0_FY,
	HINC0_FY_P,
	HINC15_CY,
	HINC15_CY_P,
	HINC15_FY,
	HINC15_FY_P,
	HINC25_CY,
	HINC25_CY_P,
	HINC25_FY,
	HINC25_FY_P,
	HINC35_CY,
	HINC35_CY_P,
	HINC35_FY,
	HINC35_FY_P,
	HINC50_CY,
	HINC50_CY_P,
	HINC50_FY,
	HINC50_FY_P,
	HINC75_CY,
	HINC75_CY_P,
	HINC75_FY,
	HINC75_FY_P,
	HINC100_CY,
	HINC100_CY_P,
	HINC100_FY,
	HINC100_FY_P,
	HINC150_CY,
	HINC150_CY_P,
	HINC150_FY,
	HINC150_FY_P,
	HINC200_CY,
	HINC200_CY_P,
	HINC200_FY,
	HINC200_FY_P,
	MEDHINC_CY,
	MEDHINC_FY,
	AVGHINC_CY,
	AVGHINC_FY,
	PCI_CY,
	PCI_FY,
	POP0C10,
	POP0C10_P,
	POP0_CY,
	POP0_CY_P,
	POP0_FY,
	POP0_FY_P,
	POP5C10,
	POP5C10_P,
	POP5_CY,
	POP5_CY_P,
	POP5_FY,
	POP5_FY_P,
	POP10C10,
	POP10C10_P,
	POP10_CY,
	POP10_CY_P,
	POP10_FY,
	POP10_FY_P,
	POP15C10,
	POP15C10_P,
	POP15_CY,
	POP15_CY_P,
	POP15_FY,
	POP15_FY_P,
	POP20C10,
	POP20C10_P,
	POP20_CY,
	POP20_CY_P,
	POP20_FY,
	POP20_FY_P,
	POP2534C10,
	POP2534C10_P,
	POP2534_CY,
	POP2534_CY_P,
	POP2534_FY,
	POP2534_FY_P,
	POP3544C10,
	POP3544C10_P,
	POP3544_CY,
	POP3544_CY_P,
	POP3544_FY,
	POP3544_FY_P,
	POP4554C10,
	POP4554C10_P,
	POP4554_CY,
	POP4554_CY_P,
	POP4554_FY,
	POP4554_FY_P,
	POP5564C10,
	POP5564C10_P,
	POP5564_CY,
	POP5564_CY_P,
	POP5564_FY,
	POP5564_FY_P,
	POP6574C10,
	POP6574C10_P,
	POP6574_CY,
	POP6574_CY_P,
	POP6574_FY,
	POP6574_FY_P,
	POP7584C10,
	POP7584C10_P,
	POP7584_CY,
	POP7584_CY_P,
	POP7584_FY,
	POP7584_FY_P,
	POP85C10,
	POP85PC10_P,
	POP85_CY,
	POP85P_CY_P,
	POP85_FY,
	POP85P_FY_P,
	WHITE10,
	WHITE10_P,
	WHITE_CY,
	WHITE_CY_P,
	WHITE_FY,
	WHITE_FY_P,
	BLACK10,
	BLACK10_P,
	BLACK_CY,
	BLACK_CY_P,
	BLACK_FY,
	BLACK_FY_P,
	AMERIND10,
	AMERIND10_P,
	AMERIND_CY,
	AMERIND_CY_P,
	AMERIND_FY,
	AMERIND_FY_P,
	ASIAN10,
	ASIAN10_P,
	ASIAN_CY,
	ASIAN_CY_P,
	ASIAN_FY,
	ASIAN_FY_P,
	PACIFIC10,
	PACIFIC10_P,
	PACIFIC_CY,
	PACIFIC_CY_P,
	PACIFIC_FY,
	PACIFIC_FY_P,
	OTHRACE10,
	OTHRACE10_P,
	OTHRACE_CY,
	OTHRACE_CY_P,
	OTHRACE_FY,
	OTHRACE_FY_P,
	RACE2UP10,
	RACE2UP10_P,
	RACE2UP_CY,
	RACE2UP_CY_P,
	RACE2UP_FY,
	RACE2UP_FY_P,
	HISPPOP10,
	HISPPOP10_P,
	HISPPOPCY,
	HISPPOP_CY_P,
	HISPPOPFY,
	HISPPOPFY_P,
	POPRATE,
	HHRATE,
	FAMRATE,
	OWNRATE,
	INCRATE,
	MALE0C10,
	MALE5C10,
	MALE10C10,
	MALE15C10,
	MALE20C10,
	MALE25C10,
	MALE30C10,
	MALE35C10,
	MALE40C10,
	MALE45C10,
	MALE50C10,
	MALE55C10,
	MALE60C10,
	MALE65C10,
	MALE70C10,
	MALE75C10,
	MALE80C10,
	MALE85C10,
	MAL18UP10,
	MAL21UP10,
	MEDMAGE10,
	FEM0C10,
	FEM5C10,
	FEM10C10,
	FEM15C10,
	FEM20C10,
	FEM25C10,
	FEM30C10,
	FEM35C10,
	FEM40C10,
	FEM45C10,
	FEM50C10,
	FEM55C10,
	FEM60C10,
	FEM65C10,
	FEM70C10,
	FEM75C10,
	FEM80C10,
	FEM85C10,
	FEM18UP10,
	FEM21UP10,
	MEDFAGE10,
	agg_income)
	--traffic, auto_parts_DIY_proxy, auto_parts_DIFM_proxy, auto_fleet, commutation_driving_pct, commutation_commute_time, traffic_summed, traffic_weighted_distance)
select
	c.name as company_name,
	s.store_id,
	s.assumed_opened_date,
	s.assumed_closed_date,
	t.trade_area_id,
	dn_TOTPOP10.value as TOTPOP10,
	dn_TOTPOP_CY.value as TOTPOP_CY,
	dn_TOTPOP_FY.value as TOTPOP_FY,
	dn_TOTHH10.value as TOTHH10,
	dn_TOTHH_CY.value as TOTHH_CY,
	dn_TOTHH_FY.value as TOTHH_FY,
	dn_FAMHH10.value as FAMHH10,
	dn_FAMHH_CY.value as FAMHH_CY,
	dn_FAMHH_FY.value as FAMHH_FY,
	dn_AVGHHSZ10.value as AVGHHSZ10,
	dn_AVGHHSZ_CY.value as AVGHHSZ_CY,
	dn_AVGHHSZ_FY.value as AVGHHSZ_FY,
	dn_OWNER10.value as OWNER10,
	dn_OWNER_CY.value as OWNER_CY,
	dn_OWNER_FY.value as OWNER_FY,
	dn_RENTER10.value as RENTER10,
	dn_RENTER_CY.value as RENTER_CY,
	dn_RENTER_FY.value as RENTER_FY,
	dn_MEDAGE10.value as MEDAGE10,
	dn_MEDAGE_CY.value as MEDAGE_CY,
	dn_MEDAGE_FY.value as MEDAGE_FY,
	dn_SCRIPT_ANU.value as SCRIPT_ANU,
	dn_POPRATE_S.value as POPRATE_S,
	dn_TR_POP_NAT.value as TR_POP_NAT,
	dn_SCRIPT_A_1.value as SCRIPT_A_1,
	dn_HHRATE_S.value as HHRATE_S,
	dn_TR_HH_NAT.value as TR_HH_NAT,
	dn_SCRIPT_A_2.value as SCRIPT_A_2,
	dn_FAMRATE_S.value as FAMRATE_S,
	dn_TR_FAM_NAT.value as TR_FAM_NAT,
	dn_SCRIPT_AN1.value as SCRIPT_AN1,
	dn_OWNRATE_S.value as OWNRATE_S,
	dn_TR_OWN_NAT.value as TR_OWN_NAT,
	dn_SCRIPT_AN0.value as SCRIPT_AN0,
	dn_INCRATE_S.value as INCRATE_S,
	dn_TR_MHI_NAT.value as TR_MHI_NAT,
	dn_HINC0_CY.value as HINC0_CY,
	dn_HINC0_CY_P.value as HINC0_CY_P,
	dn_HINC0_FY.value as HINC0_FY,
	dn_HINC0_FY_P.value as HINC0_FY_P,
	dn_HINC15_CY.value as HINC15_CY,
	dn_HINC15_CY_P.value as HINC15_CY_P,
	dn_HINC15_FY.value as HINC15_FY,
	dn_HINC15_FY_P.value as HINC15_FY_P,
	dn_HINC25_CY.value as HINC25_CY,
	dn_HINC25_CY_P.value as HINC25_CY_P,
	dn_HINC25_FY.value as HINC25_FY,
	dn_HINC25_FY_P.value as HINC25_FY_P,
	dn_HINC35_CY.value as HINC35_CY,
	dn_HINC35_CY_P.value as HINC35_CY_P,
	dn_HINC35_FY.value as HINC35_FY,
	dn_HINC35_FY_P.value as HINC35_FY_P,
	dn_HINC50_CY.value as HINC50_CY,
	dn_HINC50_CY_P.value as HINC50_CY_P,
	dn_HINC50_FY.value as HINC50_FY,
	dn_HINC50_FY_P.value as HINC50_FY_P,
	dn_HINC75_CY.value as HINC75_CY,
	dn_HINC75_CY_P.value as HINC75_CY_P,
	dn_HINC75_FY.value as HINC75_FY,
	dn_HINC75_FY_P.value as HINC75_FY_P,
	dn_HINC100_CY.value as HINC100_CY,
	dn_HINC100_CY_P.value as HINC100_CY_P,
	dn_HINC100_FY.value as HINC100_FY,
	dn_HINC100_FY_P.value as HINC100_FY_P,
	dn_HINC150_CY.value as HINC150_CY,
	dn_HINC150_CY_P.value as HINC150_CY_P,
	dn_HINC150_FY.value as HINC150_FY,
	dn_HINC150_FY_P.value as HINC150_FY_P,
	dn_HINC200_CY.value as HINC200_CY,
	dn_HINC200_CY_P.value as HINC200_CY_P,
	dn_HINC200_FY.value as HINC200_FY,
	dn_HINC200_FY_P.value as HINC200_FY_P,
	dn_MEDHINC_CY.value as MEDHINC_CY,
	dn_MEDHINC_FY.value as MEDHINC_FY,
	dn_AVGHINC_CY.value as AVGHINC_CY,
	dn_AVGHINC_FY.value as AVGHINC_FY,
	dn_PCI_CY.value as PCI_CY,
	dn_PCI_FY.value as PCI_FY,
	dn_POP0C10.value as POP0C10,
	dn_POP0C10_P.value as POP0C10_P,
	dn_POP0_CY.value as POP0_CY,
	dn_POP0_CY_P.value as POP0_CY_P,
	dn_POP0_FY.value as POP0_FY,
	dn_POP0_FY_P.value as POP0_FY_P,
	dn_POP5C10.value as POP5C10,
	dn_POP5C10_P.value as POP5C10_P,
	dn_POP5_CY.value as POP5_CY,
	dn_POP5_CY_P.value as POP5_CY_P,
	dn_POP5_FY.value as POP5_FY,
	dn_POP5_FY_P.value as POP5_FY_P,
	dn_POP10C10.value as POP10C10,
	dn_POP10C10_P.value as POP10C10_P,
	dn_POP10_CY.value as POP10_CY,
	dn_POP10_CY_P.value as POP10_CY_P,
	dn_POP10_FY.value as POP10_FY,
	dn_POP10_FY_P.value as POP10_FY_P,
	dn_POP15C10.value as POP15C10,
	dn_POP15C10_P.value as POP15C10_P,
	dn_POP15_CY.value as POP15_CY,
	dn_POP15_CY_P.value as POP15_CY_P,
	dn_POP15_FY.value as POP15_FY,
	dn_POP15_FY_P.value as POP15_FY_P,
	dn_POP20C10.value as POP20C10,
	dn_POP20C10_P.value as POP20C10_P,
	dn_POP20_CY.value as POP20_CY,
	dn_POP20_CY_P.value as POP20_CY_P,
	dn_POP20_FY.value as POP20_FY,
	dn_POP20_FY_P.value as POP20_FY_P,
	dn_POP2534C10.value as POP2534C10,
	dn_POP2534C10_P.value as POP2534C10_P,
	dn_POP2534_CY.value as POP2534_CY,
	dn_POP2534_CY_P.value as POP2534_CY_P,
	dn_POP2534_FY.value as POP2534_FY,
	dn_POP2534_FY_P.value as POP2534_FY_P,
	dn_POP3544C10.value as POP3544C10,
	dn_POP3544C10_P.value as POP3544C10_P,
	dn_POP3544_CY.value as POP3544_CY,
	dn_POP3544_CY_P.value as POP3544_CY_P,
	dn_POP3544_FY.value as POP3544_FY,
	dn_POP3544_FY_P.value as POP3544_FY_P,
	dn_POP4554C10.value as POP4554C10,
	dn_POP4554C10_P.value as POP4554C10_P,
	dn_POP4554_CY.value as POP4554_CY,
	dn_POP4554_CY_P.value as POP4554_CY_P,
	dn_POP4554_FY.value as POP4554_FY,
	dn_POP4554_FY_P.value as POP4554_FY_P,
	dn_POP5564C10.value as POP5564C10,
	dn_POP5564C10_P.value as POP5564C10_P,
	dn_POP5564_CY.value as POP5564_CY,
	dn_POP5564_CY_P.value as POP5564_CY_P,
	dn_POP5564_FY.value as POP5564_FY,
	dn_POP5564_FY_P.value as POP5564_FY_P,
	dn_POP6574C10.value as POP6574C10,
	dn_POP6574C10_P.value as POP6574C10_P,
	dn_POP6574_CY.value as POP6574_CY,
	dn_POP6574_CY_P.value as POP6574_CY_P,
	dn_POP6574_FY.value as POP6574_FY,
	dn_POP6574_FY_P.value as POP6574_FY_P,
	dn_POP7584C10.value as POP7584C10,
	dn_POP7584C10_P.value as POP7584C10_P,
	dn_POP7584_CY.value as POP7584_CY,
	dn_POP7584_CY_P.value as POP7584_CY_P,
	dn_POP7584_FY.value as POP7584_FY,
	dn_POP7584_FY_P.value as POP7584_FY_P,
	dn_POP85C10.value as POP85C10,
	dn_POP85PC10_P.value as POP85PC10_P,
	dn_POP85_CY.value as POP85_CY,
	dn_POP85P_CY_P.value as POP85P_CY_P,
	dn_POP85_FY.value as POP85_FY,
	dn_POP85P_FY_P.value as POP85P_FY_P,
	dn_WHITE10.value as WHITE10,
	dn_WHITE10_P.value as WHITE10_P,
	dn_WHITE_CY.value as WHITE_CY,
	dn_WHITE_CY_P.value as WHITE_CY_P,
	dn_WHITE_FY.value as WHITE_FY,
	dn_WHITE_FY_P.value as WHITE_FY_P,
	dn_BLACK10.value as BLACK10,
	dn_BLACK10_P.value as BLACK10_P,
	dn_BLACK_CY.value as BLACK_CY,
	dn_BLACK_CY_P.value as BLACK_CY_P,
	dn_BLACK_FY.value as BLACK_FY,
	dn_BLACK_FY_P.value as BLACK_FY_P,
	dn_AMERIND10.value as AMERIND10,
	dn_AMERIND10_P.value as AMERIND10_P,
	dn_AMERIND_CY.value as AMERIND_CY,
	dn_AMERIND_CY_P.value as AMERIND_CY_P,
	dn_AMERIND_FY.value as AMERIND_FY,
	dn_AMERIND_FY_P.value as AMERIND_FY_P,
	dn_ASIAN10.value as ASIAN10,
	dn_ASIAN10_P.value as ASIAN10_P,
	dn_ASIAN_CY.value as ASIAN_CY,
	dn_ASIAN_CY_P.value as ASIAN_CY_P,
	dn_ASIAN_FY.value as ASIAN_FY,
	dn_ASIAN_FY_P.value as ASIAN_FY_P,
	dn_PACIFIC10.value as PACIFIC10,
	dn_PACIFIC10_P.value as PACIFIC10_P,
	dn_PACIFIC_CY.value as PACIFIC_CY,
	dn_PACIFIC_CY_P.value as PACIFIC_CY_P,
	dn_PACIFIC_FY.value as PACIFIC_FY,
	dn_PACIFIC_FY_P.value as PACIFIC_FY_P,
	dn_OTHRACE10.value as OTHRACE10,
	dn_OTHRACE10_P.value as OTHRACE10_P,
	dn_OTHRACE_CY.value as OTHRACE_CY,
	dn_OTHRACE_CY_P.value as OTHRACE_CY_P,
	dn_OTHRACE_FY.value as OTHRACE_FY,
	dn_OTHRACE_FY_P.value as OTHRACE_FY_P,
	dn_RACE2UP10.value as RACE2UP10,
	dn_RACE2UP10_P.value as RACE2UP10_P,
	dn_RACE2UP_CY.value as RACE2UP_CY,
	dn_RACE2UP_CY_P.value as RACE2UP_CY_P,
	dn_RACE2UP_FY.value as RACE2UP_FY,
	dn_RACE2UP_FY_P.value as RACE2UP_FY_P,
	dn_HISPPOP10.value as HISPPOP10,
	dn_HISPPOP10_P.value as HISPPOP10_P,
	dn_HISPPOPCY.value as HISPPOPCY,
	dn_HISPPOP_CY_P.value as HISPPOP_CY_P,
	dn_HISPPOPFY.value as HISPPOPFY,
	dn_HISPPOPFY_P.value as HISPPOPFY_P,
	dn_POPRATE.value as POPRATE,
	dn_HHRATE.value as HHRATE,
	dn_FAMRATE.value as FAMRATE,
	dn_OWNRATE.value as OWNRATE,
	dn_INCRATE.value as INCRATE,
	dn_MALE0C10.value as MALE0C10,
	dn_MALE5C10.value as MALE5C10,
	dn_MALE10C10.value as MALE10C10,
	dn_MALE15C10.value as MALE15C10,
	dn_MALE20C10.value as MALE20C10,
	dn_MALE25C10.value as MALE25C10,
	dn_MALE30C10.value as MALE30C10,
	dn_MALE35C10.value as MALE35C10,
	dn_MALE40C10.value as MALE40C10,
	dn_MALE45C10.value as MALE45C10,
	dn_MALE50C10.value as MALE50C10,
	dn_MALE55C10.value as MALE55C10,
	dn_MALE60C10.value as MALE60C10,
	dn_MALE65C10.value as MALE65C10,
	dn_MALE70C10.value as MALE70C10,
	dn_MALE75C10.value as MALE75C10,
	dn_MALE80C10.value as MALE80C10,
	dn_MALE85C10.value as MALE85C10,
	dn_MAL18UP10.value as MAL18UP10,
	dn_MAL21UP10.value as MAL21UP10,
	dn_MEDMAGE10.value as MEDMAGE10,
	dn_FEM0C10.value as FEM0C10,
	dn_FEM5C10.value as FEM5C10,
	dn_FEM10C10.value as FEM10C10,
	dn_FEM15C10.value as FEM15C10,
	dn_FEM20C10.value as FEM20C10,
	dn_FEM25C10.value as FEM25C10,
	dn_FEM30C10.value as FEM30C10,
	dn_FEM35C10.value as FEM35C10,
	dn_FEM40C10.value as FEM40C10,
	dn_FEM45C10.value as FEM45C10,
	dn_FEM50C10.value as FEM50C10,
	dn_FEM55C10.value as FEM55C10,
	dn_FEM60C10.value as FEM60C10,
	dn_FEM65C10.value as FEM65C10,
	dn_FEM70C10.value as FEM70C10,
	dn_FEM75C10.value as FEM75C10,
	dn_FEM80C10.value as FEM80C10,
	dn_FEM85C10.value as FEM85C10,
	dn_FEM18UP10.value as FEM18UP10,
	dn_FEM21UP10.value as FEM21UP10,
	dn_MEDFAGE10.value as MEDFAGE10,
	(dn_TOTPOP_CY.value * dn_PCI_CY.value) as agg_income
	--case when (ISNULL(dn_Count_1.value / dn_Count_1.value, 0) + ISNULL(dn_Count_2.value / dn_Count_2.value, 0) + ISNULL(dn_Count_3.value / dn_Count_3.value, 0) + ISNULL(dn_Count_4.value / dn_Count_4.value, 0) + ISNULL(dn_Count_5.value / dn_Count_5.value, 0) + ISNULL(dn_Count_6.value / dn_Count_6.value, 0) + ISNULL(dn_Count_7.value / dn_Count_7.value, 0) + ISNULL(dn_Count_8.value / dn_Count_8.value, 0) + ISNULL(dn_Count_9.value / dn_Count_9.value, 0) + ISNULL(dn_Count_10.value / dn_Count_10.value, 0) + ISNULL(dn_Count_11.value / dn_Count_11.value, 0) + ISNULL(dn_Count_12.value / dn_Count_12.value, 0) + ISNULL(dn_Count_13.value / dn_Count_13.value, 0) + ISNULL(dn_Count_14.value / dn_Count_14.value, 0) + ISNULL(dn_Count_15.value / dn_Count_15.value, 0) + ISNULL(dn_Count_16.value / dn_Count_16.value, 0) + ISNULL(dn_Count_17.value / dn_Count_17.value, 0) + ISNULL(dn_Count_11.value / dn_Count_11.value, 0) + ISNULL(dn_Count_19.value / dn_Count_19.value, 0) + ISNULL(dn_Count_20.value / dn_Count_20.value, 0) + ISNULL(dn_Count_21.value / dn_Count_21.value, 0) + ISNULL(dn_Count_22.value / dn_Count_22.value, 0) + ISNULL(dn_Count_23.value / dn_Count_23.value, 0) + ISNULL(dn_Count_24.value / dn_Count_24.value, 0) + ISNULL(dn_Count_25.value / dn_Count_25.value, 0) + ISNULL(dn_Count_26.value / dn_Count_26.value, 0) + ISNULL(dn_Count_27.value / dn_Count_27.value, 0) + ISNULL(dn_Count_28.value / dn_Count_28.value, 0) + ISNULL(dn_Count_29.value / dn_Count_29.value, 0) + ISNULL(dn_Count_30.value / dn_Count_30.value, 0)) != 0
	--	then (ISNULL(dn_Count_1.value, 0) + ISNULL(dn_Count_2.value, 0) + ISNULL(dn_Count_3.value, 0) + ISNULL(dn_Count_4.value, 0) + ISNULL(dn_Count_5.value, 0) + ISNULL(dn_Count_6.value, 0) + ISNULL(dn_Count_7.value, 0) + ISNULL(dn_Count_8.value, 0) + ISNULL(dn_Count_9.value, 0) + ISNULL(dn_Count_10.value, 0) + ISNULL(dn_Count_11.value, 0) + ISNULL(dn_Count_12.value, 0) + ISNULL(dn_Count_13.value, 0) + ISNULL(dn_Count_14.value, 0) + ISNULL(dn_Count_15.value, 0) + ISNULL(dn_Count_16.value, 0) + ISNULL(dn_Count_17.value, 0) + ISNULL(dn_Count_11.value, 0) + ISNULL(dn_Count_19.value, 0) + ISNULL(dn_Count_20.value, 0) + ISNULL(dn_Count_21.value, 0) + ISNULL(dn_Count_22.value, 0) + ISNULL(dn_Count_23.value, 0) + ISNULL(dn_Count_24.value, 0) + ISNULL(dn_Count_25.value, 0) + ISNULL(dn_Count_26.value, 0) + ISNULL(dn_Count_27.value, 0) + ISNULL(dn_Count_28.value, 0) + ISNULL(dn_Count_29.value, 0) + ISNULL(dn_Count_30.value, 0)) / (ISNULL(dn_Count_1.value / dn_Count_1.value, 0) + ISNULL(dn_Count_2.value / dn_Count_2.value, 0) + ISNULL(dn_Count_3.value / dn_Count_3.value, 0) + ISNULL(dn_Count_4.value / dn_Count_4.value, 0) + ISNULL(dn_Count_5.value / dn_Count_5.value, 0) + ISNULL(dn_Count_6.value / dn_Count_6.value, 0) + ISNULL(dn_Count_7.value / dn_Count_7.value, 0) + ISNULL(dn_Count_8.value / dn_Count_8.value, 0) + ISNULL(dn_Count_9.value / dn_Count_9.value, 0) + ISNULL(dn_Count_10.value / dn_Count_10.value, 0) + ISNULL(dn_Count_11.value / dn_Count_11.value, 0) + ISNULL(dn_Count_12.value / dn_Count_12.value, 0) + ISNULL(dn_Count_13.value / dn_Count_13.value, 0) + ISNULL(dn_Count_14.value / dn_Count_14.value, 0) + ISNULL(dn_Count_15.value / dn_Count_15.value, 0) + ISNULL(dn_Count_16.value / dn_Count_16.value, 0) + ISNULL(dn_Count_17.value / dn_Count_17.value, 0) + ISNULL(dn_Count_11.value / dn_Count_11.value, 0) + ISNULL(dn_Count_19.value / dn_Count_19.value, 0) + ISNULL(dn_Count_20.value / dn_Count_20.value, 0) + ISNULL(dn_Count_21.value / dn_Count_21.value, 0) + ISNULL(dn_Count_22.value / dn_Count_22.value, 0) + ISNULL(dn_Count_23.value / dn_Count_23.value, 0) + ISNULL(dn_Count_24.value / dn_Count_24.value, 0) + ISNULL(dn_Count_25.value / dn_Count_25.value, 0) + ISNULL(dn_Count_26.value / dn_Count_26.value, 0) + ISNULL(dn_Count_27.value / dn_Count_27.value, 0) + ISNULL(dn_Count_28.value / dn_Count_28.value, 0) + ISNULL(dn_Count_29.value / dn_Count_29.value, 0) + ISNULL(dn_Count_30.value / dn_Count_30.value, 0))
	--	else 0
	--end as traffic,
	--ISNULL(dn_X6016_X.value, 0) + ISNULL(dn_X6011_X.value, 0) + ISNULL(dn_X6013_X.value, 0) + ISNULL(dn_X6018_X.value, 0) as auto_parts_DIY_proxy,
	--(ISNULL(dn_X6035_X.value, 0) + ISNULL(dn_X6024_X.value, 0) + ISNULL(dn_X6027_X.value, 0) + ISNULL(dn_X6025_X.value, 0) + ISNULL(dn_X6029_X.value, 0) + ISNULL(dn_X6026_X.value, 0) + ISNULL(dn_X6037_X.value, 0) + ISNULL(dn_X6036_X.value, 0) + ISNULL(dn_X6032_X.value, 0) + ISNULL(dn_X6031_X.value, 0) + ISNULL(dn_X6038_X.value, 0) + ISNULL(dn_X6030_X.value, 0) + ISNULL(dn_X6033_X.value, 0) + ISNULL(dn_X6028_X.value, 0) + ISNULL(dn_X6034_X.value, 0)) as auto_parts_DIFM_proxy,
	--(ISNULL(dn_ACSOVEH1.value, 0) * 1) + (ISNULL(dn_ACSOVEH2.value, 0) * 2) + (ISNULL(dn_ACSOVEH3.value, 0) * 3) + (ISNULL(dn_ACSOVEH4.value, 0) * 4) + (ISNULL(dn_ACSOVEH5UP.value, 0) * 5) + (ISNULL(dn_ACSRVEH1.value, 0) * 1) + (ISNULL(dn_ACSRVEH2.value, 0) * 2) + (ISNULL(dn_ACSRVEH3.value, 0) * 3) + (ISNULL(dn_ACSRVEH4.value, 0) * 4) + (ISNULL(dn_ACSRVEH5UP.value, 0) * 5) as auto_fleet,
	--CASE WHEN ISNULL(dn_ACSTRANBAS.value, 0) != 0
	--	THEN (ISNULL(dn_ACSDRALONE.value, 0) + ISNULL(dn_ACSCARPOOL.value, 0)) / ISNULL(dn_ACSTRANBAS.value, 0)
	--	ELSE 0
	--END as commutation_driving_pct,
	--CASE WHEN (ISNULL(dn_ACSTWRKBAS.value, 0) + ISNULL(dn_ACSTWORKU5.value, 0) + ISNULL(dn_ACSTWORK5.value, 0) + ISNULL(dn_ACSTWORK10.value, 0) + ISNULL(dn_ACSTWORK15.value, 0) + ISNULL(dn_ACSTWORK20.value, 0) + ISNULL(dn_ACSTWORK25.value, 0) + ISNULL(dn_ACSTWORK30.value, 0) + ISNULL(dn_ACSTWORK35.value, 0) + ISNULL(dn_ACSTWORK40.value, 0) + ISNULL(dn_ACSTWORK45.value, 0) + ISNULL(dn_ACSTWORK60.value, 0) + ISNULL(dn_ACSTWORK90.value, 0)) != 0
	--	THEN ((ISNULL(dn_ACSTWRKBAS.value, 0) * 3) + (ISNULL(dn_ACSTWORKU5.value, 0) * 7) + (ISNULL(dn_ACSTWORK5.value, 0) * 12) + (ISNULL(dn_ACSTWORK10.value, 0) * 17) + (ISNULL(dn_ACSTWORK15.value, 0) * 22) + (ISNULL(dn_ACSTWORK20.value, 0) * 27) + (ISNULL(dn_ACSTWORK25.value, 0) * 32) + (ISNULL(dn_ACSTWORK30.value, 0) * 37) + (ISNULL(dn_ACSTWORK35.value, 0) * 42) + (ISNULL(dn_ACSTWORK40.value, 0) * 47) + (ISNULL(dn_ACSTWORK45.value, 0) * 52) + (ISNULL(dn_ACSTWORK60.value, 0) * 74.5) + (ISNULL(dn_ACSTWORK90.value, 0) * 90)) / (ISNULL(dn_ACSTWRKBAS.value, 0) + ISNULL(dn_ACSTWORKU5.value, 0) + ISNULL(dn_ACSTWORK5.value, 0) + ISNULL(dn_ACSTWORK10.value, 0) + ISNULL(dn_ACSTWORK15.value, 0) + ISNULL(dn_ACSTWORK20.value, 0) + ISNULL(dn_ACSTWORK25.value, 0) + ISNULL(dn_ACSTWORK30.value, 0) + ISNULL(dn_ACSTWORK35.value, 0) + ISNULL(dn_ACSTWORK40.value, 0) + ISNULL(dn_ACSTWORK45.value, 0) + ISNULL(dn_ACSTWORK60.value, 0) + ISNULL(dn_ACSTWORK90.value, 0))
	--	ELSE 0
	--END as commutation_commute_time,	
	--ISNULL(dn_Count_1.value, 0) + ISNULL(dn_Count_2.value, 0) + ISNULL(dn_Count_3.value, 0) + ISNULL(dn_Count_4.value, 0) + ISNULL(dn_Count_5.value, 0) + ISNULL(dn_Count_6.value, 0) + ISNULL(dn_Count_7.value, 0) + ISNULL(dn_Count_8.value, 0) + ISNULL(dn_Count_9.value, 0) + ISNULL(dn_Count_10.value, 0) + ISNULL(dn_Count_11.value, 0) + ISNULL(dn_Count_12.value, 0) + ISNULL(dn_Count_13.value, 0) + ISNULL(dn_Count_14.value, 0) + ISNULL(dn_Count_15.value, 0) + ISNULL(dn_Count_16.value, 0) + ISNULL(dn_Count_17.value, 0) + ISNULL(dn_Count_11.value, 0) + ISNULL(dn_Count_19.value, 0) + ISNULL(dn_Count_20.value, 0) + ISNULL(dn_Count_21.value, 0) + ISNULL(dn_Count_22.value, 0) + ISNULL(dn_Count_23.value, 0) + ISNULL(dn_Count_24.value, 0) + ISNULL(dn_Count_25.value, 0) + ISNULL(dn_Count_26.value, 0) + ISNULL(dn_Count_27.value, 0) + ISNULL(dn_Count_28.value, 0) + ISNULL(dn_Count_29.value, 0) + ISNULL(dn_Count_30.value, 0) as traffic_summed,
	--(ISNULL(dn_Count_1.value, 0) / (1 + dn_Distance_1.value)) + (ISNULL(dn_Count_2.value, 0) / (1 + dn_Distance_2.value)) + (ISNULL(dn_Count_3.value, 0) / (1 + dn_Distance_3.value)) + (ISNULL(dn_Count_4.value, 0) / (1 + dn_Distance_4.value)) + (ISNULL(dn_Count_5.value, 0) / (1 + dn_Distance_5.value)) + (ISNULL(dn_Count_6.value, 0) / (1 + dn_Distance_6.value)) + (ISNULL(dn_Count_7.value, 0) / (1 + dn_Distance_7.value)) + (ISNULL(dn_Count_8.value, 0) / (1 + dn_Distance_8.value)) + (ISNULL(dn_Count_9.value, 0) / (1 + dn_Distance_9.value)) + (ISNULL(dn_Count_10.value, 0) / (1 + dn_Distance_10.value)) + (ISNULL(dn_Count_11.value, 0) / (1 + dn_Distance_11.value)) + (ISNULL(dn_Count_12.value, 0) / (1 + dn_Distance_12.value)) + (ISNULL(dn_Count_13.value, 0) / (1 + dn_Distance_13.value)) + (ISNULL(dn_Count_14.value, 0) / (1 + dn_Distance_14.value)) + (ISNULL(dn_Count_15.value, 0) / (1 + dn_Distance_15.value)) + (ISNULL(dn_Count_16.value, 0) / (1 + dn_Distance_16.value)) + (ISNULL(dn_Count_17.value, 0) / (1 + dn_Distance_17.value)) + (ISNULL(dn_Count_11.value, 0) / (1 + dn_Distance_11.value)) + (ISNULL(dn_Count_19.value, 0) / (1 + dn_Distance_19.value)) + (ISNULL(dn_Count_20.value, 0) / (1 + dn_Distance_20.value)) + (ISNULL(dn_Count_21.value, 0) / (1 + dn_Distance_21.value)) + (ISNULL(dn_Count_22.value, 0) / (1 + dn_Distance_22.value)) + (ISNULL(dn_Count_23.value, 0) / (1 + dn_Distance_23.value)) + (ISNULL(dn_Count_24.value, 0) / (1 + dn_Distance_24.value)) + (ISNULL(dn_Count_25.value, 0) / (1 + dn_Distance_25.value)) + (ISNULL(dn_Count_26.value, 0) / (1 + dn_Distance_26.value)) + (ISNULL(dn_Count_27.value, 0) / (1 + dn_Distance_27.value)) + (ISNULL(dn_Count_28.value, 0) / (1 + dn_Distance_28.value)) + (ISNULL(dn_Count_29.value, 0) / (1 + dn_Distance_29.value)) + (ISNULL(dn_Count_30.value, 0) / (1 + dn_Distance_30.value)) as traffic_weighted_distance
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
inner join companies c on c.company_id = s.company_id
--inner join demographic_numvalues dn on dn.trade_area_id = t.trade_area_id
--inner join data_items di on di.data_item_id = dn.data_item_id
left join demographic_numvalues dn_TOTPOP10 on dn_TOTPOP10.trade_area_id = t.trade_area_id and dn_TOTPOP10.data_item_id = 12
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13
left join demographic_numvalues dn_TOTPOP_FY on dn_TOTPOP_FY.trade_area_id = t.trade_area_id and dn_TOTPOP_FY.data_item_id = 14
left join demographic_numvalues dn_TOTHH10 on dn_TOTHH10.trade_area_id = t.trade_area_id and dn_TOTHH10.data_item_id = 15
left join demographic_numvalues dn_TOTHH_CY on dn_TOTHH_CY.trade_area_id = t.trade_area_id and dn_TOTHH_CY.data_item_id = 16
left join demographic_numvalues dn_TOTHH_FY on dn_TOTHH_FY.trade_area_id = t.trade_area_id and dn_TOTHH_FY.data_item_id = 17
left join demographic_numvalues dn_FAMHH10 on dn_FAMHH10.trade_area_id = t.trade_area_id and dn_FAMHH10.data_item_id = 18
left join demographic_numvalues dn_FAMHH_CY on dn_FAMHH_CY.trade_area_id = t.trade_area_id and dn_FAMHH_CY.data_item_id = 19
left join demographic_numvalues dn_FAMHH_FY on dn_FAMHH_FY.trade_area_id = t.trade_area_id and dn_FAMHH_FY.data_item_id = 20
left join demographic_numvalues dn_AVGHHSZ10 on dn_AVGHHSZ10.trade_area_id = t.trade_area_id and dn_AVGHHSZ10.data_item_id = 21
left join demographic_numvalues dn_AVGHHSZ_CY on dn_AVGHHSZ_CY.trade_area_id = t.trade_area_id and dn_AVGHHSZ_CY.data_item_id = 22
left join demographic_numvalues dn_AVGHHSZ_FY on dn_AVGHHSZ_FY.trade_area_id = t.trade_area_id and dn_AVGHHSZ_FY.data_item_id = 23
left join demographic_numvalues dn_OWNER10 on dn_OWNER10.trade_area_id = t.trade_area_id and dn_OWNER10.data_item_id = 24
left join demographic_numvalues dn_OWNER_CY on dn_OWNER_CY.trade_area_id = t.trade_area_id and dn_OWNER_CY.data_item_id = 25
left join demographic_numvalues dn_OWNER_FY on dn_OWNER_FY.trade_area_id = t.trade_area_id and dn_OWNER_FY.data_item_id = 26
left join demographic_numvalues dn_RENTER10 on dn_RENTER10.trade_area_id = t.trade_area_id and dn_RENTER10.data_item_id = 27
left join demographic_numvalues dn_RENTER_CY on dn_RENTER_CY.trade_area_id = t.trade_area_id and dn_RENTER_CY.data_item_id = 28
left join demographic_numvalues dn_RENTER_FY on dn_RENTER_FY.trade_area_id = t.trade_area_id and dn_RENTER_FY.data_item_id = 29
left join demographic_numvalues dn_MEDAGE10 on dn_MEDAGE10.trade_area_id = t.trade_area_id and dn_MEDAGE10.data_item_id = 30
left join demographic_numvalues dn_MEDAGE_CY on dn_MEDAGE_CY.trade_area_id = t.trade_area_id and dn_MEDAGE_CY.data_item_id = 31
left join demographic_numvalues dn_MEDAGE_FY on dn_MEDAGE_FY.trade_area_id = t.trade_area_id and dn_MEDAGE_FY.data_item_id = 32
left join demographic_numvalues dn_SCRIPT_ANU on dn_SCRIPT_ANU.trade_area_id = t.trade_area_id and dn_SCRIPT_ANU.data_item_id = 33
left join demographic_numvalues dn_POPRATE_S on dn_POPRATE_S.trade_area_id = t.trade_area_id and dn_POPRATE_S.data_item_id = 34
left join demographic_numvalues dn_TR_POP_NAT on dn_TR_POP_NAT.trade_area_id = t.trade_area_id and dn_TR_POP_NAT.data_item_id = 35
left join demographic_numvalues dn_SCRIPT_A_1 on dn_SCRIPT_A_1.trade_area_id = t.trade_area_id and dn_SCRIPT_A_1.data_item_id = 36
left join demographic_numvalues dn_HHRATE_S on dn_HHRATE_S.trade_area_id = t.trade_area_id and dn_HHRATE_S.data_item_id = 37
left join demographic_numvalues dn_TR_HH_NAT on dn_TR_HH_NAT.trade_area_id = t.trade_area_id and dn_TR_HH_NAT.data_item_id = 38
left join demographic_numvalues dn_SCRIPT_A_2 on dn_SCRIPT_A_2.trade_area_id = t.trade_area_id and dn_SCRIPT_A_2.data_item_id = 39
left join demographic_numvalues dn_FAMRATE_S on dn_FAMRATE_S.trade_area_id = t.trade_area_id and dn_FAMRATE_S.data_item_id = 40
left join demographic_numvalues dn_TR_FAM_NAT on dn_TR_FAM_NAT.trade_area_id = t.trade_area_id and dn_TR_FAM_NAT.data_item_id = 41
left join demographic_numvalues dn_SCRIPT_AN1 on dn_SCRIPT_AN1.trade_area_id = t.trade_area_id and dn_SCRIPT_AN1.data_item_id = 42
left join demographic_numvalues dn_OWNRATE_S on dn_OWNRATE_S.trade_area_id = t.trade_area_id and dn_OWNRATE_S.data_item_id = 43
left join demographic_numvalues dn_TR_OWN_NAT on dn_TR_OWN_NAT.trade_area_id = t.trade_area_id and dn_TR_OWN_NAT.data_item_id = 44
left join demographic_numvalues dn_SCRIPT_AN0 on dn_SCRIPT_AN0.trade_area_id = t.trade_area_id and dn_SCRIPT_AN0.data_item_id = 45
left join demographic_numvalues dn_INCRATE_S on dn_INCRATE_S.trade_area_id = t.trade_area_id and dn_INCRATE_S.data_item_id = 46
left join demographic_numvalues dn_TR_MHI_NAT on dn_TR_MHI_NAT.trade_area_id = t.trade_area_id and dn_TR_MHI_NAT.data_item_id = 47
left join demographic_numvalues dn_HINC0_CY on dn_HINC0_CY.trade_area_id = t.trade_area_id and dn_HINC0_CY.data_item_id = 48
left join demographic_numvalues dn_HINC0_CY_P on dn_HINC0_CY_P.trade_area_id = t.trade_area_id and dn_HINC0_CY_P.data_item_id = 49
left join demographic_numvalues dn_HINC0_FY on dn_HINC0_FY.trade_area_id = t.trade_area_id and dn_HINC0_FY.data_item_id = 50
left join demographic_numvalues dn_HINC0_FY_P on dn_HINC0_FY_P.trade_area_id = t.trade_area_id and dn_HINC0_FY_P.data_item_id = 51
left join demographic_numvalues dn_HINC15_CY on dn_HINC15_CY.trade_area_id = t.trade_area_id and dn_HINC15_CY.data_item_id = 52
left join demographic_numvalues dn_HINC15_CY_P on dn_HINC15_CY_P.trade_area_id = t.trade_area_id and dn_HINC15_CY_P.data_item_id = 53
left join demographic_numvalues dn_HINC15_FY on dn_HINC15_FY.trade_area_id = t.trade_area_id and dn_HINC15_FY.data_item_id = 54
left join demographic_numvalues dn_HINC15_FY_P on dn_HINC15_FY_P.trade_area_id = t.trade_area_id and dn_HINC15_FY_P.data_item_id = 55
left join demographic_numvalues dn_HINC25_CY on dn_HINC25_CY.trade_area_id = t.trade_area_id and dn_HINC25_CY.data_item_id = 56
left join demographic_numvalues dn_HINC25_CY_P on dn_HINC25_CY_P.trade_area_id = t.trade_area_id and dn_HINC25_CY_P.data_item_id = 57
left join demographic_numvalues dn_HINC25_FY on dn_HINC25_FY.trade_area_id = t.trade_area_id and dn_HINC25_FY.data_item_id = 58
left join demographic_numvalues dn_HINC25_FY_P on dn_HINC25_FY_P.trade_area_id = t.trade_area_id and dn_HINC25_FY_P.data_item_id = 59
left join demographic_numvalues dn_HINC35_CY on dn_HINC35_CY.trade_area_id = t.trade_area_id and dn_HINC35_CY.data_item_id = 60
left join demographic_numvalues dn_HINC35_CY_P on dn_HINC35_CY_P.trade_area_id = t.trade_area_id and dn_HINC35_CY_P.data_item_id = 61
left join demographic_numvalues dn_HINC35_FY on dn_HINC35_FY.trade_area_id = t.trade_area_id and dn_HINC35_FY.data_item_id = 62
left join demographic_numvalues dn_HINC35_FY_P on dn_HINC35_FY_P.trade_area_id = t.trade_area_id and dn_HINC35_FY_P.data_item_id = 63
left join demographic_numvalues dn_HINC50_CY on dn_HINC50_CY.trade_area_id = t.trade_area_id and dn_HINC50_CY.data_item_id = 64
left join demographic_numvalues dn_HINC50_CY_P on dn_HINC50_CY_P.trade_area_id = t.trade_area_id and dn_HINC50_CY_P.data_item_id = 65
left join demographic_numvalues dn_HINC50_FY on dn_HINC50_FY.trade_area_id = t.trade_area_id and dn_HINC50_FY.data_item_id = 66
left join demographic_numvalues dn_HINC50_FY_P on dn_HINC50_FY_P.trade_area_id = t.trade_area_id and dn_HINC50_FY_P.data_item_id = 67
left join demographic_numvalues dn_HINC75_CY on dn_HINC75_CY.trade_area_id = t.trade_area_id and dn_HINC75_CY.data_item_id = 68
left join demographic_numvalues dn_HINC75_CY_P on dn_HINC75_CY_P.trade_area_id = t.trade_area_id and dn_HINC75_CY_P.data_item_id = 69
left join demographic_numvalues dn_HINC75_FY on dn_HINC75_FY.trade_area_id = t.trade_area_id and dn_HINC75_FY.data_item_id = 70
left join demographic_numvalues dn_HINC75_FY_P on dn_HINC75_FY_P.trade_area_id = t.trade_area_id and dn_HINC75_FY_P.data_item_id = 71
left join demographic_numvalues dn_HINC100_CY on dn_HINC100_CY.trade_area_id = t.trade_area_id and dn_HINC100_CY.data_item_id = 72
left join demographic_numvalues dn_HINC100_CY_P on dn_HINC100_CY_P.trade_area_id = t.trade_area_id and dn_HINC100_CY_P.data_item_id = 73
left join demographic_numvalues dn_HINC100_FY on dn_HINC100_FY.trade_area_id = t.trade_area_id and dn_HINC100_FY.data_item_id = 74
left join demographic_numvalues dn_HINC100_FY_P on dn_HINC100_FY_P.trade_area_id = t.trade_area_id and dn_HINC100_FY_P.data_item_id = 75
left join demographic_numvalues dn_HINC150_CY on dn_HINC150_CY.trade_area_id = t.trade_area_id and dn_HINC150_CY.data_item_id = 76
left join demographic_numvalues dn_HINC150_CY_P on dn_HINC150_CY_P.trade_area_id = t.trade_area_id and dn_HINC150_CY_P.data_item_id = 77
left join demographic_numvalues dn_HINC150_FY on dn_HINC150_FY.trade_area_id = t.trade_area_id and dn_HINC150_FY.data_item_id = 78
left join demographic_numvalues dn_HINC150_FY_P on dn_HINC150_FY_P.trade_area_id = t.trade_area_id and dn_HINC150_FY_P.data_item_id = 79
left join demographic_numvalues dn_HINC200_CY on dn_HINC200_CY.trade_area_id = t.trade_area_id and dn_HINC200_CY.data_item_id = 80
left join demographic_numvalues dn_HINC200_CY_P on dn_HINC200_CY_P.trade_area_id = t.trade_area_id and dn_HINC200_CY_P.data_item_id = 81
left join demographic_numvalues dn_HINC200_FY on dn_HINC200_FY.trade_area_id = t.trade_area_id and dn_HINC200_FY.data_item_id = 82
left join demographic_numvalues dn_HINC200_FY_P on dn_HINC200_FY_P.trade_area_id = t.trade_area_id and dn_HINC200_FY_P.data_item_id = 83
left join demographic_numvalues dn_MEDHINC_CY on dn_MEDHINC_CY.trade_area_id = t.trade_area_id and dn_MEDHINC_CY.data_item_id = 84
left join demographic_numvalues dn_MEDHINC_FY on dn_MEDHINC_FY.trade_area_id = t.trade_area_id and dn_MEDHINC_FY.data_item_id = 85
left join demographic_numvalues dn_AVGHINC_CY on dn_AVGHINC_CY.trade_area_id = t.trade_area_id and dn_AVGHINC_CY.data_item_id = 86
left join demographic_numvalues dn_AVGHINC_FY on dn_AVGHINC_FY.trade_area_id = t.trade_area_id and dn_AVGHINC_FY.data_item_id = 87
left join demographic_numvalues dn_PCI_CY on dn_PCI_CY.trade_area_id = t.trade_area_id and dn_PCI_CY.data_item_id = 88
left join demographic_numvalues dn_PCI_FY on dn_PCI_FY.trade_area_id = t.trade_area_id and dn_PCI_FY.data_item_id = 89
left join demographic_numvalues dn_POP0C10 on dn_POP0C10.trade_area_id = t.trade_area_id and dn_POP0C10.data_item_id = 90
left join demographic_numvalues dn_POP0C10_P on dn_POP0C10_P.trade_area_id = t.trade_area_id and dn_POP0C10_P.data_item_id = 91
left join demographic_numvalues dn_POP0_CY on dn_POP0_CY.trade_area_id = t.trade_area_id and dn_POP0_CY.data_item_id = 92
left join demographic_numvalues dn_POP0_CY_P on dn_POP0_CY_P.trade_area_id = t.trade_area_id and dn_POP0_CY_P.data_item_id = 93
left join demographic_numvalues dn_POP0_FY on dn_POP0_FY.trade_area_id = t.trade_area_id and dn_POP0_FY.data_item_id = 94
left join demographic_numvalues dn_POP0_FY_P on dn_POP0_FY_P.trade_area_id = t.trade_area_id and dn_POP0_FY_P.data_item_id = 95
left join demographic_numvalues dn_POP5C10 on dn_POP5C10.trade_area_id = t.trade_area_id and dn_POP5C10.data_item_id = 96
left join demographic_numvalues dn_POP5C10_P on dn_POP5C10_P.trade_area_id = t.trade_area_id and dn_POP5C10_P.data_item_id = 97
left join demographic_numvalues dn_POP5_CY on dn_POP5_CY.trade_area_id = t.trade_area_id and dn_POP5_CY.data_item_id = 98
left join demographic_numvalues dn_POP5_CY_P on dn_POP5_CY_P.trade_area_id = t.trade_area_id and dn_POP5_CY_P.data_item_id = 99
left join demographic_numvalues dn_POP5_FY on dn_POP5_FY.trade_area_id = t.trade_area_id and dn_POP5_FY.data_item_id = 100
left join demographic_numvalues dn_POP5_FY_P on dn_POP5_FY_P.trade_area_id = t.trade_area_id and dn_POP5_FY_P.data_item_id = 101
left join demographic_numvalues dn_POP10C10 on dn_POP10C10.trade_area_id = t.trade_area_id and dn_POP10C10.data_item_id = 102
left join demographic_numvalues dn_POP10C10_P on dn_POP10C10_P.trade_area_id = t.trade_area_id and dn_POP10C10_P.data_item_id = 103
left join demographic_numvalues dn_POP10_CY on dn_POP10_CY.trade_area_id = t.trade_area_id and dn_POP10_CY.data_item_id = 104
left join demographic_numvalues dn_POP10_CY_P on dn_POP10_CY_P.trade_area_id = t.trade_area_id and dn_POP10_CY_P.data_item_id = 105
left join demographic_numvalues dn_POP10_FY on dn_POP10_FY.trade_area_id = t.trade_area_id and dn_POP10_FY.data_item_id = 106
left join demographic_numvalues dn_POP10_FY_P on dn_POP10_FY_P.trade_area_id = t.trade_area_id and dn_POP10_FY_P.data_item_id = 107
left join demographic_numvalues dn_POP15C10 on dn_POP15C10.trade_area_id = t.trade_area_id and dn_POP15C10.data_item_id = 108
left join demographic_numvalues dn_POP15C10_P on dn_POP15C10_P.trade_area_id = t.trade_area_id and dn_POP15C10_P.data_item_id = 109
left join demographic_numvalues dn_POP15_CY on dn_POP15_CY.trade_area_id = t.trade_area_id and dn_POP15_CY.data_item_id = 110
left join demographic_numvalues dn_POP15_CY_P on dn_POP15_CY_P.trade_area_id = t.trade_area_id and dn_POP15_CY_P.data_item_id = 111
left join demographic_numvalues dn_POP15_FY on dn_POP15_FY.trade_area_id = t.trade_area_id and dn_POP15_FY.data_item_id = 112
left join demographic_numvalues dn_POP15_FY_P on dn_POP15_FY_P.trade_area_id = t.trade_area_id and dn_POP15_FY_P.data_item_id = 113
left join demographic_numvalues dn_POP20C10 on dn_POP20C10.trade_area_id = t.trade_area_id and dn_POP20C10.data_item_id = 114
left join demographic_numvalues dn_POP20C10_P on dn_POP20C10_P.trade_area_id = t.trade_area_id and dn_POP20C10_P.data_item_id = 115
left join demographic_numvalues dn_POP20_CY on dn_POP20_CY.trade_area_id = t.trade_area_id and dn_POP20_CY.data_item_id = 116
left join demographic_numvalues dn_POP20_CY_P on dn_POP20_CY_P.trade_area_id = t.trade_area_id and dn_POP20_CY_P.data_item_id = 117
left join demographic_numvalues dn_POP20_FY on dn_POP20_FY.trade_area_id = t.trade_area_id and dn_POP20_FY.data_item_id = 118
left join demographic_numvalues dn_POP20_FY_P on dn_POP20_FY_P.trade_area_id = t.trade_area_id and dn_POP20_FY_P.data_item_id = 119
left join demographic_numvalues dn_POP2534C10 on dn_POP2534C10.trade_area_id = t.trade_area_id and dn_POP2534C10.data_item_id = 120
left join demographic_numvalues dn_POP2534C10_P on dn_POP2534C10_P.trade_area_id = t.trade_area_id and dn_POP2534C10_P.data_item_id = 121
left join demographic_numvalues dn_POP2534_CY on dn_POP2534_CY.trade_area_id = t.trade_area_id and dn_POP2534_CY.data_item_id = 122
left join demographic_numvalues dn_POP2534_CY_P on dn_POP2534_CY_P.trade_area_id = t.trade_area_id and dn_POP2534_CY_P.data_item_id = 123
left join demographic_numvalues dn_POP2534_FY on dn_POP2534_FY.trade_area_id = t.trade_area_id and dn_POP2534_FY.data_item_id = 124
left join demographic_numvalues dn_POP2534_FY_P on dn_POP2534_FY_P.trade_area_id = t.trade_area_id and dn_POP2534_FY_P.data_item_id = 125
left join demographic_numvalues dn_POP3544C10 on dn_POP3544C10.trade_area_id = t.trade_area_id and dn_POP3544C10.data_item_id = 126
left join demographic_numvalues dn_POP3544C10_P on dn_POP3544C10_P.trade_area_id = t.trade_area_id and dn_POP3544C10_P.data_item_id = 127
left join demographic_numvalues dn_POP3544_CY on dn_POP3544_CY.trade_area_id = t.trade_area_id and dn_POP3544_CY.data_item_id = 128
left join demographic_numvalues dn_POP3544_CY_P on dn_POP3544_CY_P.trade_area_id = t.trade_area_id and dn_POP3544_CY_P.data_item_id = 129
left join demographic_numvalues dn_POP3544_FY on dn_POP3544_FY.trade_area_id = t.trade_area_id and dn_POP3544_FY.data_item_id = 130
left join demographic_numvalues dn_POP3544_FY_P on dn_POP3544_FY_P.trade_area_id = t.trade_area_id and dn_POP3544_FY_P.data_item_id = 131
left join demographic_numvalues dn_POP4554C10 on dn_POP4554C10.trade_area_id = t.trade_area_id and dn_POP4554C10.data_item_id = 132
left join demographic_numvalues dn_POP4554C10_P on dn_POP4554C10_P.trade_area_id = t.trade_area_id and dn_POP4554C10_P.data_item_id = 133
left join demographic_numvalues dn_POP4554_CY on dn_POP4554_CY.trade_area_id = t.trade_area_id and dn_POP4554_CY.data_item_id = 134
left join demographic_numvalues dn_POP4554_CY_P on dn_POP4554_CY_P.trade_area_id = t.trade_area_id and dn_POP4554_CY_P.data_item_id = 135
left join demographic_numvalues dn_POP4554_FY on dn_POP4554_FY.trade_area_id = t.trade_area_id and dn_POP4554_FY.data_item_id = 136
left join demographic_numvalues dn_POP4554_FY_P on dn_POP4554_FY_P.trade_area_id = t.trade_area_id and dn_POP4554_FY_P.data_item_id = 137
left join demographic_numvalues dn_POP5564C10 on dn_POP5564C10.trade_area_id = t.trade_area_id and dn_POP5564C10.data_item_id = 138
left join demographic_numvalues dn_POP5564C10_P on dn_POP5564C10_P.trade_area_id = t.trade_area_id and dn_POP5564C10_P.data_item_id = 139
left join demographic_numvalues dn_POP5564_CY on dn_POP5564_CY.trade_area_id = t.trade_area_id and dn_POP5564_CY.data_item_id = 140
left join demographic_numvalues dn_POP5564_CY_P on dn_POP5564_CY_P.trade_area_id = t.trade_area_id and dn_POP5564_CY_P.data_item_id = 141
left join demographic_numvalues dn_POP5564_FY on dn_POP5564_FY.trade_area_id = t.trade_area_id and dn_POP5564_FY.data_item_id = 142
left join demographic_numvalues dn_POP5564_FY_P on dn_POP5564_FY_P.trade_area_id = t.trade_area_id and dn_POP5564_FY_P.data_item_id = 143
left join demographic_numvalues dn_POP6574C10 on dn_POP6574C10.trade_area_id = t.trade_area_id and dn_POP6574C10.data_item_id = 144
left join demographic_numvalues dn_POP6574C10_P on dn_POP6574C10_P.trade_area_id = t.trade_area_id and dn_POP6574C10_P.data_item_id = 145
left join demographic_numvalues dn_POP6574_CY on dn_POP6574_CY.trade_area_id = t.trade_area_id and dn_POP6574_CY.data_item_id = 146
left join demographic_numvalues dn_POP6574_CY_P on dn_POP6574_CY_P.trade_area_id = t.trade_area_id and dn_POP6574_CY_P.data_item_id = 147
left join demographic_numvalues dn_POP6574_FY on dn_POP6574_FY.trade_area_id = t.trade_area_id and dn_POP6574_FY.data_item_id = 148
left join demographic_numvalues dn_POP6574_FY_P on dn_POP6574_FY_P.trade_area_id = t.trade_area_id and dn_POP6574_FY_P.data_item_id = 149
left join demographic_numvalues dn_POP7584C10 on dn_POP7584C10.trade_area_id = t.trade_area_id and dn_POP7584C10.data_item_id = 150
left join demographic_numvalues dn_POP7584C10_P on dn_POP7584C10_P.trade_area_id = t.trade_area_id and dn_POP7584C10_P.data_item_id = 151
left join demographic_numvalues dn_POP7584_CY on dn_POP7584_CY.trade_area_id = t.trade_area_id and dn_POP7584_CY.data_item_id = 152
left join demographic_numvalues dn_POP7584_CY_P on dn_POP7584_CY_P.trade_area_id = t.trade_area_id and dn_POP7584_CY_P.data_item_id = 153
left join demographic_numvalues dn_POP7584_FY on dn_POP7584_FY.trade_area_id = t.trade_area_id and dn_POP7584_FY.data_item_id = 154
left join demographic_numvalues dn_POP7584_FY_P on dn_POP7584_FY_P.trade_area_id = t.trade_area_id and dn_POP7584_FY_P.data_item_id = 155
left join demographic_numvalues dn_POP85C10 on dn_POP85C10.trade_area_id = t.trade_area_id and dn_POP85C10.data_item_id = 156
left join demographic_numvalues dn_POP85PC10_P on dn_POP85PC10_P.trade_area_id = t.trade_area_id and dn_POP85PC10_P.data_item_id = 157
left join demographic_numvalues dn_POP85_CY on dn_POP85_CY.trade_area_id = t.trade_area_id and dn_POP85_CY.data_item_id = 158
left join demographic_numvalues dn_POP85P_CY_P on dn_POP85P_CY_P.trade_area_id = t.trade_area_id and dn_POP85P_CY_P.data_item_id = 159
left join demographic_numvalues dn_POP85_FY on dn_POP85_FY.trade_area_id = t.trade_area_id and dn_POP85_FY.data_item_id = 160
left join demographic_numvalues dn_POP85P_FY_P on dn_POP85P_FY_P.trade_area_id = t.trade_area_id and dn_POP85P_FY_P.data_item_id = 161
left join demographic_numvalues dn_WHITE10 on dn_WHITE10.trade_area_id = t.trade_area_id and dn_WHITE10.data_item_id = 162
left join demographic_numvalues dn_WHITE10_P on dn_WHITE10_P.trade_area_id = t.trade_area_id and dn_WHITE10_P.data_item_id = 163
left join demographic_numvalues dn_WHITE_CY on dn_WHITE_CY.trade_area_id = t.trade_area_id and dn_WHITE_CY.data_item_id = 164
left join demographic_numvalues dn_WHITE_CY_P on dn_WHITE_CY_P.trade_area_id = t.trade_area_id and dn_WHITE_CY_P.data_item_id = 165
left join demographic_numvalues dn_WHITE_FY on dn_WHITE_FY.trade_area_id = t.trade_area_id and dn_WHITE_FY.data_item_id = 166
left join demographic_numvalues dn_WHITE_FY_P on dn_WHITE_FY_P.trade_area_id = t.trade_area_id and dn_WHITE_FY_P.data_item_id = 167
left join demographic_numvalues dn_BLACK10 on dn_BLACK10.trade_area_id = t.trade_area_id and dn_BLACK10.data_item_id = 168
left join demographic_numvalues dn_BLACK10_P on dn_BLACK10_P.trade_area_id = t.trade_area_id and dn_BLACK10_P.data_item_id = 169
left join demographic_numvalues dn_BLACK_CY on dn_BLACK_CY.trade_area_id = t.trade_area_id and dn_BLACK_CY.data_item_id = 170
left join demographic_numvalues dn_BLACK_CY_P on dn_BLACK_CY_P.trade_area_id = t.trade_area_id and dn_BLACK_CY_P.data_item_id = 171
left join demographic_numvalues dn_BLACK_FY on dn_BLACK_FY.trade_area_id = t.trade_area_id and dn_BLACK_FY.data_item_id = 172
left join demographic_numvalues dn_BLACK_FY_P on dn_BLACK_FY_P.trade_area_id = t.trade_area_id and dn_BLACK_FY_P.data_item_id = 173
left join demographic_numvalues dn_AMERIND10 on dn_AMERIND10.trade_area_id = t.trade_area_id and dn_AMERIND10.data_item_id = 174
left join demographic_numvalues dn_AMERIND10_P on dn_AMERIND10_P.trade_area_id = t.trade_area_id and dn_AMERIND10_P.data_item_id = 175
left join demographic_numvalues dn_AMERIND_CY on dn_AMERIND_CY.trade_area_id = t.trade_area_id and dn_AMERIND_CY.data_item_id = 176
left join demographic_numvalues dn_AMERIND_CY_P on dn_AMERIND_CY_P.trade_area_id = t.trade_area_id and dn_AMERIND_CY_P.data_item_id = 177
left join demographic_numvalues dn_AMERIND_FY on dn_AMERIND_FY.trade_area_id = t.trade_area_id and dn_AMERIND_FY.data_item_id = 178
left join demographic_numvalues dn_AMERIND_FY_P on dn_AMERIND_FY_P.trade_area_id = t.trade_area_id and dn_AMERIND_FY_P.data_item_id = 179
left join demographic_numvalues dn_ASIAN10 on dn_ASIAN10.trade_area_id = t.trade_area_id and dn_ASIAN10.data_item_id = 180
left join demographic_numvalues dn_ASIAN10_P on dn_ASIAN10_P.trade_area_id = t.trade_area_id and dn_ASIAN10_P.data_item_id = 181
left join demographic_numvalues dn_ASIAN_CY on dn_ASIAN_CY.trade_area_id = t.trade_area_id and dn_ASIAN_CY.data_item_id = 182
left join demographic_numvalues dn_ASIAN_CY_P on dn_ASIAN_CY_P.trade_area_id = t.trade_area_id and dn_ASIAN_CY_P.data_item_id = 183
left join demographic_numvalues dn_ASIAN_FY on dn_ASIAN_FY.trade_area_id = t.trade_area_id and dn_ASIAN_FY.data_item_id = 184
left join demographic_numvalues dn_ASIAN_FY_P on dn_ASIAN_FY_P.trade_area_id = t.trade_area_id and dn_ASIAN_FY_P.data_item_id = 185
left join demographic_numvalues dn_PACIFIC10 on dn_PACIFIC10.trade_area_id = t.trade_area_id and dn_PACIFIC10.data_item_id = 186
left join demographic_numvalues dn_PACIFIC10_P on dn_PACIFIC10_P.trade_area_id = t.trade_area_id and dn_PACIFIC10_P.data_item_id = 187
left join demographic_numvalues dn_PACIFIC_CY on dn_PACIFIC_CY.trade_area_id = t.trade_area_id and dn_PACIFIC_CY.data_item_id = 188
left join demographic_numvalues dn_PACIFIC_CY_P on dn_PACIFIC_CY_P.trade_area_id = t.trade_area_id and dn_PACIFIC_CY_P.data_item_id = 189
left join demographic_numvalues dn_PACIFIC_FY on dn_PACIFIC_FY.trade_area_id = t.trade_area_id and dn_PACIFIC_FY.data_item_id = 190
left join demographic_numvalues dn_PACIFIC_FY_P on dn_PACIFIC_FY_P.trade_area_id = t.trade_area_id and dn_PACIFIC_FY_P.data_item_id = 191
left join demographic_numvalues dn_OTHRACE10 on dn_OTHRACE10.trade_area_id = t.trade_area_id and dn_OTHRACE10.data_item_id = 192
left join demographic_numvalues dn_OTHRACE10_P on dn_OTHRACE10_P.trade_area_id = t.trade_area_id and dn_OTHRACE10_P.data_item_id = 193
left join demographic_numvalues dn_OTHRACE_CY on dn_OTHRACE_CY.trade_area_id = t.trade_area_id and dn_OTHRACE_CY.data_item_id = 194
left join demographic_numvalues dn_OTHRACE_CY_P on dn_OTHRACE_CY_P.trade_area_id = t.trade_area_id and dn_OTHRACE_CY_P.data_item_id = 195
left join demographic_numvalues dn_OTHRACE_FY on dn_OTHRACE_FY.trade_area_id = t.trade_area_id and dn_OTHRACE_FY.data_item_id = 196
left join demographic_numvalues dn_OTHRACE_FY_P on dn_OTHRACE_FY_P.trade_area_id = t.trade_area_id and dn_OTHRACE_FY_P.data_item_id = 197
left join demographic_numvalues dn_RACE2UP10 on dn_RACE2UP10.trade_area_id = t.trade_area_id and dn_RACE2UP10.data_item_id = 198
left join demographic_numvalues dn_RACE2UP10_P on dn_RACE2UP10_P.trade_area_id = t.trade_area_id and dn_RACE2UP10_P.data_item_id = 199
left join demographic_numvalues dn_RACE2UP_CY on dn_RACE2UP_CY.trade_area_id = t.trade_area_id and dn_RACE2UP_CY.data_item_id = 200
left join demographic_numvalues dn_RACE2UP_CY_P on dn_RACE2UP_CY_P.trade_area_id = t.trade_area_id and dn_RACE2UP_CY_P.data_item_id = 201
left join demographic_numvalues dn_RACE2UP_FY on dn_RACE2UP_FY.trade_area_id = t.trade_area_id and dn_RACE2UP_FY.data_item_id = 202
left join demographic_numvalues dn_RACE2UP_FY_P on dn_RACE2UP_FY_P.trade_area_id = t.trade_area_id and dn_RACE2UP_FY_P.data_item_id = 203
left join demographic_numvalues dn_HISPPOP10 on dn_HISPPOP10.trade_area_id = t.trade_area_id and dn_HISPPOP10.data_item_id = 204
left join demographic_numvalues dn_HISPPOP10_P on dn_HISPPOP10_P.trade_area_id = t.trade_area_id and dn_HISPPOP10_P.data_item_id = 205
left join demographic_numvalues dn_HISPPOPCY on dn_HISPPOPCY.trade_area_id = t.trade_area_id and dn_HISPPOPCY.data_item_id = 206
left join demographic_numvalues dn_HISPPOP_CY_P on dn_HISPPOP_CY_P.trade_area_id = t.trade_area_id and dn_HISPPOP_CY_P.data_item_id = 207
left join demographic_numvalues dn_HISPPOPFY on dn_HISPPOPFY.trade_area_id = t.trade_area_id and dn_HISPPOPFY.data_item_id = 208
left join demographic_numvalues dn_HISPPOPFY_P on dn_HISPPOPFY_P.trade_area_id = t.trade_area_id and dn_HISPPOPFY_P.data_item_id = 209
left join demographic_numvalues dn_POPRATE on dn_POPRATE.trade_area_id = t.trade_area_id and dn_POPRATE.data_item_id = 210
left join demographic_numvalues dn_HHRATE on dn_HHRATE.trade_area_id = t.trade_area_id and dn_HHRATE.data_item_id = 211
left join demographic_numvalues dn_FAMRATE on dn_FAMRATE.trade_area_id = t.trade_area_id and dn_FAMRATE.data_item_id = 212
left join demographic_numvalues dn_OWNRATE on dn_OWNRATE.trade_area_id = t.trade_area_id and dn_OWNRATE.data_item_id = 213
left join demographic_numvalues dn_INCRATE on dn_INCRATE.trade_area_id = t.trade_area_id and dn_INCRATE.data_item_id = 214
left join demographic_numvalues dn_MALE0C10 on dn_MALE0C10.trade_area_id = t.trade_area_id and dn_MALE0C10.data_item_id = 215
left join demographic_numvalues dn_MALE5C10 on dn_MALE5C10.trade_area_id = t.trade_area_id and dn_MALE5C10.data_item_id = 216
left join demographic_numvalues dn_MALE10C10 on dn_MALE10C10.trade_area_id = t.trade_area_id and dn_MALE10C10.data_item_id = 217
left join demographic_numvalues dn_MALE15C10 on dn_MALE15C10.trade_area_id = t.trade_area_id and dn_MALE15C10.data_item_id = 218
left join demographic_numvalues dn_MALE20C10 on dn_MALE20C10.trade_area_id = t.trade_area_id and dn_MALE20C10.data_item_id = 219
left join demographic_numvalues dn_MALE25C10 on dn_MALE25C10.trade_area_id = t.trade_area_id and dn_MALE25C10.data_item_id = 220
left join demographic_numvalues dn_MALE30C10 on dn_MALE30C10.trade_area_id = t.trade_area_id and dn_MALE30C10.data_item_id = 221
left join demographic_numvalues dn_MALE35C10 on dn_MALE35C10.trade_area_id = t.trade_area_id and dn_MALE35C10.data_item_id = 222
left join demographic_numvalues dn_MALE40C10 on dn_MALE40C10.trade_area_id = t.trade_area_id and dn_MALE40C10.data_item_id = 223
left join demographic_numvalues dn_MALE45C10 on dn_MALE45C10.trade_area_id = t.trade_area_id and dn_MALE45C10.data_item_id = 224
left join demographic_numvalues dn_MALE50C10 on dn_MALE50C10.trade_area_id = t.trade_area_id and dn_MALE50C10.data_item_id = 225
left join demographic_numvalues dn_MALE55C10 on dn_MALE55C10.trade_area_id = t.trade_area_id and dn_MALE55C10.data_item_id = 226
left join demographic_numvalues dn_MALE60C10 on dn_MALE60C10.trade_area_id = t.trade_area_id and dn_MALE60C10.data_item_id = 227
left join demographic_numvalues dn_MALE65C10 on dn_MALE65C10.trade_area_id = t.trade_area_id and dn_MALE65C10.data_item_id = 228
left join demographic_numvalues dn_MALE70C10 on dn_MALE70C10.trade_area_id = t.trade_area_id and dn_MALE70C10.data_item_id = 229
left join demographic_numvalues dn_MALE75C10 on dn_MALE75C10.trade_area_id = t.trade_area_id and dn_MALE75C10.data_item_id = 230
left join demographic_numvalues dn_MALE80C10 on dn_MALE80C10.trade_area_id = t.trade_area_id and dn_MALE80C10.data_item_id = 231
left join demographic_numvalues dn_MALE85C10 on dn_MALE85C10.trade_area_id = t.trade_area_id and dn_MALE85C10.data_item_id = 232
left join demographic_numvalues dn_MAL18UP10 on dn_MAL18UP10.trade_area_id = t.trade_area_id and dn_MAL18UP10.data_item_id = 233
left join demographic_numvalues dn_MAL21UP10 on dn_MAL21UP10.trade_area_id = t.trade_area_id and dn_MAL21UP10.data_item_id = 234
left join demographic_numvalues dn_MEDMAGE10 on dn_MEDMAGE10.trade_area_id = t.trade_area_id and dn_MEDMAGE10.data_item_id = 235
left join demographic_numvalues dn_FEM0C10 on dn_FEM0C10.trade_area_id = t.trade_area_id and dn_FEM0C10.data_item_id = 236
left join demographic_numvalues dn_FEM5C10 on dn_FEM5C10.trade_area_id = t.trade_area_id and dn_FEM5C10.data_item_id = 237
left join demographic_numvalues dn_FEM10C10 on dn_FEM10C10.trade_area_id = t.trade_area_id and dn_FEM10C10.data_item_id = 238
left join demographic_numvalues dn_FEM15C10 on dn_FEM15C10.trade_area_id = t.trade_area_id and dn_FEM15C10.data_item_id = 239
left join demographic_numvalues dn_FEM20C10 on dn_FEM20C10.trade_area_id = t.trade_area_id and dn_FEM20C10.data_item_id = 240
left join demographic_numvalues dn_FEM25C10 on dn_FEM25C10.trade_area_id = t.trade_area_id and dn_FEM25C10.data_item_id = 241
left join demographic_numvalues dn_FEM30C10 on dn_FEM30C10.trade_area_id = t.trade_area_id and dn_FEM30C10.data_item_id = 242
left join demographic_numvalues dn_FEM35C10 on dn_FEM35C10.trade_area_id = t.trade_area_id and dn_FEM35C10.data_item_id = 243
left join demographic_numvalues dn_FEM40C10 on dn_FEM40C10.trade_area_id = t.trade_area_id and dn_FEM40C10.data_item_id = 244
left join demographic_numvalues dn_FEM45C10 on dn_FEM45C10.trade_area_id = t.trade_area_id and dn_FEM45C10.data_item_id = 245
left join demographic_numvalues dn_FEM50C10 on dn_FEM50C10.trade_area_id = t.trade_area_id and dn_FEM50C10.data_item_id = 246
left join demographic_numvalues dn_FEM55C10 on dn_FEM55C10.trade_area_id = t.trade_area_id and dn_FEM55C10.data_item_id = 247
left join demographic_numvalues dn_FEM60C10 on dn_FEM60C10.trade_area_id = t.trade_area_id and dn_FEM60C10.data_item_id = 248
left join demographic_numvalues dn_FEM65C10 on dn_FEM65C10.trade_area_id = t.trade_area_id and dn_FEM65C10.data_item_id = 249
left join demographic_numvalues dn_FEM70C10 on dn_FEM70C10.trade_area_id = t.trade_area_id and dn_FEM70C10.data_item_id = 250
left join demographic_numvalues dn_FEM75C10 on dn_FEM75C10.trade_area_id = t.trade_area_id and dn_FEM75C10.data_item_id = 251
left join demographic_numvalues dn_FEM80C10 on dn_FEM80C10.trade_area_id = t.trade_area_id and dn_FEM80C10.data_item_id = 252
left join demographic_numvalues dn_FEM85C10 on dn_FEM85C10.trade_area_id = t.trade_area_id and dn_FEM85C10.data_item_id = 253
left join demographic_numvalues dn_FEM18UP10 on dn_FEM18UP10.trade_area_id = t.trade_area_id and dn_FEM18UP10.data_item_id = 254
left join demographic_numvalues dn_FEM21UP10 on dn_FEM21UP10.trade_area_id = t.trade_area_id and dn_FEM21UP10.data_item_id = 255
left join demographic_numvalues dn_MEDFAGE10 on dn_MEDFAGE10.trade_area_id = t.trade_area_id and dn_MEDFAGE10.data_item_id = 256