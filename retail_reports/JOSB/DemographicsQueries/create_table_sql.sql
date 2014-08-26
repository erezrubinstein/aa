USE JOSB_OCT14_CMA_101113
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
	TOTPOP_FY [decimal](19, 5) NULL,
TOTHH10 [decimal](19, 5) NULL,
TOTHH_CY [decimal](19, 5) NULL,
TOTHH_FY [decimal](19, 5) NULL,
FAMHH10 [decimal](19, 5) NULL,
FAMHH_CY [decimal](19, 5) NULL,
FAMHH_FY [decimal](19, 5) NULL,
AVGHHSZ10 [decimal](19, 5) NULL,
AVGHHSZ_CY [decimal](19, 5) NULL,
AVGHHSZ_FY [decimal](19, 5) NULL,
OWNER10 [decimal](19, 5) NULL,
OWNER_CY [decimal](19, 5) NULL,
OWNER_FY [decimal](19, 5) NULL,
RENTER10 [decimal](19, 5) NULL,
RENTER_CY [decimal](19, 5) NULL,
RENTER_FY [decimal](19, 5) NULL,
MEDAGE10 [decimal](19, 5) NULL,
MEDAGE_CY [decimal](19, 5) NULL,
MEDAGE_FY [decimal](19, 5) NULL,
SCRIPT_ANU [decimal](19, 5) NULL,
POPRATE_S [decimal](19, 5) NULL,
TR_POP_NAT [decimal](19, 5) NULL,
SCRIPT_A_1 [decimal](19, 5) NULL,
HHRATE_S [decimal](19, 5) NULL,
TR_HH_NAT [decimal](19, 5) NULL,
SCRIPT_A_2 [decimal](19, 5) NULL,
FAMRATE_S [decimal](19, 5) NULL,
TR_FAM_NAT [decimal](19, 5) NULL,
SCRIPT_AN1 [decimal](19, 5) NULL,
OWNRATE_S [decimal](19, 5) NULL,
TR_OWN_NAT [decimal](19, 5) NULL,
SCRIPT_AN0 [decimal](19, 5) NULL,
INCRATE_S [decimal](19, 5) NULL,
TR_MHI_NAT [decimal](19, 5) NULL,
HINC0_CY [decimal](19, 5) NULL,
HINC0_CY_P [decimal](19, 5) NULL,
HINC0_FY [decimal](19, 5) NULL,
HINC0_FY_P [decimal](19, 5) NULL,
HINC15_CY [decimal](19, 5) NULL,
HINC15_CY_P [decimal](19, 5) NULL,
HINC15_FY [decimal](19, 5) NULL,
HINC15_FY_P [decimal](19, 5) NULL,
HINC25_CY [decimal](19, 5) NULL,
HINC25_CY_P [decimal](19, 5) NULL,
HINC25_FY [decimal](19, 5) NULL,
HINC25_FY_P [decimal](19, 5) NULL,
HINC35_CY [decimal](19, 5) NULL,
HINC35_CY_P [decimal](19, 5) NULL,
HINC35_FY [decimal](19, 5) NULL,
HINC35_FY_P [decimal](19, 5) NULL,
HINC50_CY [decimal](19, 5) NULL,
HINC50_CY_P [decimal](19, 5) NULL,
HINC50_FY [decimal](19, 5) NULL,
HINC50_FY_P [decimal](19, 5) NULL,
HINC75_CY [decimal](19, 5) NULL,
HINC75_CY_P [decimal](19, 5) NULL,
HINC75_FY [decimal](19, 5) NULL,
HINC75_FY_P [decimal](19, 5) NULL,
HINC100_CY [decimal](19, 5) NULL,
HINC100_CY_P [decimal](19, 5) NULL,
HINC100_FY [decimal](19, 5) NULL,
HINC100_FY_P [decimal](19, 5) NULL,
HINC150_CY [decimal](19, 5) NULL,
HINC150_CY_P [decimal](19, 5) NULL,
HINC150_FY [decimal](19, 5) NULL,
HINC150_FY_P [decimal](19, 5) NULL,
HINC200_CY [decimal](19, 5) NULL,
HINC200_CY_P [decimal](19, 5) NULL,
HINC200_FY [decimal](19, 5) NULL,
HINC200_FY_P [decimal](19, 5) NULL,
MEDHINC_CY [decimal](19, 5) NULL,
MEDHINC_FY [decimal](19, 5) NULL,
AVGHINC_CY [decimal](19, 5) NULL,
AVGHINC_FY [decimal](19, 5) NULL,
PCI_CY [decimal](19, 5) NULL,
PCI_FY [decimal](19, 5) NULL,
POP0C10 [decimal](19, 5) NULL,
POP0C10_P [decimal](19, 5) NULL,
POP0_CY [decimal](19, 5) NULL,
POP0_CY_P [decimal](19, 5) NULL,
POP0_FY [decimal](19, 5) NULL,
POP0_FY_P [decimal](19, 5) NULL,
POP5C10 [decimal](19, 5) NULL,
POP5C10_P [decimal](19, 5) NULL,
POP5_CY [decimal](19, 5) NULL,
POP5_CY_P [decimal](19, 5) NULL,
POP5_FY [decimal](19, 5) NULL,
POP5_FY_P [decimal](19, 5) NULL,
POP10C10 [decimal](19, 5) NULL,
POP10C10_P [decimal](19, 5) NULL,
POP10_CY [decimal](19, 5) NULL,
POP10_CY_P [decimal](19, 5) NULL,
POP10_FY [decimal](19, 5) NULL,
POP10_FY_P [decimal](19, 5) NULL,
POP15C10 [decimal](19, 5) NULL,
POP15C10_P [decimal](19, 5) NULL,
POP15_CY [decimal](19, 5) NULL,
POP15_CY_P [decimal](19, 5) NULL,
POP15_FY [decimal](19, 5) NULL,
POP15_FY_P [decimal](19, 5) NULL,
POP20C10 [decimal](19, 5) NULL,
POP20C10_P [decimal](19, 5) NULL,
POP20_CY [decimal](19, 5) NULL,
POP20_CY_P [decimal](19, 5) NULL,
POP20_FY [decimal](19, 5) NULL,
POP20_FY_P [decimal](19, 5) NULL,
POP2534C10 [decimal](19, 5) NULL,
POP2534C10_P [decimal](19, 5) NULL,
POP2534_CY [decimal](19, 5) NULL,
POP2534_CY_P [decimal](19, 5) NULL,
POP2534_FY [decimal](19, 5) NULL,
POP2534_FY_P [decimal](19, 5) NULL,
POP3544C10 [decimal](19, 5) NULL,
POP3544C10_P [decimal](19, 5) NULL,
POP3544_CY [decimal](19, 5) NULL,
POP3544_CY_P [decimal](19, 5) NULL,
POP3544_FY [decimal](19, 5) NULL,
POP3544_FY_P [decimal](19, 5) NULL,
POP4554C10 [decimal](19, 5) NULL,
POP4554C10_P [decimal](19, 5) NULL,
POP4554_CY [decimal](19, 5) NULL,
POP4554_CY_P [decimal](19, 5) NULL,
POP4554_FY [decimal](19, 5) NULL,
POP4554_FY_P [decimal](19, 5) NULL,
POP5564C10 [decimal](19, 5) NULL,
POP5564C10_P [decimal](19, 5) NULL,
POP5564_CY [decimal](19, 5) NULL,
POP5564_CY_P [decimal](19, 5) NULL,
POP5564_FY [decimal](19, 5) NULL,
POP5564_FY_P [decimal](19, 5) NULL,
POP6574C10 [decimal](19, 5) NULL,
POP6574C10_P [decimal](19, 5) NULL,
POP6574_CY [decimal](19, 5) NULL,
POP6574_CY_P [decimal](19, 5) NULL,
POP6574_FY [decimal](19, 5) NULL,
POP6574_FY_P [decimal](19, 5) NULL,
POP7584C10 [decimal](19, 5) NULL,
POP7584C10_P [decimal](19, 5) NULL,
POP7584_CY [decimal](19, 5) NULL,
POP7584_CY_P [decimal](19, 5) NULL,
POP7584_FY [decimal](19, 5) NULL,
POP7584_FY_P [decimal](19, 5) NULL,
POP85C10 [decimal](19, 5) NULL,
POP85PC10_P [decimal](19, 5) NULL,
POP85_CY [decimal](19, 5) NULL,
POP85P_CY_P [decimal](19, 5) NULL,
POP85_FY [decimal](19, 5) NULL,
POP85P_FY_P [decimal](19, 5) NULL,
WHITE10 [decimal](19, 5) NULL,
WHITE10_P [decimal](19, 5) NULL,
WHITE_CY [decimal](19, 5) NULL,
WHITE_CY_P [decimal](19, 5) NULL,
WHITE_FY [decimal](19, 5) NULL,
WHITE_FY_P [decimal](19, 5) NULL,
BLACK10 [decimal](19, 5) NULL,
BLACK10_P [decimal](19, 5) NULL,
BLACK_CY [decimal](19, 5) NULL,
BLACK_CY_P [decimal](19, 5) NULL,
BLACK_FY [decimal](19, 5) NULL,
BLACK_FY_P [decimal](19, 5) NULL,
AMERIND10 [decimal](19, 5) NULL,
AMERIND10_P [decimal](19, 5) NULL,
AMERIND_CY [decimal](19, 5) NULL,
AMERIND_CY_P [decimal](19, 5) NULL,
AMERIND_FY [decimal](19, 5) NULL,
AMERIND_FY_P [decimal](19, 5) NULL,
ASIAN10 [decimal](19, 5) NULL,
ASIAN10_P [decimal](19, 5) NULL,
ASIAN_CY [decimal](19, 5) NULL,
ASIAN_CY_P [decimal](19, 5) NULL,
ASIAN_FY [decimal](19, 5) NULL,
ASIAN_FY_P [decimal](19, 5) NULL,
PACIFIC10 [decimal](19, 5) NULL,
PACIFIC10_P [decimal](19, 5) NULL,
PACIFIC_CY [decimal](19, 5) NULL,
PACIFIC_CY_P [decimal](19, 5) NULL,
PACIFIC_FY [decimal](19, 5) NULL,
PACIFIC_FY_P [decimal](19, 5) NULL,
OTHRACE10 [decimal](19, 5) NULL,
OTHRACE10_P [decimal](19, 5) NULL,
OTHRACE_CY [decimal](19, 5) NULL,
OTHRACE_CY_P [decimal](19, 5) NULL,
OTHRACE_FY [decimal](19, 5) NULL,
OTHRACE_FY_P [decimal](19, 5) NULL,
RACE2UP10 [decimal](19, 5) NULL,
RACE2UP10_P [decimal](19, 5) NULL,
RACE2UP_CY [decimal](19, 5) NULL,
RACE2UP_CY_P [decimal](19, 5) NULL,
RACE2UP_FY [decimal](19, 5) NULL,
RACE2UP_FY_P [decimal](19, 5) NULL,
HISPPOP10 [decimal](19, 5) NULL,
HISPPOP10_P [decimal](19, 5) NULL,
HISPPOPCY [decimal](19, 5) NULL,
HISPPOP_CY_P [decimal](19, 5) NULL,
HISPPOPFY [decimal](19, 5) NULL,
HISPPOPFY_P [decimal](19, 5) NULL,
POPRATE [decimal](19, 5) NULL,
HHRATE [decimal](19, 5) NULL,
FAMRATE [decimal](19, 5) NULL,
OWNRATE [decimal](19, 5) NULL,
INCRATE [decimal](19, 5) NULL,
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
