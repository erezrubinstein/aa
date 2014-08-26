create view dbo.addresses_vw as
select *, convert(varchar(100), street_number) + ' ' + street + ', ' + municipality + ', ' + governing_district as fulladdress
from addresses;
go