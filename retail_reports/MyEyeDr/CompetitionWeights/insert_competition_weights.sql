use retaildb_timeseries_staging_myeyedr
go

declare @comps table (home_company varchar(100), away_company varchar(100), strength float)
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, 
	case 
		when home.name = 'Optometrists and Insurance Companies' then 0
		when away.name = 'Optometrists and Insurance Companies' then 0
		when home.name = 'SHAMIR' then 0
		when away.name = 'SHAMIR' then 0
		when home.name = 'ACUVUE' then 0
		when away.name = 'ACUVUE' then 0
		else 1
	end as strength
from companies home
cross join companies away


insert into weighed_competitive_weights(home_company_id, away_company_id, strength)
select 
	ch.company_id as home_company_id,
	ca.company_id as away_company_id,
	c.strength
from @comps c
inner join companies ch on ch.name = c.home_company
inner join companies ca on ca.name = c.away_company

