--clear connections
  alter database retaildb_timeseries_staging_a set single_user with rollback immediate;
  alter database retaildb_timeseries_staging_a set multi_user;
  exec sp_renamedb 'retaildb_timeseries_staging_a','LL_OCT3_CMA_100213';
  alter database LL_OCT3_CMA_100213 set offline;
  alter database LL_OCT3_CMA_100213
  modify file (name = N'db_data',
    filename = N'D:\SQLData\LL_OCT3_CMA_100213.mdf');
  alter database LL_OCT3_CMA_100213
  modify file (name = N'db_log',
    filename = N'D:\SQLData\LL_OCT3_CMA_100213.ldf');
  exec xp_cmdshell 'rename D:\SQLData\retaildb_timeseries_staging_a.mdf LL_OCT3_CMA_100213.mdf';
  exec xp_cmdshell 'rename D:\SQLData\retaildb_timeseries_staging_a.ldf LL_OCT3_CMA_100213.ldf';
  alter database LL_OCT3_CMA_100213 set online;