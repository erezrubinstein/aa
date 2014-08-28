USE [retaildb_dev]
GO

/****** Object:  Table [dbo].[demographic_types]    Script Date: 10/07/2012 18:40:12 ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[demographic_types]') AND type in (N'U'))
DROP TABLE [dbo].[demographic_types]
GO

USE [retaildb_dev]
GO

/****** Object:  Table [dbo].[demographic_types]    Script Date: 10/07/2012 18:40:12 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

SET ANSI_PADDING ON
GO

CREATE TABLE [dbo].[demographic_types](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[name] [varchar](50) NOT NULL,
	[caption] [varchar](1000) NOT NULL,
	[type] [varchar](10) NOT NULL,
	[created_at] datetime NOT NULL,
	[updated_at] datetime NOT NULL
 CONSTRAINT [PK_demographic_types] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY],
 CONSTRAINT [UK_demographic_types] UNIQUE NONCLUSTERED 
(
	[name] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

SET ANSI_PADDING OFF
GO







USE [retaildb_dev]
GO

/****** Object:  Table [dbo].[demographic_values]    Script Date: 10/07/2012 18:34:04 ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[demographic_numvalues]') AND type in (N'U'))
DROP TABLE [dbo].[demographic_numvalues]
GO

USE [retaildb_dev]
GO

/****** Object:  Table [dbo].[demographic_values]    Script Date: 10/07/2012 18:34:04 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[demographic_numvalues](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[demographic_type_id] [int] NOT NULL,
	[value] [varchar](200) NOT NULL,
	[created_at] datetime NOT NULL,
	[updated_at] datetime NOT NULL
 CONSTRAINT [PK_demographic_numvalues] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO






USE [retaildb_dev]
GO

/****** Object:  Table [dbo].[demographic_values]    Script Date: 10/07/2012 18:34:04 ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[demographic_strvalues]') AND type in (N'U'))
DROP TABLE [dbo].[demographic_strvalues]
GO

USE [retaildb_dev]
GO

/****** Object:  Table [dbo].[demographic_values]    Script Date: 10/07/2012 18:34:04 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[demographic_strvalues](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[demographic_type_id] [int] NOT NULL,
	[value] [varchar](200) NOT NULL,
	[created_at] datetime NOT NULL,
	[updated_at] datetime NOT NULL
 CONSTRAINT [PK_demographic_strvalues] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO






USE [retaildb_dev]
GO


/****** Object:  Table [dbo].[demographic_values]    Script Date: 10/07/2012 18:34:04 ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[competitive_stores]') AND type in (N'U'))
DROP TABLE [dbo].[competitive_stores]
GO


CREATE TABLE [dbo].[competitive_stores]
(
   [id] [int] IDENTITY(1,1) NOT NULL,
   [competition_id] [int] NOT NULL,   
   [home_store_id] [int] NOT NULL,
   [away_store_id] [int] NOT NULL,
   [radius_thresh] [smallint] NOT NULL,
   [travel_time] [decimal](19,5) NOT NULL,
   [created_at] datetime NOT NULL,
   [updated_at] datetime NOT NULL
   CONSTRAINT [PK_competitive_stores] PRIMARY KEY CLUSTERED 
	(	[id] ASC
	) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO







