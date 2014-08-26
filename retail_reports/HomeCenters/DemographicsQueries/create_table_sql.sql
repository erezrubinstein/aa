USE HOMECENT_JUL13_CMA_072213
GO

/****** Object:  Table [dbo].[demographics_denorm]    Script Date: 04/07/2013 12:32:40 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

SET ANSI_PADDING ON
GO

CREATE TABLE [dbo].[demographics_denorm](
	[demographic_denorm_id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[store_id] [int] NOT NULL,
	[company_name] [varchar](200) NOT NULL,
	[assumed_opened_date] [datetime] NOT NULL,
	[assumed_closed_date] [datetime] NULL,
	TOTPOP_CY [decimal](19, 4) NULL,
TOTHH_CY [decimal](19, 4) NULL,
OWNER_CY [decimal](19, 4) NULL,
RENTER_CY [decimal](19, 4) NULL,
MEDAGE_CY [decimal](19, 4) NULL,
HINC0_CY [decimal](19, 4) NULL,
HINC15_CY [decimal](19, 4) NULL,
HINC25_CY [decimal](19, 4) NULL,
HINC35_CY [decimal](19, 4) NULL,
HINC50_CY [decimal](19, 4) NULL,
HINC75_CY [decimal](19, 4) NULL,
HINC100_CY [decimal](19, 4) NULL,
HINC150_CY [decimal](19, 4) NULL,
HINC200_CY [decimal](19, 4) NULL,
PCI_CY [decimal](19, 4) NULL,
WHITE_CY [decimal](19, 4) NULL,
BLACK_CY [decimal](19, 4) NULL,
AMERIND_CY [decimal](19, 4) NULL,
ASIAN_CY [decimal](19, 4) NULL,
PACIFIC_CY [decimal](19, 4) NULL,
OTHRACE_CY [decimal](19, 4) NULL,
RACE2UP_CY [decimal](19, 4) NULL,
HISPPOPCY [decimal](19, 4) NULL,
ACSUNT1DET [decimal](19, 4) NULL,
ACSUNT1ATT [decimal](19, 4) NULL,
ACSUNT2 [decimal](19, 4) NULL,
ACSUNT3 [decimal](19, 4) NULL,
ACSUNT5 [decimal](19, 4) NULL,
ACSUNT10 [decimal](19, 4) NULL,
ACSUNT20 [decimal](19, 4) NULL,
ACSUNT50UP [decimal](19, 4) NULL,
ACSUNTMOB [decimal](19, 4) NULL,
ACSUNTOTH [decimal](19, 4) NULL,
ACSBLT2005 [decimal](19, 4) NULL,
ACSBLT2000 [decimal](19, 4) NULL,
ACSBLT1990 [decimal](19, 4) NULL,
ACSBLT1980 [decimal](19, 4) NULL,
ACSBLT1970 [decimal](19, 4) NULL,
ACSBLT1960 [decimal](19, 4) NULL,
ACSBLT1950 [decimal](19, 4) NULL,
ACSBLT1940 [decimal](19, 4) NULL,
ACSBLT1939 [decimal](19, 4) NULL,
ACSOMV2005 [decimal](19, 4) NULL,
ACSOMV2000 [decimal](19, 4) NULL,
ACSOMV1990 [decimal](19, 4) NULL,
ACSOMV1980 [decimal](19, 4) NULL,
ACSOMV1970 [decimal](19, 4) NULL,
ACSOMV1969 [decimal](19, 4) NULL,
ACSRMV2005 [decimal](19, 4) NULL,
ACSRMV2000 [decimal](19, 4) NULL,
ACSRMV1990 [decimal](19, 4) NULL,
ACSRMV1980 [decimal](19, 4) NULL,
ACSRMV1970 [decimal](19, 4) NULL,
ACSRMV1969 [decimal](19, 4) NULL,
ACSOCCBASE [decimal](19, 4) NULL,
ACSA15I0 [decimal](19, 4) NULL,
ACSA15I10 [decimal](19, 4) NULL,
ACSA15I15 [decimal](19, 4) NULL,
ACSA15I20 [decimal](19, 4) NULL,
ACSA15I25 [decimal](19, 4) NULL,
ACSA15I30 [decimal](19, 4) NULL,
ACSA15I35 [decimal](19, 4) NULL,
ACSA15I40 [decimal](19, 4) NULL,
ACSA15I45 [decimal](19, 4) NULL,
ACSA15I50 [decimal](19, 4) NULL,
ACSA15I60 [decimal](19, 4) NULL,
ACSA15I75 [decimal](19, 4) NULL,
ACSA15I100 [decimal](19, 4) NULL,
ACSA15I125 [decimal](19, 4) NULL,
ACSA15I150 [decimal](19, 4) NULL,
ACSA15I200 [decimal](19, 4) NULL,
ACSA25I0 [decimal](19, 4) NULL,
ACSA25I10 [decimal](19, 4) NULL,
ACSA25I15 [decimal](19, 4) NULL,
ACSA25I20 [decimal](19, 4) NULL,
ACSA25I25 [decimal](19, 4) NULL,
ACSA25I30 [decimal](19, 4) NULL,
ACSA25I35 [decimal](19, 4) NULL,
ACSA25I40 [decimal](19, 4) NULL,
ACSA25I45 [decimal](19, 4) NULL,
ACSA25I50 [decimal](19, 4) NULL,
ACSA25I60 [decimal](19, 4) NULL,
ACSA25I75 [decimal](19, 4) NULL,
ACSA25I100 [decimal](19, 4) NULL,
ACSA25I125 [decimal](19, 4) NULL,
ACSA25I150 [decimal](19, 4) NULL,
ACSA25I200 [decimal](19, 4) NULL,
ACSA45I0 [decimal](19, 4) NULL,
ACSA45I10 [decimal](19, 4) NULL,
ACSA45I15 [decimal](19, 4) NULL,
ACSA45I20 [decimal](19, 4) NULL,
ACSA45I25 [decimal](19, 4) NULL,
ACSA45I30 [decimal](19, 4) NULL,
ACSA45I35 [decimal](19, 4) NULL,
ACSA45I40 [decimal](19, 4) NULL,
ACSA45I45 [decimal](19, 4) NULL,
ACSA45I50 [decimal](19, 4) NULL,
ACSA45I60 [decimal](19, 4) NULL,
ACSA45I75 [decimal](19, 4) NULL,
ACSA45I100 [decimal](19, 4) NULL,
ACSA45I125 [decimal](19, 4) NULL,
ACSA45I150 [decimal](19, 4) NULL,
ACSA45I200 [decimal](19, 4) NULL,
ACSA65I0 [decimal](19, 4) NULL,
ACSA65I10 [decimal](19, 4) NULL,
ACSA65I15 [decimal](19, 4) NULL,
ACSA65I20 [decimal](19, 4) NULL,
ACSA65I25 [decimal](19, 4) NULL,
ACSA65I30 [decimal](19, 4) NULL,
ACSA65I35 [decimal](19, 4) NULL,
ACSA65I40 [decimal](19, 4) NULL,
ACSA65I45 [decimal](19, 4) NULL,
ACSA65I50 [decimal](19, 4) NULL,
ACSA65I60 [decimal](19, 4) NULL,
ACSA65I75 [decimal](19, 4) NULL,
ACSA65I100 [decimal](19, 4) NULL,
ACSA65I125 [decimal](19, 4) NULL,
ACSA65I150 [decimal](19, 4) NULL,
ACSA65I200 [decimal](19, 4) NULL,
X3019_X [decimal](19, 4) NULL,
X4057_X [decimal](19, 4) NULL,
X4060_X [decimal](19, 4) NULL,
X4080_X [decimal](19, 4) NULL,
HINC_50KPLUS_CY [decimal](19, 4) NULL,
HINC_75KPLUS_CY [decimal](19, 4) NULL,
HINC_100KPLUS [decimal](19, 4) NULL,
AGG_INCOME [decimal](19, 4) NULL,
TOTHU_CY [decimal](19, 4) NULL,
VACANT_CY [decimal](19, 4) NULL,
X4082_X [decimal](19, 4) NULL,
X4084_X [decimal](19, 4) NULL,
X4085_X [decimal](19, 4) NULL,
X4095_X [decimal](19, 4) NULL,
X4096_X [decimal](19, 4) NULL,
X4011_X [decimal](19, 4) NULL,
X4012_X [decimal](19, 4) NULL,
X4013_X [decimal](19, 4) NULL,
X3025_X [decimal](19, 4) NULL,
X3041_X [decimal](19, 4) NULL,
X3047_X [decimal](19, 4) NULL,
X3048_X [decimal](19, 4) NULL,
HI_PROD_PROXY_CY [decimal](19, 4) NULL,
 CONSTRAINT [PK_demographics_denorm] PRIMARY KEY CLUSTERED 
(
	[demographic_denorm_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

SET ANSI_PADDING OFF
GO





/****** Object:  Index [IX_trade_area__assumed_closed_date]    Script Date: 04/07/2013 12:42:46 ******/
CREATE NONCLUSTERED INDEX [IX_trade_area__assumed_closed_date] ON [dbo].[demographics_denorm] 
(
	[trade_area_id] ASC,
	[assumed_closed_date] ASC
)
INCLUDE ( [store_id],
[company_name],
[assumed_opened_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area__assumed_start_date] ON [dbo].[demographics_denorm] 
(
	[trade_area_id] ASC,
	[assumed_opened_date] ASC
)
INCLUDE ( [store_id],
[company_name],
[assumed_closed_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area_id] ON [dbo].[demographics_denorm] 
(
	[trade_area_id] ASC
)
INCLUDE ( [demographic_denorm_id],
[store_id],
[company_name],
[assumed_opened_date],
[assumed_closed_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area_ids__assumed_dates] ON [dbo].[demographics_denorm] 
(
	[trade_area_id] ASC,
	[assumed_opened_date] ASC,
	[assumed_closed_date] ASC
)
INCLUDE ( [demographic_denorm_id],
[store_id],
[company_name]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
