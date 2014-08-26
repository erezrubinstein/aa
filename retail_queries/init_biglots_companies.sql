--to get the company names as in the files:
--head -n 1 data/company_load/working/*.csv

begin transaction

--just to make sure we get company id = 1 as the first one
dbcc checkident(companies, reseed, 0);

--init all to the same date
declare @now datetime = getutcdate();

select * from companies;

insert into companies (ticker, name, created_at, updated_at) values ('','99 Cents Only Stores',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Big Lots',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Dollar General',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Dollar Tree',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Family Dollar',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Fred''s',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','HomeGoods',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Kmart',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Ollie''s Bargain Outlet',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Target',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Tuesday Morning',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Walmart Discount Store',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Walmart Express',@now,@now);
insert into companies (ticker, name, created_at, updated_at) values ('','Walmart Supercenter',@now,@now);

select * from companies;

commit

--dbcc checkident(companies, reseed, 0)
--Checking identity information: current identity value '13', current column value '1'.
--DBCC execution completed. If DBCC printed error messages, contact your system administrator.
