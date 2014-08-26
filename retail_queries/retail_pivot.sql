select company_id, fulladdress, [TOTPOP_CY], [TOTHH_CY], [MEDHINC_CY], [AVGHINC_CY]
from (	
	select company_id, fulladdress, name, value 
	from retail_demographic_values_vw
	where company_id in (14117, 14116, 14122, 14123)
) as t
pivot (
	max(value)
	for name in ([TOTPOP_CY], [TOTHH_CY], [MEDHINC_CY], [AVGHINC_CY])
) as pvt
order by company_id, fulladdress desc