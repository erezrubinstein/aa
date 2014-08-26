select * from competitions where home_company_id = away_company_id

begin transaction
insert into competitions (home_company_id, away_company_id)
select c.id as home_company_id, c.id away_company_id
from companies c
commit

select * from competitions where home_company_id = away_company_id
