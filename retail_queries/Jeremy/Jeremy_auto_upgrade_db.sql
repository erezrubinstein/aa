-- configure db to allow renaming db files
EXEC sp_configure 'show advanced options', 1
GO
RECONFIGURE
GO
EXEC sp_configure 'xp_cmdshell', 1
GO
RECONFIGURE
GO


-- declare vars
declare @db_name varchar(100) = 'retaildb_timeseries_verification'
declare @num_dbs int = 2
declare @new_mdf_name varchar(100) = 'C:\SQLData\' + @db_name + '.mdf'
declare @new_ldf_name varchar(100) = 'C:\SQLData\' + @db_name + '.ldf'
declare @back_up_name varchar(100) = 'C:\SQLData\' + @db_name + '.bak'
declare @current_db_name varchar(100)
declare @new_db_name varchar(100)



-- roll dbs and drop last any dbs with up to 5 numbers above the num_dbs
declare @db_to_drop_index int = -1
WHILE @db_to_drop_index < 5
BEGIN
	declare @db_to_drop varchar(100) = @db_name + '_' + cast(@num_dbs + @db_to_drop_index as varchar(2))
	select 'dropping db: ' + @db_to_drop
	if DB_ID(@db_to_drop) is not null
	begin
		declare @drop_db_sql nvarchar(400) = 'drop database ' + @db_to_drop
		execute sp_executesql @drop_db_sql
	end 

	-- increment counter
	set @db_to_drop_index = @db_to_drop_index + 1
END

-- roll over old dbs
declare @current_index int = @num_dbs - 1
while @current_index > 0
BEGIN
	-- figure out new db names
	if @current_index = 1
	BEGIN
		set @current_db_name = @db_name
		set @new_db_name = @db_name + '_1'
	END
	ELSE
	BEGIN 
		set @current_db_name = @db_name + '_' + CAST(@current_index - 1 as varchar(2))
		set @new_db_name = @db_name + '_' + CAST(@current_index as varchar(2))
	END
	
	if DB_ID(@current_db_name) is not null
	begin
		declare @rename_db_sql nvarchar(max) = '
		alter database ' + @current_db_name + ' set single_user with rollback immediate;
		alter database ' + @current_db_name + ' set multi_user;
		exec sp_renamedb ''' + @current_db_name + ''',''' + @new_db_name + ''';
		alter database ' + @new_db_name + ' set offline;
		alter database ' + @new_db_name + '
		modify file (name = N''db_data'',
		filename = N''C:\SQLData\' + @new_db_name + '.mdf'');
		alter database ' + @new_db_name + '
		modify file (name = N''db_log'',
		filename = N''C:\SQLData\' + @new_db_name + '.ldf'');
		exec xp_cmdshell ''rename C:\SQLData\' + @current_db_name + '.mdf ' + @new_db_name + '.mdf'';
		exec xp_cmdshell ''rename C:\SQLData\' + @current_db_name + '.ldf ' + @new_db_name + '.ldf'';
		alter database ' + @new_db_name + ' set online;'
		
		execute sp_executesql @rename_db_sql
		print @rename_db_sql
	end
	
	set @current_index = @current_index - 1
END


-- restore to original db
RESTORE FILELISTONLY
FROM DISK = @back_up_name


RESTORE DATABASE @db_name
FROM DISK = @back_up_name
WITH MOVE 'db_data' TO @new_mdf_name,
MOVE 'db_log' TO @new_ldf_name

