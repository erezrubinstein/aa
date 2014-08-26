/*
   Thursday, November 08, 20123:27:02 PM
   User: jsternberg
   Server: 192.168.10.104
   Database: retaildb_dev
   Application: 
*/


/* To prevent any potential data loss issues, you should review this script in detail before running it outside the context of the database designer.*/
BEGIN TRANSACTION
SET QUOTED_IDENTIFIER ON
SET ARITHABORT ON
SET NUMERIC_ROUNDABORT OFF
SET CONCAT_NULL_YIELDS_NULL ON
SET ANSI_NULLS ON
SET ANSI_PADDING ON
SET ANSI_WARNINGS ON
COMMIT


SET XACT_ABORT ON

BEGIN TRANSACTION
GO

--clean up bad data
delete cp
from competitions cp
where not exists (select 1 from companies c where c.id = cp.home_company_id)
--(252070 row(s) affected)

--select count(*)
--from competitions cp
--where not exists (select 1 from companies c where c.id = cp.home_company_id);

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('competitions') and referenced_object_id=object_id('companies')
		and name like '%home_company_id%'
		)
begin
	ALTER TABLE dbo.competitions ADD CONSTRAINT
		FK_competitions_companies_home_company_id FOREIGN KEY
		(
		home_company_id
		) REFERENCES dbo.companies
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end


--clean up bad data
delete cp
from competitions cp
where not exists (select 1 from companies c where c.id = cp.away_company_id)
--(0 row(s) affected)

--select count(*)
--from competitions cp
--where not exists (select 1 from companies c where c.id = cp.away_company_id)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('competitions') and referenced_object_id=object_id('companies')
		and name like '%away_company_id%'
		)
begin
	ALTER TABLE dbo.competitions ADD CONSTRAINT
		FK_competitions_companies_away_company_id FOREIGN KEY
		(
		away_company_id
		) REFERENCES dbo.companies
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end



delete cs
from companies_sectors cs
where not exists (
	select 1 from companies c where c.id = cs.company_id
)
--(1040 row(s) affected)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('companies_sectors') and referenced_object_id=object_id('companies')
		and name like '%companies_sectors_companies%'
		)
begin
	ALTER TABLE dbo.companies_sectors ADD CONSTRAINT
		FK_companies_sectors_companies FOREIGN KEY
		(
		company_id
		) REFERENCES dbo.companies
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end	

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('companies_sectors') and referenced_object_id=object_id('sectors')
		and name like '%companies_sectors_sectors%'
		)
begin
	ALTER TABLE dbo.companies_sectors ADD CONSTRAINT
		FK_companies_sectors_sectors FOREIGN KEY
		(
		sector_id
		) REFERENCES dbo.sectors
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end





delete s
from stores s
where not exists (
	select 1 from companies c where c.id = s.company_id
)
--(21282 row(s) affected)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('stores') and referenced_object_id=object_id('companies')
		and name like '%stores_companies%'
		)
begin
	ALTER TABLE dbo.stores ADD CONSTRAINT
		FK_stores_companies FOREIGN KEY
		(
		company_id
		) REFERENCES dbo.companies
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end
	
	


delete m
--select *
from monopolies m
where not exists (
	select 1 from stores s where s.id = m.store_id
)
--(2 row(s) affected)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('monopolies') and referenced_object_id=object_id('stores')
		and name like '%monopolies_stores%'
		)
begin
	ALTER TABLE dbo.monopolies ADD CONSTRAINT
		FK_monopolies_stores FOREIGN KEY
		(
		store_id
		) REFERENCES dbo.stores
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end
	




delete t
from trade_areas t
where not exists (
	select 1 from stores s where s.id = t.store_id
)
--(22 row(s) affected)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('trade_areas') and referenced_object_id=object_id('stores')
		and name like '%trade_areas_stores%'
		)
begin
	ALTER TABLE dbo.trade_areas ADD CONSTRAINT
		FK_trade_areas_stores FOREIGN KEY
		(
		store_id
		) REFERENCES dbo.stores
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end





delete v
from demographic_strvalues v
where not exists (
	select 1 from trade_areas t where t.id = v.trade_area_id
)
--(22 row(s) affected)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('demographic_strvalues') and referenced_object_id=object_id('trade_areas')
		and name like '%demographic_strvalues_trade_areas%'
		)
