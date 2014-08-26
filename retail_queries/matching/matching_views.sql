USE [retaildb_test_june2011]
GO

/****** Object:  View [dbo].[addresses_vw]    Script Date: 11/18/2012 15:29:35 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

alter view [dbo].[addresses_matching_vw] as
select *
	, replace(replace(replace(replace(
		replace(replace(replace(replace(street, 'East ', 'E '), 'West ','W '), 'South ','S '),'North ','N ')
		,'E. ','E '),'W. ','W '),'S. ','S '),'N. ','N ') as street_normalized
from addresses

GO

ALTER view [dbo].[addresses_vw] as
select *
	, convert(varchar(100), street_number) + ' ' + street + ', ' + municipality + ', ' + governing_district + ' ' + postal_area as fulladdress
	, convert(varchar(100), street_number) + ' ' + street_normalized + ', ' + municipality + ', ' + governing_district + ' ' + postal_area as fulladdress_normalized
	, case when street_normalized like '% %' then substring(street_normalized,1, charindex(' ', street_normalized) - 1) else street_normalized end as street_normalized_first_word
from addresses_matching_vw

GO


alter view stores_vw as
select *, replace(replace(replace(replace(phone_number,'(',''),')',''),'-',''),' ','') as stripped_phone_number
from stores
GO


select * from [addresses_vw]

select * from [stores_vw] order by phone_number desc
--where stripped_phone_number <> ''
--	and ISNUMERIC(stripped_phone_number) <> 1

