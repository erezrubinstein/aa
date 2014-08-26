USE DOLLFULL_JUN13_CMA_062313
GO

/****** Object:  Table [dbo].[demographics_denorm_5_mile]    Script Date: 04/07/2013 12:32:40 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

SET ANSI_PADDING ON
GO

CREATE TABLE [dbo].[demographics_denorm_5_mile](
	[demographic_denorm_id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[store_id] [int] NOT NULL,
	[company_name] [varchar](200) NOT NULL,
	[assumed_opened_date] [datetime] NOT NULL,
	[assumed_closed_date] [datetime] NULL,
	TOTPOP_CY [decimal](19, 9) NULL,
TOTHH_CY [decimal](19, 9) NULL,
MEDAGE_CY [decimal](19, 9) NULL,
HINC0_CY [decimal](19, 9) NULL,
HINC15_CY [decimal](19, 9) NULL,
HINC25_CY [decimal](19, 9) NULL,
HINC35_CY [decimal](19, 9) NULL,
HINC50_CY [decimal](19, 9) NULL,
HINC75_CY [decimal](19, 9) NULL,
HINC100_CY [decimal](19, 9) NULL,
HINC150_CY [decimal](19, 9) NULL,
HINC200_CY [decimal](19, 9) NULL,
MEDHINC_CY [decimal](19, 9) NULL,
PCI_CY [decimal](19, 9) NULL,
POP0_CY [decimal](19, 9) NULL,
POP5_CY [decimal](19, 9) NULL,
POP10_CY [decimal](19, 9) NULL,
POP15_CY [decimal](19, 9) NULL,
POP20_CY [decimal](19, 9) NULL,
POP2534_CY [decimal](19, 9) NULL,
POP3544_CY [decimal](19, 9) NULL,
POP4554_CY [decimal](19, 9) NULL,
POP5564_CY [decimal](19, 9) NULL,
POP6574_CY [decimal](19, 9) NULL,
POP7584_CY [decimal](19, 9) NULL,
POP85_CY [decimal](19, 9) NULL,
WHITE_CY [decimal](19, 9) NULL,
BLACK_CY [decimal](19, 9) NULL,
AMERIND_CY [decimal](19, 9) NULL,
ASIAN_CY [decimal](19, 9) NULL,
PACIFIC_CY [decimal](19, 9) NULL,
OTHRACE_CY [decimal](19, 9) NULL,
RACE2UP_CY [decimal](19, 9) NULL,
HISPPOPCY [decimal](19, 9) NULL,
ACSFEMPBAS [decimal](19, 9) NULL,
ACSKDSLT6O [decimal](19, 9) NULL,
ACSLT6FLF [decimal](19, 9) NULL,
ACSLT6FNLF [decimal](19, 9) NULL,
ACSKIDS [decimal](19, 9) NULL,
ACSKDSFLF [decimal](19, 9) NULL,
ACSKDSFNLF [decimal](19, 9) NULL,
ACSKDS617O [decimal](19, 9) NULL,
ACS617FLF [decimal](19, 9) NULL,
ACS617FNLF [decimal](19, 9) NULL,
ACSNOKIDS [decimal](19, 9) NULL,
ACSNKDFLF [decimal](19, 9) NULL,
ACSNKDFNLF [decimal](19, 9) NULL,
ACSHPOVBAS [decimal](19, 9) NULL,
ACSHHBPOV [decimal](19, 9) NULL,
ACSBPOVMCF [decimal](19, 9) NULL,
ACSBPOVOFM [decimal](19, 9) NULL,
ACSBPOVOFF [decimal](19, 9) NULL,
ACSBPOVNFM [decimal](19, 9) NULL,
ACSBPOVNFF [decimal](19, 9) NULL,
ACSHHAPOV [decimal](19, 9) NULL,
ACSAPOVMCF [decimal](19, 9) NULL,
ACSAPOVOFM [decimal](19, 9) NULL,
ACSAPOVOFF [decimal](19, 9) NULL,
ACSAPOVNFM [decimal](19, 9) NULL,
ACSAPOVNFF [decimal](19, 9) NULL,
X5001_X [decimal](19, 9) NULL,
X5066_X [decimal](19, 9) NULL,
X1002_X [decimal](19, 9) NULL,
X4028_X [decimal](19, 9) NULL,
X10002_X [decimal](19, 9) NULL,
X12002_X [decimal](19, 9) NULL,
X12005_X [decimal](19, 9) NULL,
	agg_income [decimal](30, 9) NULL,
	less_than_50K_HH [decimal](30, 9) NULL,
	less_than_75K_HH [decimal](30, 9) NULL,
	pct_black [decimal](30, 9) NULL,
	pct_hispanic [decimal](30, 9) NULL,
	femHH [decimal](30, 9) NULL,
 CONSTRAINT [PK_demographics_denorm_5_mile] PRIMARY KEY CLUSTERED 
(
	[demographic_denorm_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

SET ANSI_PADDING OFF
GO





/****** Object:  Index [IX_trade_area__assumed_closed_date]    Script Date: 04/07/2013 12:42:46 ******/
CREATE NONCLUSTERED INDEX [IX_trade_area__assumed_closed_date] ON [dbo].[demographics_denorm_5_mile] 
(
	[trade_area_id] ASC,
	[assumed_closed_date] ASC
)
INCLUDE ( [store_id],
[company_name],
[assumed_opened_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area__assumed_start_date] ON [dbo].[demographics_denorm_5_mile] 
(
	[trade_area_id] ASC,
	[assumed_opened_date] ASC
)
INCLUDE ( [store_id],
[company_name],
[assumed_closed_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area_id] ON [dbo].[demographics_denorm_5_mile] 
(
	[trade_area_id] ASC
)
INCLUDE ( [demographic_denorm_id],
[store_id],
[company_name],
[assumed_opened_date],
[assumed_closed_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area_ids__assumed_dates] ON [dbo].[demographics_denorm_5_mile] 
(
	[trade_area_id] ASC,
	[assumed_opened_date] ASC,
	[assumed_closed_date] ASC
)
INCLUDE ( [demographic_denorm_id],
[store_id],
[company_name]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
