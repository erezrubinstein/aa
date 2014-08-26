--group by match type
select match_type, count(*)
from matching.dbo.stores_matched_analysis_vw with (nolock)
group by match_type
with rollup;

--pure store count
select count(*) from retaildb_test_june2011.dbo.stores --30337

--core matching table
select * from matching.dbo.stores_matched_analysis_vw

--clean june loader files
select * from matching.dbo.june2011_clean_vw with (nolock) --30337


