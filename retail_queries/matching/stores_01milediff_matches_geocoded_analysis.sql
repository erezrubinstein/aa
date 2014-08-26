

--match june based on esri 6 digits?
select m.esri_x, m.esri_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
where round(m.esri_x,6) = round(a0.longitude,6)
	and round(m.esri_y,6) = round(a0.latitude,6);
--0 rows

--match june based on google 6 digits?
select m.google_x, m.google_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
where round(m.google_x,6) = round(a0.longitude,6)
	and round(m.google_y,6) = round(a0.latitude,6);
--0 rows


--match june based on esri 4 digits?
select m.esri_x, m.esri_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
where round(m.esri_x,4) = round(a0.longitude,4)
	and round(m.esri_y,4) = round(a0.latitude,4);
--6 rows

--match june based on google 4 digits?
select m.google_x, m.google_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join retaildb_test_june2011.dbo.addresses_vw a0 on a0.store_id = s0.id
where round(m.google_x,4) = round(a0.longitude,4)
	and round(m.google_y,4) = round(a0.latitude,4);
--17 rows




--match oct based on esri 6 digits?
select m.esri_x, m.esri_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join matching.dbo.stores_matched sm on sm.june2011_store_id = s0.id
inner join retaildb_test_oct2012.dbo.addresses_vw a0 on a0.store_id = sm.oct2012_store_id
where round(m.esri_x,6) = round(a0.longitude,6)
	and round(m.esri_y,6) = round(a0.latitude,6); 
--0 rows

--match oct based on esri 4 digits?
select m.esri_x, m.esri_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join matching.dbo.stores_matched sm on sm.june2011_store_id = s0.id
inner join retaildb_test_oct2012.dbo.addresses_vw a0 on a0.store_id = sm.oct2012_store_id
where round(m.esri_x,4) = round(a0.longitude,4)
	and round(m.esri_y,4) = round(a0.latitude,4); 
--53 rows


--match oct based on google 6 digits?
select m.google_x, m.google_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join matching.dbo.stores_matched sm on sm.june2011_store_id = s0.id
inner join retaildb_test_oct2012.dbo.addresses_vw a0 on a0.store_id = sm.oct2012_store_id
where round(m.google_x,6) = round(a0.longitude,6)
	and round(m.google_y,6) = round(a0.latitude,6); 
--0 rows

--match oct based on google 4 digits?
select m.google_x, m.google_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join matching.dbo.stores_matched sm on sm.june2011_store_id = s0.id
inner join retaildb_test_oct2012.dbo.addresses_vw a0 on a0.store_id = sm.oct2012_store_id
where round(m.google_x,4) = round(a0.longitude,4)
	and round(m.google_y,4) = round(a0.latitude,4); 
--73 rows






--match oct based on esri 3 digits?
select m.esri_x, m.esri_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join matching.dbo.stores_matched sm on sm.june2011_store_id = s0.id
inner join retaildb_test_oct2012.dbo.addresses_vw a0 on a0.store_id = sm.oct2012_store_id
where round(m.esri_x,3) = round(a0.longitude,3)
	and round(m.esri_y,3) = round(a0.latitude,3); 
--695 rows

--match oct based on google 3 digits?
select m.google_x, m.google_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join matching.dbo.stores_matched sm on sm.june2011_store_id = s0.id
inner join retaildb_test_oct2012.dbo.addresses_vw a0 on a0.store_id = sm.oct2012_store_id
where round(m.google_x,3) = round(a0.longitude,3)
	and round(m.google_y,3) = round(a0.latitude,3); 
--756 rows


--match oct based on esri or google 3 digits?
select m.esri_x, m.esri_y, m.google_x, m.google_y, a0.longitude, a0.latitude, a0.fulladdress, m.google_formatted_address
from stores_01milediff_matches m
inner join retaildb_test_june2011.dbo.stores s0 on s0.id = m.store_id
inner join matching.dbo.stores_matched sm on sm.june2011_store_id = s0.id
inner join retaildb_test_oct2012.dbo.addresses_vw a0 on a0.store_id = sm.oct2012_store_id
where (
	round(m.esri_x,3) = round(a0.longitude,3)
	and round(m.esri_y,3) = round(a0.latitude,3)
	)
	or (
	round(m.google_x,3) = round(a0.longitude,3)
	and round(m.google_y,3) = round(a0.latitude,3)
	)
	; 
--1155 rows