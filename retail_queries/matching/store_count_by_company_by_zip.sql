

--how many stores per zip code per company?
--and get the lat/long range between max/mins
select *, max_lat - min_lat as diff_lat, max_long - min_long as diff_long
from (
select s.company_id
	, a.postal_area
	, count(distinct s.id) cnt_distinct_stores
	, min(a.latitude) as min_lat 
	, min(a.longitude) as min_long
	, max(a.latitude) as max_lat
	, max(a.longitude) as max_long
from retaildb_test_june2011.dbo.addresses_vw a
inner join retaildb_test_june2011.dbo.stores s on s.id = a.store_id
group by s.company_id, a.postal_area
having count(distinct s.id) > 1
) x
order by diff_lat desc
;


select * from retaildb_test_june2011.dbo.addresses_vw a
inner join retaildb_test_june2011.dbo.stores s on s.id = a.store_id
where a.postal_area = '01752'
order by postal_area;

