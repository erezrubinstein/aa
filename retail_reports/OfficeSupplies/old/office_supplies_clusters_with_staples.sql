use retaildb_timeseries_office_supplies_v2
go

--select * from thresholds
declare @trade_area_threshold int = 5 -- id for 5 miles
declare @OD int = 63
declare @OM int = 65
declare @SP int = 64

-- create competition temp table
declare @all_relationships table(home_store_id int, home_company_id int, away_store_id int, away_company_id int)
insert into @all_relationships
select 
	cs.home_store_id,
	s_home.company_id,
	cs.away_store_id,
	s_away.company_id
from trade_areas t
inner join competitive_stores cs on cs.trade_area_id = t.trade_area_id
inner join stores s_home on s_home.store_id = cs.home_store_id
inner join stores s_away on s_away.store_id = cs.away_store_id
where t.threshold_id = @trade_area_threshold
	-- no same player comps
	and s_home.company_id != s_away.company_id

	
	
-- create list of companies which remain unprocesses (for circular loop recognition)
create table #clusters (row_number int identity(1,1), store_id int, company_id int, cluster_id int, players int)

insert into #clusters
select distinct
	home_store_id, 
	home_company_id,
	NULL, -- no cluster by default
	2 -- 2 players by default
from @all_relationships
order by home_store_id



-- declare variables for loop state
declare @counter int = 1
declare @count_distinct_stores int = (select count(*) from #clusters)
declare @current_store int
declare @current_store_cluster_id int
declare @cluster_id_counter int = 1

-- loop and add to cluster
WHILE @counter <= @count_distinct_stores
BEGIN
	-- get current store and its cluster id
	set @current_store = (select top 1 store_id from #clusters where row_number = @counter)
	set @current_store_cluster_id = (select top 1 cluster_id from #clusters where row_number = @counter)
	
	-- if no cluster id is set, than give it a new cluster id
	if @current_store_cluster_id is null
	BEGIN
		-- set current cluster id of record
		set @current_store_cluster_id = @cluster_id_counter
		update #clusters set cluster_id = @current_store_cluster_id where row_number = @counter
		
		-- increment cluster counter
		set @cluster_id_counter = @cluster_id_counter + 1
	END
	
	-- find all stores that compete with this store and update their cluster id to be the same
	update cl set cluster_id = @current_store_cluster_id
	from #clusters cl
	inner join
	(
		select cl2.cluster_id
		from @all_relationships comp
		inner join #clusters cl2 on cl2.store_id = comp.away_store_id
		where comp.home_store_id = @current_store
			and cl2.cluster_id is not null and cl2.cluster_id <> @current_store_cluster_id
	) t on t.cluster_id = cl.cluster_id
	
	
	-- find all stores that compete with this store and update their cluster id to be the same
	update cl set cluster_id = @current_store_cluster_id
	from @all_relationships comp
	inner join #clusters cl on cl.store_id = comp.away_store_id
	where comp.home_store_id = @current_store

	-- increment counter
	set @counter = @counter + 1
END

-- remove any clusters that don't have office depot and staples in it
delete from #clusters 
where cluster_id in 
(
	--find all clusters with 2 companies and one of them is staples
	select cl_complete.cluster_id
	from #clusters cl_sp
	inner join #clusters cl_complete on cl_complete.cluster_id = cl_sp.cluster_id
	where cl_sp.company_id = @SP
	group by cl_complete.cluster_id
	having count(distinct cl_complete.company_id) = 2
)



-- find all clusters that have stapes in them and update players
update cl_entire_cluster set players = 3
from #clusters cl
inner join #clusters cl_entire_cluster on cl_entire_cluster.cluster_id = cl.cluster_id
where cl.company_id = @SP

-- group by count by players
select *
from
(
	select cluster_id, players, count(*) as count
	from #clusters
	group by cluster_id, players
) t
pivot
(
	COUNT(cluster_id)
	for players in ([1], [2], [3])
) p
order by count


--select * from #clusters order by cluster_id

--select cluster_id, count(*) 
--from #clusters
--group by cluster_id
--order by count(*) desc

--select cl.*, s.company_id, a.street_number, a.street, a.municipality, a.governing_district, a.postal_area, a.longitude, a.latitude
--from #clusters cl
--inner join stores s on s.store_id = cl.store_id
--inner join addresses a on a.address_id = s.address_id
--order by cl.cluster_id


drop table #clusters