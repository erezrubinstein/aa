
alter view june2011_clean_vw as

--june 2011 query
select name
	, 'D' as record_type
	, 'C' as action_type
	, 'OCT2012-' + convert(varchar(100), oct2012_store_id) as store_id
	, case when oct2012_street_number is null then '' else convert(varchar(100), oct2012_street_number) + ' ' end 
		+ oct2012_street as street
	, oct2012_city as city
	, oct2012_state as state
	, oct2012_zip as zip
	, oct2012_phone_number as phone
	, '' as country
	, oct2012_shopping_center as shopping_center
	, coalesce(oct2012_opened_on,'') as opened_on
	, '' as suite
	, '' as store_format
	, '' as company_generated_store_number
	, oct2012_note as note
	, oct2012_longitude as x
	, oct2012_latitude as y
	--8 blank columns
from matching.dbo.stores_matched_analysis_vw with (nolock)
where match_type <> 'closed'

union all

select name
	, 'D' as record_type
	, 'C' as action_type
	, 'JUN2011-' + convert(varchar(100), june2011_store_id) as store_id
	, case when june2011_street_number is null then '' else convert(varchar(100), june2011_street_number) + ' ' end 
		+ june2011_street as street
	, june2011_city as city
	, june2011_state as state
	, june2011_zip as zip
	, june2011_phone_number as phone
	, '' as country
	, june2011_shopping_center as shopping_center
	, coalesce(june2011_opened_on,'') as opened_on
	, '' as suite
	, '' as store_format
	, '' as company_generated_store_number
	, june2011_note as note
	, june2011_longitude as x
	, june2011_latitude as y
	--8 blank columns
from matching.dbo.stores_matched_analysis_vw with (nolock)
where match_type = 'closed'