use retaildb_timeseries_dev

select * from dbo.addresses where right(street,1) = ' ' --858 rows in june2011
select * from dbo.addresses where right(municipality,1) = ' ' --106 rows in june2011
select * from dbo.addresses where right(governing_district,1) = ' ' --2 rows in june2011

begin transaction

update .dbo.addresses
set street = RTRIM(street)
where  right(street,1) = ' ' --858

update dbo.addresses
set municipality = RTRIM(municipality)
where  right(municipality,1) = ' ' --106

update dbo.addresses
set governing_district = RTRIM(governing_district)
where  right(governing_district,1) = ' ' --2
	
select * from dbo.addresses where right(street,1) = ' ' --should be 0 rows
select * from dbo.addresses where right(municipality,1) = ' ' --should be 0 rows
select * from dbo.addresses where right(governing_district,1) = ' ' --should be 0 rows

commit



select * from dbo.addresses where left(street,1) = ' ' --15 rows in june2011
select * from dbo.addresses where left(municipality,1) = ' ' --0 rows in june2011
select * from dbo.addresses where left(governing_district,1) = ' ' --0 rows in june2011

begin transaction

update .dbo.addresses
set street = LTRIM(street)
where  left(street,1) = ' ' --858

update dbo.addresses
set municipality = LTRIM(municipality)
where  left(municipality,1) = ' ' --106

update dbo.addresses
set governing_district = LTRIM(governing_district)
where  left(governing_district,1) = ' ' --2
	
select * from dbo.addresses where left(street,1) = ' ' --should be 0 rows
select * from dbo.addresses where left(municipality,1) = ' ' --should be 0 rows
select * from dbo.addresses where left(governing_district,1) = ' ' --should be 0 rows

commit