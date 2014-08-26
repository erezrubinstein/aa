use retaildb_timeseries_lululemon_v20
go
-- get data item ids for age/sex demograhpics
declare @hh_data_items table (data_item_id int primary key, description varchar(100))
insert into @hh_data_items(data_item_id, description)
select data_item_id, description
from data_items di
where di.name like 'FEM%C10' or di.name like 'MAL%C10'

-- get list of current period trade_areas per company
declare @trade_areas table (trade_area_id int primary key, company_name varchar(100))
insert into @trade_areas (trade_area_id, company_name)
select t.trade_area_id, c.name
from stores s
inner join companies c on c.company_id = s.company_id
inner join trade_areas t on t.store_id = s.store_id and t.threshold_id = 1
where s.assumed_closed_date is NULL


-- get demographics per company
declare @demographics table(company_name varchar(100), data_item_id int, description varchar(100), value int, primary key(company_name, description))
insert into @demographics (company_name, data_item_id, description, value)
select 
	t.company_name,
	di.data_item_id,
	di.description, 
	cast(avg(dn.value) as int)
from @trade_areas t
cross join @hh_data_items di
-- left join incase a demographic is missing (i.e. too rich or too poor)
left join demographic_numvalues dn on dn.data_item_id = di.data_item_id and dn.trade_area_id = t.trade_area_id
group by t.company_name, di.data_item_id, di.description


-- display statistics
select 
	d.company_name, 
	d.description,  
	d.value,
	round(d.value / cast(sum.sum as float) * 100, 1) as [percent]
from @demographics d
inner join
(
	select company_name, SUM(value) as sum
	from @demographics
	group by company_name
) sum on sum.company_name = d.company_name
order by d.company_name, d.data_item_id