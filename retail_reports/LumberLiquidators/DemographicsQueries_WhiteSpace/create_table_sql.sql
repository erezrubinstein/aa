USE LL_OCT13_CMA_100213
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
	TOTPOP_CY [decimal](19, 5) NULL,
TOTHH_CY [decimal](19, 5) NULL,
OWNER_CY [decimal](19, 5) NULL,
RENTER_CY [decimal](19, 5) NULL,
PCI_CY [decimal](19, 5) NULL,
ACSUNT1DET [decimal](19, 5) NULL,
ACSUNT1ATT [decimal](19, 5) NULL,
ACSUNT2 [decimal](19, 5) NULL,
ACSUNT3 [decimal](19, 5) NULL,
ACSUNT5 [decimal](19, 5) NULL,
ACSUNT10 [decimal](19, 5) NULL,
ACSUNT20 [decimal](19, 5) NULL,
ACSUNT50UP [decimal](19, 5) NULL,
ACSUNTMOB [decimal](19, 5) NULL,
ACSUNTOTH [decimal](19, 5) NULL,
ACSBLT2005 [decimal](19, 5) NULL,
ACSBLT2000 [decimal](19, 5) NULL,
ACSBLT1990 [decimal](19, 5) NULL,
ACSBLT1980 [decimal](19, 5) NULL,
ACSBLT1970 [decimal](19, 5) NULL,
ACSBLT1960 [decimal](19, 5) NULL,
ACSBLT1950 [decimal](19, 5) NULL,
ACSBLT1940 [decimal](19, 5) NULL,
ACSBLT1939 [decimal](19, 5) NULL,
ACSOMV2005 [decimal](19, 5) NULL,
ACSOMV2000 [decimal](19, 5) NULL,
ACSOMV1990 [decimal](19, 5) NULL,
ACSOMV1980 [decimal](19, 5) NULL,
ACSOMV1970 [decimal](19, 5) NULL,
ACSOMV1969 [decimal](19, 5) NULL,
HINC_50KPLUS_CY [decimal](19, 5) NULL,
HINC_75KPLUS_CY [decimal](19, 5) NULL,
AGG_INCOME [decimal](19, 5) NULL,
TOTHU_CY [decimal](19, 5) NULL,
VACANT_CY [decimal](19, 5) NULL,
X3025_X [decimal](19, 5) NULL,
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
