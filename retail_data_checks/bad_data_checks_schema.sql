begin transaction

-- rename data_checks column result -> bad_data_rows
if exists(
	select 1 
	from sys.columns 
	where name in ('result') and object_id = object_id('data_checks')
	)
begin
	exec sp_RENAME 'data_checks.result' , 'bad_data_rows', 'COLUMN';
	
	alter table data_checks
	alter column bad_data_rows int NOT NULL
end


-- rename data_checks column data_check_values_id -> data_check_value_id
if exists(
	select 1
	from sys.columns
	where name in ('data_check_values_id') and object_id = object_id('data_check_values')
	)
begin
	exec sp_rename 'data_check_values.data_check_values_id', 'data_check_value_id', 'COLUMN';
end

-- move entity_id from data_checks to data_check_values table
if exists (
	select 1 
	from sys.columns 
	where name in ('entity_id') and object_id = object_id('data_checks')
		)
	and not exists (
	select 1 
	from sys.columns 
	where name in ('entity_id') and object_id = object_id('data_check_values')
		)
begin
	alter table data_check_values
	add entity_id int null;
	
	declare @sql nvarchar(max) = N'
	update data_check_values
	set data_check_values.entity_id = dc.entity_id
	from data_check_values dcv
	inner join data_checks dc
	on dcv.data_check_id = dc.data_check_id;'
	
	exec sp_executesql @sql;
	
	alter table data_check_values
	alter column entity_id int not null;
	
	DROP INDEX [IX_data_checks] ON [dbo].[data_checks] WITH ( ONLINE = OFF )

CREATE NONCLUSTERED INDEX [IX_data_checks] ON [dbo].[data_checks] 
(
	[entity_type_id] ASC
)
	
	alter table data_checks drop column entity_id;
end


commit

