use retaildb_timeseries_dollar_stores_full_version_v1
go

-- get roses stores
declare @roses_stores table(store_id int primary key, address_id int)
insert into @roses_stores
select store_id, address_id from stores where store_format = 'Roses'

-- get stores within .03 lat/long away and belong to the top 8 companies
declare @stores_in_vicinity table(store_id int primary key)
insert into @stores_in_vicinity
select distinct s.store_id
from @roses_stores s_roses
inner join addresses a_roses on a_roses.address_id = s_roses.address_id
inner join addresses a on 
	(a.longitude between (a_roses.longitude - .3) and (a_roses.longitude + .3))
	and (a.latitude between (a_roses.latitude - .3) and (a_roses.latitude + .3))
inner join stores s on s.address_id = a.address_id
where s.company_id in (64, 65, 69, 70, 71, 77, 80, 81)

/*
update stores
set assumed_opened_date = '19000101'
where store_id in (select store_id from @roses_stores)

delete
from competitive_stores
where away_store_id in (select store_id from @roses_stores)

delete
from competitive_stores
where home_store_id in (select store_id from @stores_in_vicinity)
	
delete
from monopolies
where store_id in (select store_id from @stores_in_vicinity)

select CAST(s.company_id as varchar(100)) + ',' + CAST(s.store_id as varchar(100))
from @stores_in_vicinity siv
inner join stores s on s.store_id = siv.store_id
*/