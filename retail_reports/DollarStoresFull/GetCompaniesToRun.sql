use retaildb_timeseries_dollar_stores_full_version_v1
go
select * from companies
where name like '%general%'
	or name like '%tree%'
	or name like '%fred%'
	or name like '%lots%'
	or name like '%99%'
	or name like '%indepen%'
	or name like '%ollie%'
	