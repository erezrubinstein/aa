select count(distinct zip_code) --39104
from zip_establishment_details ze
where not exists (select 1 from zip_codes z where z.zip_code = ze.zip_code)

select count(distinct zip_code) from zip_codes --33120


select top 100 *
from zip_establishment_details ze
where zip_code = '01004'
where not exists (select 1 from zip_codes z where z.zip_code = ze.zip_code)

select * from zip_codes where zip_code like '01%'

select 6647 / 39104.0