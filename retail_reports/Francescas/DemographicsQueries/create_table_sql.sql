USE FRAN_JUN13_CMA_070313
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
POP0_CY [decimal](19, 4) NULL,
POP5_CY [decimal](19, 4) NULL,
POP10_CY [decimal](19, 4) NULL,
POP15_CY [decimal](19, 4) NULL,
POP20_CY [decimal](19, 4) NULL,
POP2534_CY [decimal](19, 4) NULL,
POP3544_CY [decimal](19, 4) NULL,
POP4554_CY [decimal](19, 4) NULL,
POP5564_CY [decimal](19, 4) NULL,
POP6574_CY [decimal](19, 4) NULL,
POP7584_CY [decimal](19, 4) NULL,
POP85_CY [decimal](19, 4) NULL,
WHITE_CY [decimal](19, 4) NULL,
BLACK_CY [decimal](19, 4) NULL,
AMERIND_CY [decimal](19, 4) NULL,
ASIAN_CY [decimal](19, 4) NULL,
PACIFIC_CY [decimal](19, 4) NULL,
OTHRACE_CY [decimal](19, 4) NULL,
RACE2UP_CY [decimal](19, 4) NULL,
HISPPOPCY [decimal](19, 4) NULL,
Count_1 [decimal](19, 4) NULL,
Count_2 [decimal](19, 4) NULL,
Count_3 [decimal](19, 4) NULL,
Count_4 [decimal](19, 4) NULL,
Count_5 [decimal](19, 4) NULL,
Count_6 [decimal](19, 4) NULL,
Count_7 [decimal](19, 4) NULL,
Count_8 [decimal](19, 4) NULL,
Count_9 [decimal](19, 4) NULL,
Count_10 [decimal](19, 4) NULL,
Count_11 [decimal](19, 4) NULL,
Count_12 [decimal](19, 4) NULL,
Count_13 [decimal](19, 4) NULL,
Count_14 [decimal](19, 4) NULL,
Count_15 [decimal](19, 4) NULL,
Count_16 [decimal](19, 4) NULL,
Count_17 [decimal](19, 4) NULL,
Count_18 [decimal](19, 4) NULL,
Count_19 [decimal](19, 4) NULL,
Count_20 [decimal](19, 4) NULL,
Count_21 [decimal](19, 4) NULL,
Count_22 [decimal](19, 4) NULL,
Count_23 [decimal](19, 4) NULL,
Count_24 [decimal](19, 4) NULL,
Count_25 [decimal](19, 4) NULL,
Count_26 [decimal](19, 4) NULL,
Count_27 [decimal](19, 4) NULL,
Count_28 [decimal](19, 4) NULL,
Count_29 [decimal](19, 4) NULL,
Count_30 [decimal](19, 4) NULL,
ACSOCCBASE [decimal](19, 4) NULL,
X5015_X [decimal](19, 4) NULL,
X5077_X [decimal](19, 4) NULL,
HINC_50KPLUS_CY [decimal](19, 4) NULL,
HINC_75KPLUS_CY [decimal](19, 4) NULL,
HINC_100KPLUS [decimal](19, 4) NULL,
POP_25PLUS_CY [decimal](19, 4) NULL,
POP_30PLUS_CY [decimal](19, 4) NULL,
AGG_INCOME [decimal](19, 4) NULL,
FEMALE_18TO34 [decimal](19, 4) NULL,
PROX_WAPP_JEW [decimal](19, 4) NULL,
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
