use application_logging_staging
go


ALTER DATABASE application_logging_staging SET RECOVERY SIMPLE WITH NO_WAIT
DBCC SHRINKFILE(db_log, 1)
ALTER DATABASE application_logging_staging SET RECOVERY FULL WITH NO_WAIT