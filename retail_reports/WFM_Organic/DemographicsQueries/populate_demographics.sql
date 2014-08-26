use retaildb_timeseries_wfm_organic
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
	M17025a_B,
	X1002_X,
	M16295a_B,
	agg_income,
	agg_75K_HH)
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
	dn_M17025a_B.value as M17025a_B,
	dn_X1002_X.value as X1002_X,
	dn_M16295a_B.value as M16295a_B,
	(dn_TOTPOP_CY.value * dn_PCI_CY.value) as agg_income,
	dn_HINC75_CY.value + dn_HINC100_CY.value + dn_HINC150_CY.value + dn_HINC200_CY.value as agg_75K_HH
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
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
left join demographic_numvalues dn_MEDHINC_CY on dn_MEDHINC_CY.trade_area_id = t.trade_area_id and dn_MEDHINC_CY.data_item_id = 84
left join demographic_numvalues dn_AVGHINC_CY on dn_AVGHINC_CY.trade_area_id = t.trade_area_id and dn_AVGHINC_CY.data_item_id = 86
left join demographic_numvalues dn_PCI_CY on dn_PCI_CY.trade_area_id = t.trade_area_id and dn_PCI_CY.data_item_id = 88
left join demographic_numvalues dn_M17025a_B on dn_M17025a_B.trade_area_id = t.trade_area_id and dn_M17025a_B.data_item_id = 1950
left join demographic_numvalues dn_X1002_X on dn_X1002_X.trade_area_id = t.trade_area_id and dn_X1002_X.data_item_id = 2559
left join demographic_numvalues dn_M16295a_B on dn_M16295a_B.trade_area_id = t.trade_area_id and dn_M16295a_B.data_item_id = 2716