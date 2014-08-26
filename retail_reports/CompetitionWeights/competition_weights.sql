USE [retaildb_timeseries_auto_parts_v5_shrunken]
GO

/****** Object:  Table [dbo].[weighed_competitive_weights]    Script Date: 04/07/2013 14:42:30 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[weighed_competitive_weights](
	[weighed_competitive_companies] [int] IDENTITY(1,1) NOT NULL,
	[home_company_id] [int] NOT NULL,
	[away_company_id] [int] NOT NULL,
	[strength] [float] NOT NULL,
 CONSTRAINT [PK_weighed_competitive_weights] PRIMARY KEY CLUSTERED 
(
	[weighed_competitive_companies] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO


CREATE NONCLUSTERED INDEX [IX_home_company__away_company] ON [dbo].[weighed_competitive_weights] 
(
	[home_company_id] ASC,
	[away_company_id] ASC
)
INCLUDE ( [strength]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


