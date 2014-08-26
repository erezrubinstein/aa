USE TFM_OCT3_CMA_100713
GO

/****** Object:  Table [dbo].[demographics_denorm_3_mile]    Script Date: 04/07/2013 12:32:40 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

SET ANSI_PADDING ON
GO


CREATE TABLE [dbo].[demographics_denorm_3_mile](
	[demographic_denorm_id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[store_id] [int] NOT NULL,
	[company_name] [varchar](200) NOT NULL,
	[assumed_opened_date] [datetime] NOT NULL,
	[assumed_closed_date] [datetime] NULL,
	TOTHH_CY [decimal](19, 5) NULL,
MEDAGE_CY [decimal](19, 5) NULL,
HINC0_CY [decimal](19, 5) NULL,
HINC15_CY [decimal](19, 5) NULL,
HINC25_CY [decimal](19, 5) NULL,
HINC35_CY [decimal](19, 5) NULL,
HINC50_CY [decimal](19, 5) NULL,
HINC75_CY [decimal](19, 5) NULL,
HINC100_CY [decimal](19, 5) NULL,
HINC150_CY [decimal](19, 5) NULL,
HINC200_CY [decimal](19, 5) NULL,
MEDHINC_CY [decimal](19, 5) NULL,
AVGHINC_CY [decimal](19, 5) NULL,
PCI_CY [decimal](19, 5) NULL,
POP0_CY [decimal](19, 5) NULL,
POP5_CY [decimal](19, 5) NULL,
POP10_CY [decimal](19, 5) NULL,
POP15_CY [decimal](19, 5) NULL,
POP20_CY [decimal](19, 5) NULL,
POP2534_CY [decimal](19, 5) NULL,
POP3544_CY [decimal](19, 5) NULL,
POP4554_CY [decimal](19, 5) NULL,
POP5564_CY [decimal](19, 5) NULL,
POP6574_CY [decimal](19, 5) NULL,
POP7584_CY [decimal](19, 5) NULL,
POP85_CY [decimal](19, 5) NULL,
WHITE_CY [decimal](19, 5) NULL,
BLACK_CY [decimal](19, 5) NULL,
AMERIND_CY [decimal](19, 5) NULL,
ASIAN_CY [decimal](19, 5) NULL,
PACIFIC_CY [decimal](19, 5) NULL,
OTHRACE_CY [decimal](19, 5) NULL,
RACE2UP_CY [decimal](19, 5) NULL,
HISPPOPCY [decimal](19, 5) NULL,
X1002_X [decimal](19, 5) NULL,
X8029_X [decimal](19, 5) NULL,
HINC_50KPLUS_CY [decimal](19, 5) NULL,
HINC_75KPLUS_CY [decimal](19, 5) NULL,
HINC_100KPLUS [decimal](19, 5) NULL,
POP_25PLUS_CY [decimal](19, 5) NULL,
POP_30PLUS_CY [decimal](19, 5) NULL,
AGG_INCOME [decimal](19, 5) NULL,
FEMALE_18TO34 [decimal](19, 5) NULL,
X10003_X [decimal](19, 5) NULL,
X10008_X [decimal](19, 5) NULL,
X8031_X [decimal](19, 5) NULL,
X8035_X [decimal](19, 5) NULL,
X4029_X [decimal](19, 5) NULL,
X4032_X [decimal](19, 5) NULL,
X10006_X [decimal](19, 5) NULL,
X10007_X [decimal](19, 5) NULL,
X10009_X [decimal](19, 5) NULL,
HINC_35TO100K [decimal](19, 5) NULL,
PROX_MSGROCERY [decimal](19, 5) NULL,
 CONSTRAINT [PK_demographics_denorm_3_mile] PRIMARY KEY CLUSTERED 
(
	[demographic_denorm_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

SET ANSI_PADDING OFF
GO





/****** Object:  Index [IX_trade_area__assumed_closed_date]    Script Date: 04/07/2013 12:42:46 ******/
CREATE NONCLUSTERED INDEX [IX_trade_area__assumed_closed_date] ON [dbo].[demographics_denorm_3_mile] 
(
	[trade_area_id] ASC,
	[assumed_closed_date] ASC
)
INCLUDE ( [store_id],
[company_name],
[assumed_opened_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area__assumed_start_date] ON [dbo].[demographics_denorm_3_mile] 
(
	[trade_area_id] ASC,
	[assumed_opened_date] ASC
)
INCLUDE ( [store_id],
[company_name],
[assumed_closed_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area_id] ON [dbo].[demographics_denorm_3_mile] 
(
	[trade_area_id] ASC
)
INCLUDE ( [demographic_denorm_id],
[store_id],
[company_name],
[assumed_opened_date],
[assumed_closed_date]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IX_trade_area_ids__assumed_dates] ON [dbo].[demographics_denorm_3_mile] 
(
	[trade_area_id] ASC,
	[assumed_opened_date] ASC,
	[assumed_closed_date] ASC
)
INCLUDE ( [demographic_denorm_id],
[store_id],
[company_name]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
