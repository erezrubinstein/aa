use retaildb_timeseries_staging
go


select c.name, c2.name, 1, 1, 0, '1/1/1900', ''
from companies c
cross join companies c2
where c.company_id in (70, 68, 74, 69, 72, 65, 63, 66, 64)
order by c.name

--select * from companies

63		O'Reilly AUTO PARTS
64		Auto Parts Independent
65		NAPA Auto Parts
66		PEPBOYS AUTO
67		Tires
68		AUTOPART INTERNATIONAL
69		AutoZone
70		Advance Auto Parts
71		Fast Lube & Oil Change Stores
72		CARQUEST AUTO PARTS
73		New Auto Dealers
74		Auto Plus