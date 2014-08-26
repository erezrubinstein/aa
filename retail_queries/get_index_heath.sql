dbcc showcontig with tableresults, all_indexes


--the new way
with idx_stats as (
	select * from sys.dm_db_index_physical_stats(db_id(), null, null, null, 'detailed')
	)
select o.name as table_name, i.name as index_name, x.* 
from idx_stats x
inner join sys.indexes i on i.object_id = x.object_id and i.index_id = x.index_id
inner join sys.objects o on o.object_id = x.object_id
where x.avg_fragmentation_in_percent > 5
order by x.avg_fragmentation_in_percent desc
;