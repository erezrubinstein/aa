use retaildb_timeseries_wfm_organic
go

select * from companies

declare @comps_group_1 table (name varchar(100))
insert into @comps_group_1
SELECT 'WHOLE FOODS MARKET' UNION ALL
SELECT 'WHOLE FOODS MARKET STORES IN DEVELOPMENT' UNION ALL
SELECT 'THE FRESH MARKET' UNION ALL
SELECT 'FAIRWAY' UNION ALL
SELECT 'fresh & easy' UNION ALL
SELECT 'PAVILIONS' UNION ALL
SELECT 'Wegmans' UNION ALL
SELECT 'SPROUTS - All Banners' UNION ALL
SELECT 'Earth Fare' UNION ALL
SELECT 'Bristol Farms' UNION ALL
SELECT 'NEW SEASONS MARKET' UNION ALL
SELECT 'metropolitanmarket' UNION ALL
SELECT 'BALDUCCI''S' 

declare @comps_group_2 table (name varchar(100))
insert into @comps_group_2
SELECT 'NATURAL GROCERS' UNION ALL
SELECT 'AKiN''S NATURAL FOODS MARKET' UNION ALL
SELECT 'CHAMBERLIN''S MARKET & CAFÉ' UNION ALL
SELECT 'Earth Origins - All Banners' UNION ALL
SELECT 'Other High-End Natural/Organic/Gourmet Grocers'

declare @comps_group_3 table (name varchar(100))
insert into @comps_group_3
SELECT 'TRADER JOE''S' UNION ALL
SELECT 'Warehouse' UNION ALL
SELECT 'Mainstream Grocery'



declare @comps table (home_company varchar(100), away_company varchar(100), strength float)

-- insert 1 to 1
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, 1
from @comps_group_1 home
cross join @comps_group_1 away

-- insert 1 to 2
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, .6
from @comps_group_1 home
cross join @comps_group_2 away

-- insert 1 to 3
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, .3
from @comps_group_1 home
cross join @comps_group_3 away


-- insert 2 to 1
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, 1
from @comps_group_2 home
cross join @comps_group_1 away
order by home.name


-- insert 2 to 2
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, 1
from @comps_group_2 home
cross join @comps_group_2 away
order by home.name


-- insert 2 to 3
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, .3
from @comps_group_2 home
cross join @comps_group_3 away
order by home.name


-- insert 3 to 1 (only trader joes)
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, 1
from @comps_group_3 home
cross join @comps_group_1 away
where home.name = 'TRADER JOE''S'
order by home.name


-- insert 3 to 2 (only trader joes)
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, .6
from @comps_group_3 home
cross join @comps_group_2 away
where home.name = 'TRADER JOE''S'
order by home.name


-- insert 3 to 3 (only trader joes)
insert into @comps(home_company, away_company, strength) 
select home.name, away.name, 
	case 
		when away.name = 'TRADER JOE''S' then 1
		else .6
	end as strength
from @comps_group_3 home
cross join @comps_group_3 away
where home.name = 'TRADER JOE''S'
order by home.name




insert into weighed_competitive_weights(home_company_id, away_company_id, strength)
select 
	ch.company_id as home_company_id,
	ca.company_id as away_company_id,
	c.strength
from @comps c
inner join companies ch on ch.name = c.home_company
inner join companies ca on ca.name = c.away_company