begin
	ALTER TABLE dbo.demographic_strvalues ADD CONSTRAINT
		FK_demographic_strvalues_trade_areas FOREIGN KEY
		(
		trade_area_id
		) REFERENCES dbo.trade_areas
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end




delete v
from demographic_strvalues v
where not exists (
	select 1 from demographic_types t where t.id = v.demographic_type_id
)
	
if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('demographic_strvalues') and referenced_object_id=object_id('demographic_types')
		and name like '%demographic_strvalues_demographic_types%'
		)
begin
	ALTER TABLE dbo.demographic_strvalues ADD CONSTRAINT
		FK_demographic_strvalues_demographic_types FOREIGN KEY
		(
		demographic_type_id
		) REFERENCES dbo.demographic_types
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end




if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('demographic_strvalues') and referenced_object_id=object_id('demographic_segments')
		and name like '%demographic_strvalues_demographic_segments%'
		)
begin
	ALTER TABLE dbo.demographic_strvalues ADD CONSTRAINT
		FK_demographic_strvalues_demographic_segments FOREIGN KEY
		(
		segment_id
		) REFERENCES dbo.demographic_segments
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end






delete v
from demographic_numvalues v
where not exists (
	select 1 from trade_areas t where t.id = v.trade_area_id
)
--(2037 row(s) affected)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('demographic_numvalues') and referenced_object_id=object_id('trade_areas')
		and name like '%demographic_numvalues_trade_areas%'
		)
begin
	ALTER TABLE dbo.demographic_numvalues ADD CONSTRAINT
		FK_demographic_numvalues_trade_areas FOREIGN KEY
		(
		trade_area_id
		) REFERENCES dbo.trade_areas
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end






delete v
from demographic_numvalues v
where not exists (
	select 1 from demographic_types t where t.id = v.demographic_type_id
)
--(0 row(s) affected)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('demographic_numvalues') and referenced_object_id=object_id('demographic_types')
		and name like '%demographic_numvalues_demographic_types%'
		)
begin
	ALTER TABLE dbo.demographic_numvalues ADD CONSTRAINT
		FK_demographic_numvalues_demographic_types FOREIGN KEY
		(
		demographic_type_id
		) REFERENCES dbo.demographic_types
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end
	



if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('demographic_numvalues') and referenced_object_id=object_id('demographic_segments')
		and name like '%demographic_numvalues_demographic_segments%'
		)
begin
	ALTER TABLE dbo.demographic_numvalues ADD CONSTRAINT
		FK_demographic_numvalues_demographic_segments FOREIGN KEY
		(
		segment_id
		) REFERENCES dbo.demographic_segments
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end



delete cs
from competitive_stores cs
where not exists (select 1 from stores s where s.id = cs.home_store_id)


if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('competitive_stores') and referenced_object_id=object_id('stores')
		and name like '%competitive_stores_stores_home_store_id%'
		)
begin
	ALTER TABLE dbo.competitive_stores ADD CONSTRAINT
		FK_competitive_stores_stores_home_store_id FOREIGN KEY
		(
		home_store_id
		) REFERENCES dbo.stores
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end




delete cs
from competitive_stores cs
where not exists (select 1 from stores s where s.id = cs.away_store_id)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('competitive_stores') and referenced_object_id=object_id('stores')
		and name like '%competitive_stores_stores_away_store_id%'
		)
begin
	ALTER TABLE dbo.competitive_stores ADD CONSTRAINT
		FK_competitive_stores_stores_away_store_id FOREIGN KEY
		(
		away_store_id
		) REFERENCES dbo.stores
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end
	




delete a
from addresses a
where not exists (select 1 from stores s where s.id = a.store_id)
--(21283 row(s) affected)

if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('addresses') and referenced_object_id=object_id('stores')
		and name like '%addresses_stores%'
		)
begin
	ALTER TABLE dbo.addresses ADD CONSTRAINT
		FK_addresses_stores FOREIGN KEY
		(
		store_id
		) REFERENCES dbo.stores
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end





if not exists (
	select * from sys.foreign_keys 
	where parent_object_id=object_id('addresses') and referenced_object_id=object_id('countries')
		and name like '%addresses_countries%'
		)
begin
	ALTER TABLE dbo.addresses ADD CONSTRAINT
		FK_addresses_countries FOREIGN KEY
		(
		country_id
		) REFERENCES dbo.countries
		(
		id
		) ON UPDATE  NO ACTION 
		 ON DELETE  NO ACTION 
end





commit