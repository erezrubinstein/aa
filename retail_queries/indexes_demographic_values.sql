
USE [retaildb_test_june2011]
GO
CREATE NONCLUSTERED INDEX IX_demographic_numvalues_trade_area_id_demographic_type_id
ON [dbo].[demographic_numvalues] ([trade_area_id],[demographic_type_id])
GO



USE [retaildb_test_june2011]
GO
CREATE NONCLUSTERED INDEX IX_demographic_strvalues_trade_area_id_demographic_type_id
ON [dbo].[demographic_strvalues] ([trade_area_id],[demographic_type_id])
GO
