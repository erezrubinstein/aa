select june2011_store_id, count(*)
from matching.dbo.stores_matched
group by june2011_store_id
having count(*) > 1

select * from matching.dbo.stores_matched_analysis_vw
where june2011_store_id in (
106772,
109122,
109872,
113051,
128422
)
order by june2011_store_id

--correct: 36843, bad: 36247
--good: 36932, bad: 34132
--good; 36963, bad: 30691
--good: 41298, bad: 37862
--good: 53988, bad: 53843


create table stores_oct2012_dupes (
	good_store_id int not null,
	bad_store_id int not null
	)

insert into stores_oct2012_dupes (good_store_id, bad_store_id)
select 36843 as good, 36247 as bad union all
select 36932 as good, 34132 as bad union all
select 36963 as good, 30691 as bad union all
select 41298 as good, 37862 as bad union all
select 53988 as good, 53843 as bad
	
create unique clustered index IX_bad_store_id on stores_oct2012_dupes (bad_store_id)