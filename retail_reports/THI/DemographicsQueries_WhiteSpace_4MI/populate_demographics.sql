USE THI_OCT13_4MSQWHSP_101013
go

declare @threshold_id int = 1

insert into [demographics_denorm] (company_name, store_id, assumed_opened_date, assumed_closed_date, trade_area_id, 
	TOTPOP_CY,
	AGG_INCOME,
	PROX_QSR_B_L_S)

	select
		c.name as company_name,
		s.store_id,
		s.assumed_opened_date,
		s.assumed_closed_date,
		t.trade_area_id,
		dn_TOTPOP_CY.value as TOTPOP_CY,
		dn_AGG_INCOME.value as AGG_INCOME,
		dn_PROX_QSR_B_L_S.value as PROX_QSR_B_L_S
from stores s
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = @threshold_id
inner join companies c on c.company_id = s.company_id
left join demographic_numvalues dn_TOTPOP_CY on dn_TOTPOP_CY.trade_area_id = t.trade_area_id and dn_TOTPOP_CY.data_item_id = 13 and dn_TOTPOP_CY.template_name = 'QSR_OCT13'
left join demographic_numvalues dn_AGG_INCOME on dn_AGG_INCOME.trade_area_id = t.trade_area_id and dn_AGG_INCOME.data_item_id = 2810 and dn_AGG_INCOME.template_name = 'QSR_OCT13'
left join demographic_numvalues dn_PROX_QSR_B_L_S on dn_PROX_QSR_B_L_S.trade_area_id = t.trade_area_id and dn_PROX_QSR_B_L_S.data_item_id = 2866 and dn_PROX_QSR_B_L_S.template_name = 'QSR_OCT13'