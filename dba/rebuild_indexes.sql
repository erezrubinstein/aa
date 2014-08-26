use retaildb_timeseries_lululemon_v18
go

DECLARE @table_name VARCHAR(255)
DECLARE @sql NVARCHAR(500)
DECLARE @fillfactor INT = 80
DECLARE @tables TABLE (row_num INT IDENTITY(1,1) not null, name varchar(100) not null)
DECLARE @loop_index INT = 0
DECLARE @tables_count INT = 0

-- get all tables and count
INSERT INTO @tables (name)
SELECT OBJECT_SCHEMA_NAME([object_id])+'.'+name
FROM sys.tables order by OBJECT_SCHEMA_NAME([object_id])+'.'+name
SELECT @tables_count = COUNT(*) FROM @tables

-- for each table
WHILE @loop_index <= @tables_count
BEGIN
	-- reindex table
	SELECT @table_name = name FROM @tables WHERE row_num = @loop_index
	SET @sql = 'ALTER INDEX ALL ON ' + @table_name + ' REBUILD WITH (FILLFACTOR = ' + CONVERT(VARCHAR(3),@fillfactor) + ')'
	print @sql
	EXEC (@sql)
	
	-- increment index
	SET  @loop_index = @loop_index + 1
END