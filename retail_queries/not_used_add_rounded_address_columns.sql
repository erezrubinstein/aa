set xact_abort on
begin transaction

alter table addresses
add latitude_r4 decimal(9,4) null
, longitude_r4 decimal(9,4) null
, latitude_r3 decimal(9,3) null
, longitude_r3 decimal(9,3) null
, latitude_r2 decimal(9,2) null
, longitude_r2 decimal(9,2) null
, latitude_r1 decimal(9,1) null
, longitude_r1 decimal(9,1) null
;
go

update addresses
set latitude_r4 = round(latitude,4)
, longitude_r4 = round(longitude,4)
, latitude_r3 = round(latitude,3)
, longitude_r3 = round(longitude,3)
, latitude_r2 = round(latitude,2)
, longitude_r2 = round(longitude,2)
, latitude_r1 = round(latitude,1)
, longitude_r1 = round(longitude,1)
;

create nonclustered index IX_lat4 on addresses ([latitude_r4], [longitude_r4])
INCLUDE ( [address_id],[street_number],[street],[municipality],[governing_district],[postal_area],[suite],[max_source_date],[latitude],[longitude]);

create nonclustered index IX_lat3 on addresses ([latitude_r3], [longitude_r3])
INCLUDE ( [address_id],[street_number],[street],[municipality],[governing_district],[postal_area],[suite],[max_source_date],[latitude],[longitude]);

create nonclustered index IX_lat2 on addresses ([latitude_r2], [longitude_r2])
INCLUDE ( [address_id],[street_number],[street],[municipality],[governing_district],[postal_area],[suite],[max_source_date],[latitude],[longitude]);

create nonclustered index IX_lat1 on addresses ([latitude_r1], [longitude_r1])
INCLUDE ( [address_id],[street_number],[street],[municipality],[governing_district],[postal_area],[suite],[max_source_date],[latitude],[longitude]);


--this query uses the lat4 index
select top 100 * from addresses WHERE latitude_r4 = 38.7714 and longitude_r4 = -93.7345;

rollback
