USE [master]
GO

/****** Object:  Database [application_logging_staging]    Script Date: 11/27/2012 09:46:22 ******/
CREATE DATABASE [application_logging_staging] ON  PRIMARY 
( NAME = N'application_logging_data', FILENAME = N'D:\SQLData\application_logging_staging.mdf' , SIZE = 2048KB , MAXSIZE = UNLIMITED, FILEGROWTH = 1024KB )
 LOG ON 
( NAME = N'application_logging_log', FILENAME = N'D:\SQLData\application_logging_staging.ldf' , SIZE = 1024KB , MAXSIZE = 2048GB , FILEGROWTH = 10%)
GO

ALTER DATABASE [application_logging_staging] SET COMPATIBILITY_LEVEL = 100
GO

IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [application_logging_staging].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO

ALTER DATABASE [application_logging_staging] SET ANSI_NULL_DEFAULT OFF 
GO

ALTER DATABASE [application_logging_staging] SET ANSI_NULLS OFF 
GO

ALTER DATABASE [application_logging_staging] SET ANSI_PADDING OFF 
GO

ALTER DATABASE [application_logging_staging] SET ANSI_WARNINGS OFF 
GO

ALTER DATABASE [application_logging_staging] SET ARITHABORT OFF 
GO

ALTER DATABASE [application_logging_staging] SET AUTO_CLOSE OFF 
GO

ALTER DATABASE [application_logging_staging] SET AUTO_CREATE_STATISTICS ON 
GO

ALTER DATABASE [application_logging_staging] SET AUTO_SHRINK OFF 
GO

ALTER DATABASE [application_logging_staging] SET AUTO_UPDATE_STATISTICS ON 
GO

ALTER DATABASE [application_logging_staging] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO

ALTER DATABASE [application_logging_staging] SET CURSOR_DEFAULT  GLOBAL 
GO

ALTER DATABASE [application_logging_staging] SET CONCAT_NULL_YIELDS_NULL OFF 
GO

ALTER DATABASE [application_logging_staging] SET NUMERIC_ROUNDABORT OFF 
GO

ALTER DATABASE [application_logging_staging] SET QUOTED_IDENTIFIER OFF 
GO

ALTER DATABASE [application_logging_staging] SET RECURSIVE_TRIGGERS OFF 
GO

ALTER DATABASE [application_logging_staging] SET  DISABLE_BROKER 
GO

ALTER DATABASE [application_logging_staging] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO

ALTER DATABASE [application_logging_staging] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO

ALTER DATABASE [application_logging_staging] SET TRUSTWORTHY OFF 
GO

ALTER DATABASE [application_logging_staging] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO

ALTER DATABASE [application_logging_staging] SET PARAMETERIZATION SIMPLE 
GO

ALTER DATABASE [application_logging_staging] SET READ_COMMITTED_SNAPSHOT OFF 
GO

ALTER DATABASE [application_logging_staging] SET HONOR_BROKER_PRIORITY OFF 
GO

ALTER DATABASE [application_logging_staging] SET  READ_WRITE 
GO

ALTER DATABASE [application_logging_staging] SET RECOVERY FULL 
GO

ALTER DATABASE [application_logging_staging] SET  MULTI_USER 
GO

ALTER DATABASE [application_logging_staging] SET PAGE_VERIFY CHECKSUM  
GO

ALTER DATABASE [application_logging_staging] SET DB_CHAINING OFF 
GO


