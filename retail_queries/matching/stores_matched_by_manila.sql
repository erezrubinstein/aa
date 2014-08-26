select count(*) from stores_matched_by_manila --29836

select count(distinct june_id) --29836
from stores_matched_by_manila m1
where exists (select 1 from retaildb_test_june2011.dbo.stores s0 where s0.id = m1.june_id);

select COUNT(*) from retaildb_test_june2011.dbo.stores --30337

select 30337 - 29836; 

--387 of 501 that are definitely closed 'blank'
--85 of 501 are marked as N
--22 missed from 2012 harvest -- confirmed on the website, the store exists today
--7 Y (matched)

select 387 + 85 + 22 --= 494

select *
from stores_matched_by_manila m1
where not exists (select 1 from retaildb_test_june2011.dbo.stores s0 where s0.id = m1.june_id)


select *
from retaildb_test_june2011.dbo.stores s0
where not exists (select 1 from stores_matched_by_manila m1 where s0.id = m1.june_id)


select * from retaildb_test_june2011.dbo.companies