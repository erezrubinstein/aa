use retaildb_timeseries_staging_myeyedr
go


insert into [demographics_denorm_10_mile] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
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
	M17068a_B,
	M17074a_B,
	M17082a_B,
	M17083a_B,
	M17084a_B,
	M17113a_B,
	X8033_X,
	X8021_X,
	agg_income)
	--traffic, auto_parts_DIY_proxy, auto_parts_DIFM_proxy, auto_fleet, commutation_driving_pct, commutation_commute_time, traffic_summed, traffic_weighted_distance)
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
	dn_M17068a_B.value as M17068a_B,
	dn_M17074a_B.value as M17074a_B,
	dn_M17082a_B.value as M17082a_B,
	dn_M17083a_B.value as M17083a_B,
	dn_M17084a_B.value as M17084a_B,
	dn_M17113a_B.value as M17113a_B,
	dn_X8033_X.value as X8033_X,
	dn_X8021_X.value as X8021_X,
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
left join demographic_numvalues dn_M17068a_B on dn_M17068a_B.trade_area_id = t.trade_area_id and dn_M17068a_B.data_item_id = 2061
left join demographic_numvalues dn_M17074a_B on dn_M17074a_B.trade_area_id = t.trade_area_id and dn_M17074a_B.data_item_id = 2082
left join demographic_numvalues dn_M17082a_B on dn_M17082a_B.trade_area_id = t.trade_area_id and dn_M17082a_B.data_item_id = 2103
left join demographic_numvalues dn_M17083a_B on dn_M17083a_B.trade_area_id = t.trade_area_id and dn_M17083a_B.data_item_id = 2106
left join demographic_numvalues dn_M17084a_B on dn_M17084a_B.trade_area_id = t.trade_area_id and dn_M17084a_B.data_item_id = 2109
left join demographic_numvalues dn_M17113a_B on dn_M17113a_B.trade_area_id = t.trade_area_id and dn_M17113a_B.data_item_id = 2187
left join demographic_numvalues dn_X8033_X on dn_X8033_X.trade_area_id = t.trade_area_id and dn_X8033_X.data_item_id = 2598
left join demographic_numvalues dn_X8021_X on dn_X8021_X.trade_area_id = t.trade_area_id and dn_X8021_X.data_item_id = 2757