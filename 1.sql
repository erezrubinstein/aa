/*
Developer notes:
- this file was auto generated early in the geoprocessing dev cycle. But it's not auto-managed now.
- the build parses this file on GO\n, and executes each chunk as a separate SQL batch. So be aware of that.
- order of objects doesn't really matter. Append new objects to the end, or in the middle if that makes more sense.
- keep on rocking in the free world.
 */

/****** Object:  Table [dbo].[thresholds]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[thresholds](
	[threshold_id] [tinyint] NOT NULL,
	[measurement_type] [varchar](50) NOT NULL,
	[measurement] [decimal](9, 5) NOT NULL,
  [label] [varchar](50) NOT NULL,
 CONSTRAINT [PK_thresholds] PRIMARY KEY CLUSTERED 
(
	[threshold_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[source_file_records]    Script Date: 12/20/2012 4:59:50 PM ******/
SET ANSI_NULLS ON


GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[source_file_records](
	[source_file_record_id] [int] IDENTITY(1,1) NOT NULL,
	[source_file_id] [int] NOT NULL,
	[row_number] [int] NOT NULL,
	[record] [nvarchar](max) NOT NULL,
	[loader_record_id] [varchar](100) NULL,
	[street_number] [nvarchar](25) NULL,
	[street] [nvarchar](255) NULL,
	[city] [nvarchar](255) NULL,
	[state] [nvarchar](255) NULL,
	[zip] [nvarchar](255) NULL,
	[phone] [nvarchar](255) NULL,
	[country_id] [int] NULL,
	[latitude] [decimal](9, 6) NULL,
	[longitude] [decimal](9, 6) NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
	[suite] [nvarchar](100) NULL,
	[note] [nvarchar](255) NULL,
	[company_generated_store_number] [nvarchar](255) NULL,
	[store_format] [nvarchar](255) NULL,
	[opened_date] [datetime] NULL,
	[source_date] [datetime] NULL,
	[shopping_center_name] [nvarchar](255) NULL,
 CONSTRAINT [PK_source_file_records] PRIMARY KEY CLUSTERED
(
	[source_file_record_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
CREATE NONCLUSTERED INDEX [IX__source_file_id] ON [dbo].[source_file_records]
(
  [source_file_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO



/****** Object:  Table [dbo].[monopoly_types]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[monopoly_types](
	[monopoly_type_id] [tinyint] NOT NULL,
	[name] [varchar](100) NOT NULL,
 CONSTRAINT [PK_monopoly_types] PRIMARY KEY CLUSTERED 
(
	[monopoly_type_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[source_files]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[source_files](
	[source_file_id] [int] IDENTITY(1,1) NOT NULL,
	[full_path] [nvarchar](max) NOT NULL,
	[file_created_date] [datetime] NOT NULL,
	[file_modified_date] [datetime] NOT NULL,
	[file_size_in_bytes] [int] NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_source_files] PRIMARY KEY CLUSTERED 
(
	[source_file_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[sectors]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[sectors](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](255) NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_sectors] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


/****** Object:  Table [dbo].[monopolies_postgis]    Script Date: 12/13/2012 17:48:26 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[monopolies_postgis](
	[monopoly_id] [int] IDENTITY(1,1) NOT NULL,
	[store_id] [int] NOT NULL,
	[monopoly_type_id] [tinyint] NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[start_date] [date] NULL,
	[end_date] [date] NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_monopolies_postgis] PRIMARY KEY CLUSTERED
(
	[monopoly_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO




/****** Object:  Table [dbo].[demographic_segments]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[demographic_segments](
	[demographic_segment_id] [int] IDENTITY(1,1) NOT NULL,
	[minimum_age] [int] NULL,
	[maximum_age] [int] NULL,
	[gender] [nvarchar](255) NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_demographic_segments] PRIMARY KEY CLUSTERED 
(
	[demographic_segment_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[industries]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[industries](
	[industry_id] [int] IDENTITY(1,1) NOT NULL,
	[naics_code] [varchar](6) NOT NULL,
	[name] [nvarchar](255) NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_industries] PRIMARY KEY CLUSTERED 
(
	[industry_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[entity_types]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[entity_types](
	[entity_type_id] [smallint] NOT NULL,
	[name] [varchar](250) NOT NULL,
 CONSTRAINT [PK_entity_types] PRIMARY KEY CLUSTERED 
(
	[entity_type_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[duration_types]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[duration_types](
	[duration_type_id] [tinyint] NOT NULL,
	[name] [varchar](100) NOT NULL,
 CONSTRAINT [PK_duration_types] PRIMARY KEY CLUSTERED 
(
	[duration_type_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[data_items]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[data_items](
	[data_item_id] [int] IDENTITY(1,1) NOT NULL,
	[name] [varchar](100) NOT NULL,
	[description] [varchar](max) NOT NULL,
	[type] [varchar](10) NOT NULL,
	[source] [varchar](50) NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_data_items] PRIMARY KEY CLUSTERED 
(
	[data_item_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[countries]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[countries](
	[country_id] [int] IDENTITY(1,1) NOT NULL,
	[code] [nvarchar](255) NULL,
	[country_name] [nvarchar](255) NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_countries] PRIMARY KEY CLUSTERED 
(
	[country_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

create table governing_districts (
	governing_district_id smallint not null constraint PK_governing_districts primary key clustered,
	governing_district nvarchar(255) not null constraint UK_governing_districts_governing_district unique nonclustered,
	name nvarchar(255) not null,
	country_id int not null,
  region nvarchar(100) not null,
  division nvarchar(100) not null,
	created_at datetime not null,
	updated_at datetime not null
);

alter table governing_districts add constraint governing_districts_created_at default (getutcdate()) for created_at;
alter table governing_districts add constraint governing_districts_updated_at default (getutcdate()) for updated_at;

create nonclustered index IX_governing_districts_country_id on governing_districts (country_id);
CREATE NONCLUSTERED INDEX [IX__governing_distrincts__governing_district] ON [dbo].[governing_districts]
(
	[governing_district] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


alter table governing_districts
add constraint FK_governing_districts_countries
foreign key (country_id)
references countries (country_id);

GO

/****** Object:  Table [dbo].[companies]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[companies](
	[company_id] [int] IDENTITY(1,1) NOT NULL,
	[ticker] [nvarchar](255) NULL,
	[name] [nvarchar](255) NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_companies] PRIMARY KEY CLUSTERED 
(
	[company_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[change_types]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[change_types](
	[change_type_id] [tinyint] NOT NULL,
	[name] [varchar](50) NOT NULL,
 CONSTRAINT [PK_change_types] PRIMARY KEY CLUSTERED 
(
	[change_type_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
CREATE NONCLUSTERED INDEX [IX_stores_change_log_change_type_id] ON [dbo].[change_types] 
(
	[change_type_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[addresses_change_log]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[addresses_history](
	[addresses_history_id] [int] IDENTITY(1,1) NOT NULL,
	[address_id] [int] NULL,
	[street_number] [int] NULL,
	[street] [nvarchar](255) NULL,
	[municipality] [nvarchar](255) NULL,
	[governing_district] [nvarchar](255) NULL,
	[postal_area] [nvarchar](255) NULL,
	[country_id] [int] NULL,
	[fixed] [datetime] NULL,
	[latitude] [float] NOT NULL,
	[longitude] [float] NOT NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_address_history] PRIMARY KEY CLUSTERED 
(
	[addresses_history_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[addresses]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[addresses](
	[address_id] [int] IDENTITY(1,1) NOT NULL,
	[street_number] [nvarchar](25) NULL,
	[street] [nvarchar](255) NULL,
	[municipality] [nvarchar](255) NULL,
	[governing_district] [nvarchar](255) NULL,
	[postal_area] [nvarchar](255) NULL,
	[country_id] [int] NULL,
	[latitude] [decimal](9, 6) NULL,
	[longitude] [decimal](9, 6) NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
	[suite] [nvarchar](100) NULL,
	[shopping_center_name] [nvarchar](255) NULL,
  [unique_store_identifier] [nvarchar](255) NULL,
	[min_source_date] [datetime] NULL,
	[max_source_date] [datetime] NULL,
 CONSTRAINT [PK_addresses] PRIMARY KEY CLUSTERED 
(
	[address_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_latitude_longitude] ON [dbo].[addresses]
(
	[latitude] ASC,
	[longitude] ASC
) include ( address_id,
    street_number,
    street,
    municipality,
    governing_district,
    postal_area,
    suite,
    max_source_date
) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_longitude_latitude] ON [dbo].[addresses] 
(
	[longitude] ASC,
	[latitude] ASC
) include ( address_id,
    street_number,
    street,
    municipality,
    governing_district,
    postal_area,
    suite,
    max_source_date
) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[data_check_types]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[data_check_types](
	[data_check_type_id] [smallint] NOT NULL,
	[name] [varchar](250) NOT NULL,
	[entity_type_id] [smallint] NOT NULL,
	[sql] [varchar](max) NULL,
	[severity_level] [tinyint] NOT NULL,
	[fail_threshold] [int] NOT NULL,
 CONSTRAINT [PK_data_check_types] PRIMARY KEY CLUSTERED 
(
	[data_check_type_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[companies_target_demographic_segments]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[companies_target_demographic_segments](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[company_id] [int] NULL,
	[demographic_segment_id] [int] NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_companies_target_demographic_segments] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[companies_sectors]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[companies_sectors](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[sector_id] [int] NULL,
	[company_id] [int] NULL,
	[primary] [bit] NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
	[assumed_start_date] [datetime] NULL,
	[assumed_end_date] [datetime] NULL,
 CONSTRAINT [PK_companies_sectors] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[competitive_companies]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[competitive_companies](
	[competitive_company_id] [int] IDENTITY(1,1) NOT NULL,
	[home_company_id] [int] NULL,
	[away_company_id] [int] NULL,
	[competition_strength] [float] NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
	[assumed_start_date] [datetime] NULL,
	[assumed_end_date] [datetime] NULL,
 CONSTRAINT [PK_competitive_companies] PRIMARY KEY CLUSTERED 
(
	[competitive_company_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_competitive_away_company_id] ON [dbo].[competitive_companies] 
(
	[away_company_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_competitive_home_company_id] ON [dbo].[competitive_companies] 
(
	[home_company_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[periods]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[periods](
	[period_id] [int] IDENTITY(1,1) NOT NULL,
	[duration_type_id] [tinyint] NOT NULL,
	[period_start_date] [datetime] NOT NULL,
	[period_end_date] [datetime] NOT NULL,
 CONSTRAINT [PK_periods] PRIMARY KEY CLUSTERED 
(
	[period_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY],
 CONSTRAINT [UK_periods] UNIQUE NONCLUSTERED 
(
	[period_start_date] ASC,
	[period_end_date] ASC,
	[duration_type_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

/****** Object:  Table [dbo].[competitive_stores_postgis]    Script Date: 12/12/2012 12:55:13 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[competitive_stores_postgis](
	[competitive_store_id] [int] IDENTITY(1,1) NOT NULL,
	[competitive_company_id] [int] NOT NULL,
	[home_store_id] [int] NOT NULL,
	[away_store_id] [int] NOT NULL,
	[travel_time] [decimal](19, 5) NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[start_date] [date] NULL,
	[end_date] [date] NULL,
 CONSTRAINT [PK_competitive_stores_postgis] PRIMARY KEY CLUSTERED
(
	[competitive_store_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

/****** Object:  Table [dbo].[stores]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[stores](
	[store_id] [int] IDENTITY(1,1) NOT NULL,
	[company_id] [int] NULL,
	[address_id] [int] NOT NULL,
	[phone_number] [nvarchar](255) NULL,
	[store_format] [nvarchar](255) NULL,
	[company_generated_store_number] [nvarchar](255) NULL,
	[note] [nvarchar](1000) NULL,
	[core_store_id] [nvarchar](50) NULL,
	[opened_date] [datetime] NULL,
	[closed_date] [datetime] NULL,
	[assumed_opened_date] [datetime] NULL,
	[assumed_closed_date] [datetime] NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_stores] PRIMARY KEY CLUSTERED 
(
	[store_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_stores_address_id] ON [dbo].[stores] 
(
	[address_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_stores_company_id] ON [dbo].[stores] 
(
	[company_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX__stores__assumed_closed_date] ON [dbo].[stores]
(
	[assumed_closed_date] ASC
)
INCLUDE ( [store_id],
[company_id]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX__stores__assumed_opened_date] ON [dbo].[stores]
(
	[assumed_opened_date] ASC
)
INCLUDE ( [store_id],
[company_id]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX__stores__assumed_opened_date__assumed_closed_date] ON [dbo].[stores]
(
  [assumed_opened_date] ASC,
  [assumed_closed_date] ASC
)
INCLUDE ( [store_id],
          [company_id]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON, FILLFACTOR = 80) ON [PRIMARY]
GO



/****** Object:  Table [dbo].[company_analytics]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[company_analytics](
	[company_analytic_id] [int] IDENTITY(1,1) NOT NULL,
	[company_id] [int] NOT NULL,
	[period_id] [int] NOT NULL,
	[data_item_id] [int] NOT NULL,
	[value] [decimal](19, 9) NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_company_analytics] PRIMARY KEY CLUSTERED 
(
	[company_analytic_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_company_analytics_data_item_id] ON [dbo].[company_analytics] 
(
	[data_item_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_company_analytics_period_id] ON [dbo].[company_analytics] 
(
	[period_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE UNIQUE NONCLUSTERED INDEX [UX_company_analytics] ON [dbo].[company_analytics] 
(
	[company_id] ASC,
	[period_id] ASC,
	[data_item_id] ASC
)
INCLUDE ( [value]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[data_checks]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[data_checks](
	[data_check_id] [int] IDENTITY(1,1) NOT NULL,
	[data_check_type_id] [smallint] NOT NULL,
	[check_done] [datetime] NOT NULL,
	[bad_data_rows] [int] NOT NULL,
 CONSTRAINT [PK_data_checks] PRIMARY KEY CLUSTERED 
(
	[data_check_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[data_check_values]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[data_check_values](
	[data_check_value_id] [int] IDENTITY(1,1) NOT NULL,
	[data_check_id] [int] NOT NULL,
	[value_type] [varchar](250) NOT NULL,
	[expected_value] [varchar](250) NOT NULL,
	[actual_value] [varchar](250) NOT NULL,
	[entity_id] [int] NOT NULL,
 CONSTRAINT [PK_data_check_values] PRIMARY KEY CLUSTERED 
(
	[data_check_value_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[stores_change_log]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[stores_change_log](
	[stores_change_log_id] [int] IDENTITY(1,1) NOT NULL,
	[store_id] [int] NOT NULL,
	[log_date] [datetime] NOT NULL,
	[change_type_id] [tinyint] NOT NULL,
	[comment] [varchar](max) NULL,
	[source_file_id] [int] NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_stores_change_log] PRIMARY KEY CLUSTERED 
(
	[stores_change_log_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
CREATE NONCLUSTERED INDEX [IX_stores_change_log_store_id] ON [dbo].[stores_change_log] 
(
	[store_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO


CREATE TABLE [dbo].[addresses_change_log](
	[addresses_change_log_id] [int] IDENTITY(1,1) NOT NULL,
	[address_id] [int] NOT NULL,
	[log_date] [datetime] NOT NULL,
	[change_type_id] [tinyint] NOT NULL,
	[comment] [varchar](max) NULL,
	[source_file_id] [int] NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_addresses_change_log] PRIMARY KEY CLUSTERED
(
	[addresses_change_log_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
CREATE NONCLUSTERED INDEX [IX_addresses_change_log_store_id] ON [dbo].[addresses_change_log]
(
	[address_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO

/****** Object:  Table [dbo].[trade_areas]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[trade_areas](
	[trade_area_id] [int] IDENTITY(1,1) NOT NULL,
	[store_id] [int] NULL,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
	[threshold_id] [tinyint] NOT NULL,
	[project_period] [varchar](25) NULL,
 CONSTRAINT [PK_trade_areas] PRIMARY KEY CLUSTERED 
(
	[trade_area_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY],
 CONSTRAINT [UK_trade_areas] UNIQUE NONCLUSTERED 
(
	[store_id] ASC,
	[threshold_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[trade_area_shapes]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[trade_area_shapes](
	[trade_area_shape_id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[period_id] [int] NOT NULL,
	[wkt_shape] [varchar](max) NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_trade_area_shapes] PRIMARY KEY CLUSTERED 
(
	[trade_area_shape_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
CREATE NONCLUSTERED INDEX [IX_trade_area_shapes_period_id] ON [dbo].[trade_area_shapes] 
(
	[period_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_trade_area_shapes_trade_area_id] ON [dbo].[trade_area_shapes] 
(
	[trade_area_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[trade_area_analytics]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[trade_area_analytics](
	[trade_area_analytic_id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[period_id] [int] NOT NULL,
	[data_item_id] [int] NOT NULL,
	[value] [decimal](25, 4) NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_trade_area_analytics] PRIMARY KEY CLUSTERED 
(
	[trade_area_analytic_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_trade_area_analytics_data_item_id] ON [dbo].[trade_area_analytics] 
(
	[data_item_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_trade_area_analytics_period_id] ON [dbo].[trade_area_analytics] 
(
	[period_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE UNIQUE NONCLUSTERED INDEX [UX_trade_area_analytics] ON [dbo].[trade_area_analytics] 
(
	[trade_area_id] ASC,
	[period_id] ASC,
	[data_item_id] ASC
)
INCLUDE ( [value]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[monopolies]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[monopolies](
	[monopoly_id] [int] IDENTITY(1,1) NOT NULL,
	[store_id] [int] NOT NULL,
	[monopoly_type_id] [tinyint] NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[start_date] [date] NULL,
	[end_date] [date] NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
 CONSTRAINT [PK_monopolies] PRIMARY KEY CLUSTERED
(
	[monopoly_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[demographic_strvalues]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[demographic_strvalues](
	[demographic_strvalue_id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[data_item_id] [int] NOT NULL,
	[value] [nvarchar](400) NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
	[segment_id] [int] NULL,
	[period_id] [int] NOT NULL,
	[target_period_id] [int] NULL,
  [template_name] varchar(100) NOT NULL,
 CONSTRAINT [PK_demographic_strvalues] PRIMARY KEY CLUSTERED 
(
	[demographic_strvalue_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY],
 CONSTRAINT [UK_demographic_strvalues] UNIQUE NONCLUSTERED 
(
	[trade_area_id] ASC,
	[period_id] ASC,
	[data_item_id] ASC,
  [template_name] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
CREATE NONCLUSTERED INDEX [IX_demographic_strvalues_data_item_id] ON [dbo].[demographic_strvalues] 
(
	[data_item_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_strvalues_period_id] ON [dbo].[demographic_strvalues] 
(
	[period_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_strvalues_target_period_id] ON [dbo].[demographic_strvalues] 
(
	[target_period_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_strvalues_trade_area_id_demographic_type_id] ON [dbo].[demographic_strvalues] 
(
	[trade_area_id] ASC,
	[data_item_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_strvalues_trade_area_id_demographic_type_id_template_name] ON [dbo].[demographic_strvalues]
(
  [trade_area_id] ASC,
  [data_item_id] ASC,
  [template_name] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[demographic_numvalues]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[demographic_numvalues](
	[demographic_numvalue_id] [int] IDENTITY(1,1) NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[data_item_id] [int] NOT NULL,
	[value] [decimal](21, 8) NOT NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
	[segment_id] [int] NULL,
	[period_id] [int] NOT NULL,
	[target_period_id] [int] NULL,
  [template_name] varchar(100) NOT NULL,
 CONSTRAINT [PK_demographic_numvalues] PRIMARY KEY CLUSTERED 
(
	[demographic_numvalue_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY],
 CONSTRAINT [UK_demographic_numvalues] UNIQUE NONCLUSTERED 
(
	[trade_area_id] ASC,
	[period_id] ASC,
	[data_item_id] ASC,
  [template_name] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_numvalues_data_item_id] ON [dbo].[demographic_numvalues] 
(
	[data_item_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_numvalues_period_id] ON [dbo].[demographic_numvalues] 
(
	[period_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_numvalues_period_include] ON [dbo].[demographic_numvalues] 
(
	[period_id] ASC
)
INCLUDE ( [trade_area_id],
[data_item_id],
[value]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_numvalues_target_period_id] ON [dbo].[demographic_numvalues] 
(
	[target_period_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_numvalues_trade_area_id_demographic_type_id] ON [dbo].[demographic_numvalues] 
(
	[trade_area_id] ASC,
	[data_item_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_numvalues_trade_area_id_demographic_type_id_template_name] ON [dbo].[demographic_numvalues]
(
  [trade_area_id] ASC,
  [data_item_id] ASC,
  [template_name] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_demographic_numvalues_trade_area_id] ON [dbo].[demographic_numvalues]
(
	[trade_area_id] ASC
)
INCLUDE ( [data_item_id],
[value],
[period_id],
[target_period_id]) WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO

/****** Object:  Table [dbo].[competitive_stores]    Script Date: 11/26/2012 13:22:13 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[competitive_stores](
	[competitive_store_id] [int] IDENTITY(1,1) NOT NULL,
	[competitive_company_id] [int] NOT NULL,
	[home_store_id] [int] NOT NULL,
	[away_store_id] [int] NOT NULL,
	[travel_time] [decimal](19, 5) NULL,
	[created_at] [datetime] NOT NULL,
	[updated_at] [datetime] NOT NULL,
	[trade_area_id] [int] NOT NULL,
	[start_date] [date] NULL,
	[end_date] [date] NULL,
 CONSTRAINT [PK_competitive_stores] PRIMARY KEY CLUSTERED 
(
	[competitive_store_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX__competitive_stores__home_store__away_store__trade_area] ON [dbo].[competitive_stores]
(
	[home_store_id] ASC,
	[away_store_id] ASC,
	[trade_area_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX__competitve_stores__trade_area_id] ON [dbo].[competitive_stores]
(
	[trade_area_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX__competitive_stores__home_store__trade_area__strt_date__end_date] ON [dbo].[competitive_stores]
(
  [home_store_id] ASC,
  [trade_area_id] ASC,
  [start_date] ASC,
  [end_date] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON, FILLFACTOR = 80) ON [PRIMARY]
GO


/****** Object:  Table [dbo].[trade_area_overlaps]    Script Date: 12/3/2012 18:41:00 ******/

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[trade_area_overlaps]
(
[trade_area_overlap_id] [int] IDENTITY(1, 1) NOT NULL,
[home_trade_area_id] [int] NOT NULL,
[away_trade_area_id] [int] NOT NULL,
[overlap_area] [bigint] NOT NULL,
[created_at] [datetime] NOT NULL,
[updated_at] [datetime] NOT NULL
CONSTRAINT [PK_trade_area_overlaps] PRIMARY KEY CLUSTERED
(
[trade_area_overlap_id] ASC
)
WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[store_zip_proximities]    Script Date: 12/13/2012 17:48:26 ******/
CREATE TABLE [dbo].[store_zip_proximities](
	[store_zip_proximity_id] int NOT NULL identity(1,1),
	[store_id] [int] not null,
	[zip_code] char(5) not null,
	[threshold_id] tinyint not null,
	[proximity] decimal(19,5) not null,
	[created_at] [datetime] NULL,
	[updated_at] [datetime] NULL,
 CONSTRAINT [PK_store_zip_proximities] PRIMARY KEY CLUSTERED
(
	[store_zip_proximity_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

create table zip_codes(
        zip_code char(5) not null constraint PK_zip_codes primary key clustered,
        POP10 int not null,
        HU10 int not null,
        ALAND bigint not null,
        AWATER bigint not null,
        ALAND_SQLMI decimal(19,9) not null,
        AWATER_SQLMI decimal(19,9) not null,
        INTPTLAT decimal(9,6) not null,
        INTPTLONG decimal(9,6) not null
)
GO

create nonclustered index IX_long_lat on zip_codes (INTPTLONG, INTPTLAT);
GO

create table zip_establishment_details (
        zip_code char(5) not null,
        NAICS varchar(10) not null,
        EST int not null,
        N1_4 int not null,
        N5_9 int not null,
        N10_19 int not null,
        N20_49 int not null,
        N50_99 int not null,
        N100_249 int not null,
        N250_499 int not null,
        N500_999 int not null,
        N1000 int not null
)
GO

create nonclustered index IX_NAICS on zip_establishment_details (NAICS);
GO

/* Table populated with a whitelist of addresses corresponding to legitimate low-population trade areas */
create table trade_area_whitelist (
        latitude decimal(9, 6) NULL,
	    longitude decimal(9, 6) NULL,
	    threshold_measurement_type varchar(50) NOT NULL,
    	threshold_measurement decimal(9, 5) NOT NULL,
    	whitelist_type varchar(100) NOT NULL
)
GO

create nonclustered index IX_TRADE_AREA_WHITELIST_COORDS on trade_area_whitelist (latitude, longitude);
GO

/****** Object:  Default [DF_address_history_fixed]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[addresses_history] ADD  CONSTRAINT [DF_address_history_fixed] DEFAULT (NULL) FOR [fixed]
GO
/****** Object:  Default [DF_company_analytics_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[company_analytics] ADD  CONSTRAINT [DF_company_analytics_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_company_analytics_updated_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[company_analytics] ADD  CONSTRAINT [DF_company_analytics_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO
/****** Object:  Default [DF_data_items_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[data_items] ADD  CONSTRAINT [DF_data_items_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_data_items_updated_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[data_items] ADD  CONSTRAINT [DF_data_items_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO
/****** Object:  Default [DF_source_files_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[source_files] ADD  CONSTRAINT [DF_source_files_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_source_files_updated_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[source_files] ADD  CONSTRAINT [DF_source_files_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO
/****** Object:  Default [DF_stores_change_log_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[stores_change_log] ADD  CONSTRAINT [DF_stores_change_log_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_stores_change_log_updated_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[stores_change_log] ADD  CONSTRAINT [DF_stores_change_log_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO
/****** Object:  Default [DF_trade_area_analytics_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_analytics] ADD  CONSTRAINT [DF_trade_area_analytics_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_trade_area_analytics_updated_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_analytics] ADD  CONSTRAINT [DF_trade_area_analytics_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO
/****** Object:  Default [DF_trade_area_shapes_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_shapes] ADD  CONSTRAINT [DF_trade_area_shapes_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_trade_area_shapes_updated_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_shapes] ADD  CONSTRAINT [DF_trade_area_shapes_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO
/****** Object:  Default [DF_demographic_segments_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_segments] ADD  CONSTRAINT [DF_demographic_segments_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_demographic_segments_updated_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_segments] ADD  CONSTRAINT [DF_demographic_segments_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO
/****** Object:  Default [DF_industries_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[industries] ADD  CONSTRAINT [DF_industries_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_industries_updated_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[industries] ADD  CONSTRAINT [DF_industries_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO
/****** Object:  Default [DF_countries_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[countries] ADD  CONSTRAINT [DF_countries_created_at]  DEFAULT (getutcdate()) FOR [created_at]
GO
/****** Object:  Default [DF_countries_created_at]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[countries] ADD  CONSTRAINT [DF_countries_updated_at]  DEFAULT (getutcdate()) FOR [updated_at]
GO

/****** Object:  Table [dbo].[FK_trade_area_overlaps_home_trade_area_id]    Script Date: 12/3/2012 18:41:00 ******/

ALTER TABLE [dbo].[trade_area_overlaps] WITH CHECK ADD CONSTRAINT [FK_trade_area_overlaps_home_trade_area_id] FOREIGN KEY ([home_trade_area_id])
REFERENCES [dbo].[trade_areas]([trade_area_id])
GO
ALTER TABLE [dbo].[trade_area_overlaps] CHECK CONSTRAINT [FK_trade_area_overlaps_home_trade_area_id]

/****** Object:  Table [dbo].[FK_trade_area_overlaps_away_trade_area_id]    Script Date: 12/3/2012 18:41:00 ******/

ALTER TABLE [dbo].[trade_area_overlaps] WITH CHECK ADD CONSTRAINT [FK_trade_area_overlaps_away_trade_area_id] FOREIGN KEY ([away_trade_area_id])
REFERENCES [dbo].[trade_areas]([trade_area_id])
GO
ALTER TABLE [dbo].[trade_area_overlaps] CHECK CONSTRAINT [FK_trade_area_overlaps_away_trade_area_id]

/****** Object:  ForeignKey [FK_addresses_countries]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[addresses]  WITH CHECK ADD  CONSTRAINT [FK_addresses_countries] FOREIGN KEY([country_id])
REFERENCES [dbo].[countries] ([country_id])
GO
ALTER TABLE [dbo].[addresses] CHECK CONSTRAINT [FK_addresses_countries]
GO

ALTER TABLE [dbo].[addresses]  WITH CHECK ADD  CONSTRAINT [FK_addresses_governing_districts] FOREIGN KEY([governing_district])
REFERENCES [dbo].[governing_districts] ([governing_district])
GO
ALTER TABLE [dbo].[addresses] CHECK CONSTRAINT [FK_addresses_governing_districts]
GO

/****** Object:  ForeignKey [FK_companies_sectors_companies]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[companies_sectors]  WITH CHECK ADD  CONSTRAINT [FK_companies_sectors_companies] FOREIGN KEY([company_id])
REFERENCES [dbo].[companies] ([company_id])
GO
ALTER TABLE [dbo].[companies_sectors] CHECK CONSTRAINT [FK_companies_sectors_companies]
GO
/****** Object:  ForeignKey [FK_companies_sectors_sectors]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[companies_sectors]  WITH CHECK ADD  CONSTRAINT [FK_companies_sectors_sectors] FOREIGN KEY([sector_id])
REFERENCES [dbo].[sectors] ([id])
GO
ALTER TABLE [dbo].[companies_sectors] CHECK CONSTRAINT [FK_companies_sectors_sectors]
GO
/****** Object:  ForeignKey [FK_companies_target_demographic_segments_companies]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[companies_target_demographic_segments]  WITH CHECK ADD  CONSTRAINT [FK_companies_target_demographic_segments_companies] FOREIGN KEY([company_id])
REFERENCES [dbo].[companies] ([company_id])
GO
ALTER TABLE [dbo].[companies_target_demographic_segments] CHECK CONSTRAINT [FK_companies_target_demographic_segments_companies]
GO
/****** Object:  ForeignKey [FK_companies_target_demographic_segments_demographic_segments]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[companies_target_demographic_segments]  WITH CHECK ADD  CONSTRAINT [FK_companies_target_demographic_segments_demographic_segments] FOREIGN KEY([demographic_segment_id])
REFERENCES [dbo].[demographic_segments] ([demographic_segment_id])
GO
ALTER TABLE [dbo].[companies_target_demographic_segments] CHECK CONSTRAINT [FK_companies_target_demographic_segments_demographic_segments]
GO
/****** Object:  ForeignKey [FK_company_analytics_companies]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[company_analytics]  WITH CHECK ADD  CONSTRAINT [FK_company_analytics_companies] FOREIGN KEY([company_id])
REFERENCES [dbo].[companies] ([company_id])
GO
ALTER TABLE [dbo].[company_analytics] CHECK CONSTRAINT [FK_company_analytics_companies]
GO
/****** Object:  ForeignKey [FK_company_analytics_data_items]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[company_analytics]  WITH CHECK ADD  CONSTRAINT [FK_company_analytics_data_items] FOREIGN KEY([data_item_id])
REFERENCES [dbo].[data_items] ([data_item_id])
GO
ALTER TABLE [dbo].[company_analytics] CHECK CONSTRAINT [FK_company_analytics_data_items]
GO
/****** Object:  ForeignKey [FK_company_analytics_periods]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[company_analytics]  WITH CHECK ADD  CONSTRAINT [FK_company_analytics_periods] FOREIGN KEY([period_id])
REFERENCES [dbo].[periods] ([period_id])
GO
ALTER TABLE [dbo].[company_analytics] CHECK CONSTRAINT [FK_company_analytics_periods]
GO
/****** Object:  ForeignKey [FK_competitive_companies_away_company_id]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[competitive_companies]  WITH CHECK ADD  CONSTRAINT [FK_competitive_companies_away_company_id] FOREIGN KEY([away_company_id])
REFERENCES [dbo].[companies] ([company_id])
GO
ALTER TABLE [dbo].[competitive_companies] CHECK CONSTRAINT [FK_competitive_companies_away_company_id]
GO
/****** Object:  ForeignKey [FK_competitive_companies_home_company_id]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[competitive_companies]  WITH CHECK ADD  CONSTRAINT [FK_competitive_companies_home_company_id] FOREIGN KEY([home_company_id])
REFERENCES [dbo].[companies] ([company_id])
GO
ALTER TABLE [dbo].[competitive_companies] CHECK CONSTRAINT [FK_competitive_companies_home_company_id]
GO
/****** Object:  ForeignKey [FK_competitive_stores]  ******/
ALTER TABLE [dbo].[competitive_stores]  WITH CHECK ADD  CONSTRAINT [FK_competitive_stores_competitive_company_id] FOREIGN KEY([competitive_company_id])
REFERENCES [dbo].[competitive_companies] ([competitive_company_id])
GO
ALTER TABLE [dbo].[competitive_stores] CHECK CONSTRAINT [FK_competitive_stores_competitive_company_id]
GO
/****** Object:  ForeignKey [FK_competitive_stores]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[competitive_stores]  WITH CHECK ADD  CONSTRAINT [FK_competitive_stores] FOREIGN KEY([trade_area_id])
REFERENCES [dbo].[trade_areas] ([trade_area_id])
GO
ALTER TABLE [dbo].[competitive_stores] CHECK CONSTRAINT [FK_competitive_stores]
GO
/****** Object:  ForeignKey [FK_competitive_stores_stores_away_store_id]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[competitive_stores]  WITH CHECK ADD  CONSTRAINT [FK_competitive_stores_stores_away_store_id] FOREIGN KEY([away_store_id])
REFERENCES [dbo].[stores] ([store_id])
GO
ALTER TABLE [dbo].[competitive_stores] CHECK CONSTRAINT [FK_competitive_stores_stores_away_store_id]
GO
/****** Object:  ForeignKey [FK_competitive_stores_stores_home_store_id]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[competitive_stores]  WITH CHECK ADD  CONSTRAINT [FK_competitive_stores_stores_home_store_id] FOREIGN KEY([home_store_id])
REFERENCES [dbo].[stores] ([store_id])
GO
ALTER TABLE [dbo].[competitive_stores] CHECK CONSTRAINT [FK_competitive_stores_stores_home_store_id]
GO
/****** Object:  ForeignKey [FK_data_check_types_entity_types]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[data_check_types]  WITH CHECK ADD  CONSTRAINT [FK_data_check_types_entity_types] FOREIGN KEY([entity_type_id])
REFERENCES [dbo].[entity_types] ([entity_type_id])
GO
ALTER TABLE [dbo].[data_check_types] CHECK CONSTRAINT [FK_data_check_types_entity_types]
GO
/****** Object:  ForeignKey [FK_data_check_values_data_checks]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[data_check_values]  WITH CHECK ADD  CONSTRAINT [FK_data_check_values_data_checks] FOREIGN KEY([data_check_id])
REFERENCES [dbo].[data_checks] ([data_check_id])
GO
ALTER TABLE [dbo].[data_check_values] CHECK CONSTRAINT [FK_data_check_values_data_checks]
GO
/****** Object:  ForeignKey [FK_data_checks_data_check_types]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[data_checks]  WITH CHECK ADD  CONSTRAINT [FK_data_checks_data_check_types] FOREIGN KEY([data_check_type_id])
REFERENCES [dbo].[data_check_types] ([data_check_type_id])
GO
ALTER TABLE [dbo].[data_checks] CHECK CONSTRAINT [FK_data_checks_data_check_types]
GO
/****** Object:  ForeignKey [FK_demographic_numvalues_data_items]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_numvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_numvalues_data_items] FOREIGN KEY([data_item_id])
REFERENCES [dbo].[data_items] ([data_item_id])
GO
ALTER TABLE [dbo].[demographic_numvalues] CHECK CONSTRAINT [FK_demographic_numvalues_data_items]
GO
/****** Object:  ForeignKey [FK_demographic_numvalues_demographic_segments]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_numvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_numvalues_demographic_segments] FOREIGN KEY([segment_id])
REFERENCES [dbo].[demographic_segments] ([demographic_segment_id])
GO
ALTER TABLE [dbo].[demographic_numvalues] CHECK CONSTRAINT [FK_demographic_numvalues_demographic_segments]
GO
/****** Object:  ForeignKey [FK_demographic_numvalues_periods]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_numvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_numvalues_periods] FOREIGN KEY([period_id])
REFERENCES [dbo].[periods] ([period_id])
GO
ALTER TABLE [dbo].[demographic_numvalues] CHECK CONSTRAINT [FK_demographic_numvalues_periods]
GO
/****** Object:  ForeignKey [FK_demographic_numvalues_target_periods]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_numvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_numvalues_target_periods] FOREIGN KEY([target_period_id])
REFERENCES [dbo].[periods] ([period_id])
GO
ALTER TABLE [dbo].[demographic_numvalues] CHECK CONSTRAINT [FK_demographic_numvalues_target_periods]
GO
/****** Object:  ForeignKey [FK_demographic_numvalues_trade_areas]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_numvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_numvalues_trade_areas] FOREIGN KEY([trade_area_id])
REFERENCES [dbo].[trade_areas] ([trade_area_id])
GO
ALTER TABLE [dbo].[demographic_numvalues] CHECK CONSTRAINT [FK_demographic_numvalues_trade_areas]
GO
/****** Object:  ForeignKey [FK_demographic_strvalues_data_items]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_strvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_strvalues_data_items] FOREIGN KEY([data_item_id])
REFERENCES [dbo].[data_items] ([data_item_id])
GO
ALTER TABLE [dbo].[demographic_strvalues] CHECK CONSTRAINT [FK_demographic_strvalues_data_items]
GO
/****** Object:  ForeignKey [FK_demographic_strvalues_demographic_segments]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_strvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_strvalues_demographic_segments] FOREIGN KEY([segment_id])
REFERENCES [dbo].[demographic_segments] ([demographic_segment_id])
GO
ALTER TABLE [dbo].[demographic_strvalues] CHECK CONSTRAINT [FK_demographic_strvalues_demographic_segments]
GO
/****** Object:  ForeignKey [FK_demographic_strvalues_periods]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_strvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_strvalues_periods] FOREIGN KEY([period_id])
REFERENCES [dbo].[periods] ([period_id])
GO
ALTER TABLE [dbo].[demographic_strvalues] CHECK CONSTRAINT [FK_demographic_strvalues_periods]
GO
/****** Object:  ForeignKey [FK_demographic_strvalues_target_periods]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_strvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_strvalues_target_periods] FOREIGN KEY([target_period_id])
REFERENCES [dbo].[periods] ([period_id])
GO
ALTER TABLE [dbo].[demographic_strvalues] CHECK CONSTRAINT [FK_demographic_strvalues_target_periods]
GO
/****** Object:  ForeignKey [FK_demographic_strvalues_trade_areas]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[demographic_strvalues]  WITH CHECK ADD  CONSTRAINT [FK_demographic_strvalues_trade_areas] FOREIGN KEY([trade_area_id])
REFERENCES [dbo].[trade_areas] ([trade_area_id])
GO
ALTER TABLE [dbo].[demographic_strvalues] CHECK CONSTRAINT [FK_demographic_strvalues_trade_areas]
GO
/****** Object:  ForeignKey [FK_monopolies_monopoly_type_id]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[monopolies]  WITH CHECK ADD  CONSTRAINT [FK_monopolies_monopoly_type_id] FOREIGN KEY([monopoly_type_id])
REFERENCES [dbo].[monopoly_types] ([monopoly_type_id])
GO
ALTER TABLE [dbo].[monopolies] CHECK CONSTRAINT [FK_monopolies_monopoly_type_id]
GO
/****** Object:  ForeignKey [FK_monopolies_stores]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[monopolies]  WITH CHECK ADD  CONSTRAINT [FK_monopolies_stores] FOREIGN KEY([store_id])
REFERENCES [dbo].[stores] ([store_id])
GO
ALTER TABLE [dbo].[monopolies] CHECK CONSTRAINT [FK_monopolies_stores]
GO
/****** Object:  ForeignKey [FK_monopolies_trade_areas]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[monopolies]  WITH CHECK ADD  CONSTRAINT [FK_monopolies_trade_areas] FOREIGN KEY([trade_area_id])
REFERENCES [dbo].[trade_areas] ([trade_area_id])
GO
ALTER TABLE [dbo].[monopolies] CHECK CONSTRAINT [FK_monopolies_trade_areas]
GO
/****** Object:  ForeignKey [FK_periods_duration_types]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[periods]  WITH CHECK ADD  CONSTRAINT [FK_periods_duration_types] FOREIGN KEY([duration_type_id])
REFERENCES [dbo].[duration_types] ([duration_type_id])
GO
ALTER TABLE [dbo].[periods] CHECK CONSTRAINT [FK_periods_duration_types]
GO
/****** Object:  ForeignKey [FK_stores_address]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[stores]  WITH CHECK ADD  CONSTRAINT [FK_stores_address] FOREIGN KEY([address_id])
REFERENCES [dbo].[addresses] ([address_id])
GO
ALTER TABLE [dbo].[stores] CHECK CONSTRAINT [FK_stores_address]
GO
/****** Object:  ForeignKey [FK_stores_companies]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[stores]  WITH CHECK ADD  CONSTRAINT [FK_stores_companies] FOREIGN KEY([company_id])
REFERENCES [dbo].[companies] ([company_id])
GO
ALTER TABLE [dbo].[stores] CHECK CONSTRAINT [FK_stores_companies]
GO
/****** Object:  ForeignKey [FK_stores_change_log_change_types]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[stores_change_log]  WITH CHECK ADD  CONSTRAINT [FK_stores_change_log_change_types] FOREIGN KEY([change_type_id])
REFERENCES [dbo].[change_types] ([change_type_id])
GO
ALTER TABLE [dbo].[stores_change_log] CHECK CONSTRAINT [FK_stores_change_log_change_types]
GO

ALTER TABLE [dbo].[addresses_change_log]  WITH CHECK ADD  CONSTRAINT [FK_addresses_change_log_change_types] FOREIGN KEY([change_type_id])
REFERENCES [dbo].[change_types] ([change_type_id])
GO
ALTER TABLE [dbo].[addresses_change_log] CHECK CONSTRAINT [FK_addresses_change_log_change_types]
GO

/****** Object:  ForeignKey [FK_stores_change_log_stores]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[stores_change_log]  WITH CHECK ADD  CONSTRAINT [FK_stores_change_log_stores] FOREIGN KEY([store_id])
REFERENCES [dbo].[stores] ([store_id])
GO
ALTER TABLE [dbo].[stores_change_log] CHECK CONSTRAINT [FK_stores_change_log_stores]
GO
/****** Object:  ForeignKey [FK_trade_area_analytics_data_items]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_analytics]  WITH CHECK ADD  CONSTRAINT [FK_trade_area_analytics_data_items] FOREIGN KEY([data_item_id])
REFERENCES [dbo].[data_items] ([data_item_id])
GO
ALTER TABLE [dbo].[trade_area_analytics] CHECK CONSTRAINT [FK_trade_area_analytics_data_items]
GO
/****** Object:  ForeignKey [FK_trade_area_analytics_periods]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_analytics]  WITH CHECK ADD  CONSTRAINT [FK_trade_area_analytics_periods] FOREIGN KEY([period_id])
REFERENCES [dbo].[periods] ([period_id])
GO
ALTER TABLE [dbo].[trade_area_analytics] CHECK CONSTRAINT [FK_trade_area_analytics_periods]
GO
/****** Object:  ForeignKey [FK_trade_area_analytics_trade_areas]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_analytics]  WITH CHECK ADD  CONSTRAINT [FK_trade_area_analytics_trade_areas] FOREIGN KEY([trade_area_id])
REFERENCES [dbo].[trade_areas] ([trade_area_id])
GO
ALTER TABLE [dbo].[trade_area_analytics] CHECK CONSTRAINT [FK_trade_area_analytics_trade_areas]
GO
/****** Object:  ForeignKey [FK_trade_area_shapes_periods]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_shapes]  WITH CHECK ADD  CONSTRAINT [FK_trade_area_shapes_periods] FOREIGN KEY([period_id])
REFERENCES [dbo].[periods] ([period_id])
GO
ALTER TABLE [dbo].[trade_area_shapes] CHECK CONSTRAINT [FK_trade_area_shapes_periods]
GO
/****** Object:  ForeignKey [FK_trade_area_shapes_trade_areas]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_area_shapes]  WITH CHECK ADD  CONSTRAINT [FK_trade_area_shapes_trade_areas] FOREIGN KEY([trade_area_id])
REFERENCES [dbo].[trade_areas] ([trade_area_id])
GO
ALTER TABLE [dbo].[trade_area_shapes] CHECK CONSTRAINT [FK_trade_area_shapes_trade_areas]
GO
/****** Object:  ForeignKey [FK_trade_areas_stores]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_areas]  WITH CHECK ADD  CONSTRAINT [FK_trade_areas_stores] FOREIGN KEY([store_id])
REFERENCES [dbo].[stores] ([store_id])
GO
ALTER TABLE [dbo].[trade_areas] CHECK CONSTRAINT [FK_trade_areas_stores]
GO
/****** Object:  ForeignKey [FK_trade_areas_thresholds]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[trade_areas]  WITH CHECK ADD  CONSTRAINT [FK_trade_areas_thresholds] FOREIGN KEY([threshold_id])
REFERENCES [dbo].[thresholds] ([threshold_id])
GO
ALTER TABLE [dbo].[trade_areas] CHECK CONSTRAINT [FK_trade_areas_thresholds]
GO
/****** Object:  ForeignKey [FK_monopolies_postgis_monopoly_type_id]    Script Date: 11/26/2012 13:22:13 ******/
ALTER TABLE [dbo].[monopolies_postgis]  WITH CHECK ADD  CONSTRAINT [FK_monopolies_postgis_monopoly_type_id] FOREIGN KEY([monopoly_type_id])
REFERENCES [dbo].[monopoly_types] ([monopoly_type_id])
GO

ALTER TABLE [dbo].[monopolies_postgis] CHECK CONSTRAINT [FK_monopolies_postgis_monopoly_type_id]
GO



ALTER TABLE [dbo].[store_zip_proximities]  WITH CHECK ADD  CONSTRAINT [FK_store_zip_proximities_stores] FOREIGN KEY([store_id])
REFERENCES [dbo].[stores] ([store_id])
GO

ALTER TABLE [dbo].[store_zip_proximities] CHECK CONSTRAINT [FK_store_zip_proximities_stores]
GO

ALTER TABLE [dbo].[store_zip_proximities]  WITH CHECK ADD  CONSTRAINT [FK_store_zip_proximities_threshold_id] FOREIGN KEY([threshold_id])
REFERENCES [dbo].[thresholds] ([threshold_id])
GO

ALTER TABLE [dbo].[store_zip_proximities] CHECK CONSTRAINT [FK_store_zip_proximities_threshold_id]
GO

ALTER TABLE [dbo].[store_zip_proximities] ADD  CONSTRAINT [UK_store_zip_proximities] UNIQUE NONCLUSTERED
(
	[store_id] ASC,
	[zip_code] ASC,
	[threshold_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO

CREATE INDEX IX_store_zip_proximities_zip_code on [dbo].[store_zip_proximities] (zip_code)
GO

ALTER TABLE [dbo].[store_zip_proximities]  WITH CHECK ADD  CONSTRAINT [FK_store_zip_proximities_zip_codes] FOREIGN KEY([zip_code])
REFERENCES [dbo].[zip_codes] ([zip_code])
GO

ALTER TABLE [dbo].[store_zip_proximities] CHECK CONSTRAINT [FK_store_zip_proximities_zip_codes]
GO



ALTER TABLE [dbo].[competitive_stores_postgis]  WITH CHECK ADD  CONSTRAINT [FK_competitive_stores_postgis] FOREIGN KEY([trade_area_id])
REFERENCES [dbo].[trade_areas] ([trade_area_id])
GO

ALTER TABLE [dbo].[competitive_stores_postgis] CHECK CONSTRAINT [FK_competitive_stores_postgis]
GO

ALTER TABLE [dbo].[competitive_stores_postgis]  WITH CHECK ADD  CONSTRAINT [FK_competitive_stores_stores_away_store_id_postgis] FOREIGN KEY([away_store_id])
REFERENCES [dbo].[stores] ([store_id])
GO

ALTER TABLE [dbo].[competitive_stores_postgis] CHECK CONSTRAINT [FK_competitive_stores_stores_away_store_id_postgis]
GO

ALTER TABLE [dbo].[competitive_stores_postgis]  WITH CHECK ADD  CONSTRAINT [FK_competitive_stores_postgis_competitive_company_id] FOREIGN KEY([competitive_company_id])
REFERENCES [dbo].[competitive_companies] ([competitive_company_id])
GO

ALTER TABLE [dbo].[competitive_stores_postgis] CHECK CONSTRAINT [FK_competitive_stores_postgis_competitive_company_id]
GO

/****** Object:  Index [IX__competitive_stores_postgis__home_store__away_store__trade_area]    Script Date: 12/12/2012 12:55:47 ******/
CREATE NONCLUSTERED INDEX [IX__competitive_stores_postgis__home_store__away_store__trade_area] ON [dbo].[competitive_stores_postgis]
(
	[home_store_id] ASC,
	[away_store_id] ASC,
	[trade_area_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO



ALTER TABLE [dbo].[addresses_change_log]  WITH CHECK ADD  CONSTRAINT [FK_addresses_change_log_source_files] FOREIGN KEY([source_file_id])
REFERENCES [dbo].[source_files] ([source_file_id])
GO
ALTER TABLE [dbo].[addresses_change_log] CHECK CONSTRAINT [FK_addresses_change_log_source_files]
GO

ALTER TABLE [dbo].[stores_change_log]  WITH CHECK ADD  CONSTRAINT [FK_stores_change_log_source_files] FOREIGN KEY([source_file_id])
REFERENCES [dbo].[source_files] ([source_file_id])
GO
ALTER TABLE [dbo].[stores_change_log] CHECK CONSTRAINT [FK_stores_change_log_source_files]
GO

ALTER TABLE [dbo].[source_file_records]  WITH CHECK ADD  CONSTRAINT [FK_source_file_records_source_file] FOREIGN KEY([source_file_id])
REFERENCES [dbo].[source_files] ([source_file_id])
GO

ALTER TABLE [dbo].[source_file_records] CHECK CONSTRAINT [FK_source_file_records_source_file]
GO


create table addresses_change_log_values (
	addresses_change_log_value_id int not null identity(1,1) constraint PK_addresses_change_log_values primary key clustered,
	addresses_change_log_id int not null,
	value_type varchar(250) not null,
	from_value nvarchar(255) null,
	to_value nvarchar(255) null,
	created_at datetime not null constraint DF_addresses_change_log_values_created_at default (getutcdate()),
	updated_at datetime not null constraint DF_addresses_change_log_values_updated_at default (getutcdate())
)

alter table addresses_change_log_values
add constraint FK_addresses_change_log_values
foreign key (addresses_change_log_id)
references addresses_change_log (addresses_change_log_id);

create nonclustered index IX_addresses_change_log_values_addresses_change_log_id on addresses_change_log_values (addresses_change_log_id);
GO

create nonclustered index IX_industries_naics_code on industries (naics_code);
GO


-------

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

SET ANSI_PADDING ON
GO

CREATE TABLE [dbo].[cbsa](
	[cbsa_id] [int] IDENTITY(1,1) NOT NULL,
	[geoid] [varchar](20) NOT NULL,
	[name] [nvarchar](200) NOT NULL,
	[points_json] [varchar](max) NOT NULL,
  [population] float NOT NULL,
  [pci] float NOT NULL,
  [agg_income] float NOT NULL,
  [max_degrees] float NOT NULL,
 CONSTRAINT [PK_cbsa] PRIMARY KEY CLUSTERED
(
	[cbsa_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

SET ANSI_PADDING OFF
GO


--------
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[cbsa_store_matches](
	[cbsa_store_match_id] [int] IDENTITY(1,1) NOT NULL,
	[cbsa_id] [int] NOT NULL,
	[store_id] [int] NOT NULL
 CONSTRAINT [PK_cbsa_store_matches] PRIMARY KEY CLUSTERED
(
	[cbsa_store_match_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

ALTER TABLE [dbo].[cbsa_store_matches]  WITH CHECK ADD  CONSTRAINT [FK__cbsa_store_matches__cbsa_id] FOREIGN KEY([cbsa_id])
REFERENCES [dbo].[cbsa] ([cbsa_id])
GO

ALTER TABLE [dbo].[cbsa_store_matches] CHECK CONSTRAINT [FK__cbsa_store_matches__cbsa_id]
GO

ALTER TABLE [dbo].[cbsa_store_matches]  WITH CHECK ADD  CONSTRAINT [FK_cbsa_store_matches_stores] FOREIGN KEY([store_id])
REFERENCES [dbo].[stores] ([store_id])
GO

ALTER TABLE [dbo].[cbsa_store_matches] CHECK CONSTRAINT [FK_cbsa_store_matches_stores]
GO


CREATE NONCLUSTERED INDEX [IX__cbsa_store_matches__store_id] ON [dbo].[cbsa_store_matches]
(
	[store_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IX__cbsa_store_matches__cbsa_id] ON [dbo].[cbsa_store_matches]
(
	[cbsa_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO

------


SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

SET ANSI_PADDING ON
GO

CREATE TABLE [dbo].[counties](
	[county_id] [int] IDENTITY(1,1) NOT NULL,
	[fips] [varchar](20) NOT NULL,
	[name] [nvarchar](200) NOT NULL,
	[points_json] [varchar](max) NOT NULL,
  [community_code] [int] NULL,
  [community_description] varchar(200) NULL,
  [state] varchar(10) NOT NULL,
  [population] float NOT NULL,
  [pci] float NOT NULL,
  [agg_income] float NOT NULL,
  [max_degrees] float NOT NULL,
 CONSTRAINT [PK_counties] PRIMARY KEY CLUSTERED
(
	[county_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

SET ANSI_PADDING OFF
GO

--------

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[county_store_matches](
	[county_store_match_id] [int] IDENTITY(1,1) NOT NULL,
	[county_id] [int] NOT NULL,
	[store_id] [int] NOT NULL,
 CONSTRAINT [PK_county_store_matches] PRIMARY KEY CLUSTERED
(
	[county_store_match_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

ALTER TABLE [dbo].[county_store_matches]  WITH CHECK ADD  CONSTRAINT [FK__county_store_matches__county_id] FOREIGN KEY([county_id])
REFERENCES [dbo].[counties] ([county_id])
GO

ALTER TABLE [dbo].[county_store_matches] CHECK CONSTRAINT [FK__county_store_matches__county_id]
GO

ALTER TABLE [dbo].[county_store_matches]  WITH CHECK ADD  CONSTRAINT [FK_county_store_matches_stores] FOREIGN KEY([store_id])
REFERENCES [dbo].[stores] ([store_id])
GO

ALTER TABLE [dbo].[county_store_matches] CHECK CONSTRAINT [FK_county_store_matches_stores]
GO

CREATE NONCLUSTERED INDEX [IX__county_store_matches__store_id] ON [dbo].[county_store_matches]
(
	[store_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IX__county_store_matches__county_id] ON [dbo].[county_store_matches]
(
	[county_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
GO






/* -------------------------------------- Report Tables --------------------------------------  */

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[ca_store_counts](
	[ca_store_count_id] [int] IDENTITY(1,1) NOT NULL,
	[company_id] [int] NOT NULL,
	[company_name] [nvarchar](255) NOT NULL,
	[time_period_date] [datetime] NOT NULL,
	[time_period_label] [nvarchar](100) NOT NULL,
	[store_count] [int] NOT NULL,
  [openings_count] [int] NOT NULL,
  [closings_count] [int] NOT NULL,
 CONSTRAINT [PK_ca_store_counts] PRIMARY KEY CLUSTERED
(
	[ca_store_count_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO


---------------------

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[ca_competition](
	[ca_competition_id] [int] IDENTITY(1,1) NOT NULL,
	[home_company_id] [int] NOT NULL,
	[home_company_name] [nvarchar](255) NOT NULL,
	[away_company_id] [int] NOT NULL,
	[away_company_name] [nvarchar](255) NOT NULL,
	[trade_area_threshold] [varchar](50) NOT NULL,
	[time_period_date] [datetime] NOT NULL,
	[time_period_label] [nvarchar](100) NOT NULL,
	[distinct_away_stores] [int] NOT NULL,
	[competitive_instances] [int] NOT NULL,
	[home_store_count] [int] NOT NULL,
	[competition_ratio] [decimal](19, 9) NOT NULL,
	[percent_store_base_affected] [decimal](19, 9) NOT NULL,
 CONSTRAINT [PK_ca_competition] PRIMARY KEY CLUSTERED
(
	[ca_competition_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO



------------------------

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[ca_competition_summary](
	[ca_competition_summary_id] [int] IDENTITY(1,1) NOT NULL,
	[home_company_id] [int] NOT NULL,
	[home_company_name] [nvarchar](255) NOT NULL,
	[trade_area_threshold] [varchar](50) NOT NULL,
	[time_period_date] [datetime] NOT NULL,
	[time_period_label] [nvarchar](100) NOT NULL,
	[competition_ratio] [decimal](19, 9) NOT NULL,
	[percent_store_base_affected] [decimal](19, 9) NOT NULL,
 CONSTRAINT [PK_ca_competition_summary] PRIMARY KEY CLUSTERED
(
	[ca_competition_summary_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO


------------------------

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE TABLE [dbo].[ca_demographic_aggregates](
	[ca_demographics_aggregate_id] [int] IDENTITY(1,1) NOT NULL,
	[company_id] [int] NOT NULL,
	[company_name] [nvarchar](255) NOT NULL,
	[trade_area_threshold] [varchar](50) NOT NULL,
	[time_period_date] [datetime] NOT NULL,
	[time_period_label] [nvarchar](100) NOT NULL,
  [churn_type] [varchar](100) NOT NULL,
	[data_item_id] [int] NOT NULL,
	[demographic_name] [varchar](100) NOT NULL,
	[demographic_description] [varchar](255) NOT NULL,
	[min] [decimal](21, 5) NOT NULL,
	[max] [decimal](21, 5) NOT NULL,
	[avg] [decimal](21, 5) NOT NULL,
	[median] [decimal](21, 5) NOT NULL,
	[stdev] [decimal](21, 5) NOT NULL,
	[min_competition_adjusted] [decimal](21, 5) NOT NULL,
	[max_competition_adjusted] [decimal](21, 5) NOT NULL,
	[avg_competition_adjusted] [decimal](21, 5) NOT NULL,
	[median_competition_adjusted] [decimal](21, 5) NOT NULL,
	[stdev_competition_adjusted] [decimal](21, 5) NOT NULL,
 CONSTRAINT [PK_ca_demographic_aggregates] PRIMARY KEY CLUSTERED
(
	[ca_demographics_aggregate_id] ASC
)WITH (PAD_INDEX  = OFF, STATISTICS_NORECOMPUTE  = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS  = ON, ALLOW_PAGE_LOCKS  = ON) ON [PRIMARY]
) ON [PRIMARY]

GO



------------------------
------------------------
------------------------
------------------------