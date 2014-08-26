use LL_OCT3_CMA_100213
go

 with dupes as ( select s.company_id, s.address_id, s.phone_number, s.store_format, count(*) cnt from stores s group by s.company_id, s.address_id, s.phone_number, s.store_format having count(*) > 1 ) 

select 
	c.name as company,
	s.store_id,
	s.address_id,
	isnull(s.phone_number, '') as phone_number,
	a.street_number, 
	a.street,
	ISNULL(a.suite, '') as suite,
	a.municipality as city,
	a.governing_district as state,
	a.postal_area as zip,
	a.latitude,
	a.longitude,
	ISNULL(s.note, '') as note,
	ISNULL(s.store_format, '') as store_format,
	ISNULL(a.shopping_center_name, '') as mall,
	isnull(s.company_generated_store_number, '') as company_generated_store_number,
	s.assumed_opened_date as opened,
	s.assumed_closed_date as closed
from stores s
inner join addresses a on a.address_id = s.address_id
inner join companies c on c.company_id = s.company_id
where s.store_id in 
(
	 select s1.store_id as id from stores as s1 inner join stores as s2 on s1.address_id = s2.address_id  and s1.company_id = s2.company_id where (s1.phone_number is not null and s2.phone_number is null)  or (s2.phone_number is not null and s1.phone_number is null)
)
--where a.address_id in 
--(
--	 select s1.store_id as id from stores as s1 inner join stores as s2 on s1.address_id = s2.address_id  and s1.company_id = s2.company_id where (s1.phone_number is not null and s2.phone_number is null)  or (s2.phone_number is not null and s1.phone_number is null)
--)
order by a.postal_area, a.governing_district, a.municipality, a.street
--inner join trade_areas t on t.store_id = s.store_id
--where t.trade_area_id in 
--(
--	36567, 16153
--)




