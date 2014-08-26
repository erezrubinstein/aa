--clear connections
  alter database db1 set single_user with rollback immediate;
  alter database db1 set multi_user;
  exec sp_renamedb 'db1','db2';
  alter database db2 set offline;
  alter database db2
  modify file (name = N'db_data',
    filename = N'D:\SQLData\db2.mdf');
  alter database db2
  modify file (name = N'db_log',
    filename = N'D:\SQLData\db2.ldf');
  exec xp_cmdshell 'rename D:\SQLData\db1.mdf db2.mdf';
  exec xp_cmdshell 'rename D:\SQLData\db1.ldf db2.ldf';
  alter database db2 set online;