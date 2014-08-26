use DOLLFULL_JUN13_CMA_062313
go


declare @fixed_stores table (store_id int, latitude float, longitude float)
insert into @fixed_stores
select 51323, 33.080176, -87.5613 union all
select 35187, 28.233765, -82.3016 union all
select 35248, 32.056028, -95.504 union all
select 60836, 34.441579, -88.1446 union all
select 42903, 34.19766, -77.8909 union all
select 49782, 33.464829, -87.6269 union all
select 49831, 34.919445, -79.7839 union all
select 49957, 36.150073, -81.1994 union all
select 50040, 35.9017666, -90.7980376 union all
select 49844, 36.0858781, -87.4076608 union all
select 61099, 41.9891939, -88.3407411 union all
select 35480, 32.3550967, -95.3432661 union all
select 50695, 35.9179751, -90.5886806 union all
select 36012, 32.8036013, -81.9100382 union all
select 50676, 34.9782637, -85.2126544 union all
select 54063, 34.1973930, -79.7015710 union all
select 49780, 38.04667790, -97.34503649999999 union all
select 60053, 31.0999095, -91.2858793 union all
select 35354, 26.40992820, -98.95824180 union all
select 50816, 29.6617458, -90.1092707 union all
select 49905, 33.83121850, -87.27750530 union all
select 49769, 36.53457260, -87.78059990000001 union all
select 49655, 34.51148830, -83.52711660 union all
select 54194, 35.93378620, -86.88248380 union all
select 58036, 34.2706940, -85.1976440 union all
select 6088, 35.725885, -78.655652 union all
select 18819, 26.894194, -80.061745 union all
select 11981, 36.712777, -95.937458 union all
select 13384, 44.797373, -69.872193 union all
select 21228, 39.697136, -74.269429 union all
select 18582, 27.838451, -80.487121 union all
select 61590, 39.474695, -90.378988 union all
select 8628, 36.766092, -108.146503 union all
select 8859, 40.755572, -73.945127 union all
select 6311, 36.138975, -81.102041 union all
select 18830, 26.618541, -80.056922 union all
select 9197, 34.93871, -82.264543 union all
select 8651, 35.115385, -106.513831 union all
select 61624, 34.170679, -79.399676 union all
select 18765, 25.79448590, -80.13986469999999 union all
select 8850, 40.836928, -73.943164 union all
select 3438, 28.329498, -82.668591 union all
select 2399, 41.635809, -88.204822 union all
select 137414, 42.419889, -83.003327 union all
select 164009, 36.677874, -101.48199 union all
select 134587, 39.233728, -76.612299 union all
select 194951, 38.094725, -81.837964 union all
select 118966, 33.859479, -83.406813 union all
select 154219, 35.668048, -105.988031 union all
select 111082, 28.697273, -81.357801 union all
select 126321, 37.878955, -87.566495 union all
select 159465, 41.208756, -73.984967 union all
select 92540, 33.35227, -86.78358 union all
select 156295, 40.828169, -73.292539 union all
select 153519, 39.812365, -74.931028 union all
select 129749, 37.137206, -83.764889 union all
select 185747, 30.429171, -95.470939 union all
select 181878, 30.057044, -94.814926 union all
select 92131, 32.492034, -87.855768 union all
select 179260, 32.851602, -96.56924 union all
select 185136, 33.072995, -96.875938 union all
select 141925, 39.333649, -91.181574 union all
select 184701, 30.346218, -94.178737 union all
select 157689, 40.791872, -73.416133 union all
select 173650, 36.380553, -82.366219 union all
select 182166, 30.230797, -94.193699 union all
select 181043, 29.416361, -96.049033 union all
select 123660, 41.833866, -87.873588 union all
select 129251, 37.761648, -86.441877 union all
select 152727, 39.446468, -74.702347 union all
select 167979, 41.339872, -74.840753 union all
select 95078, 34.554435, -90.71494 union all
select 93610, 31.78212, -85.950105 union all
select 181264, 29.890916, -95.583904 union all
select 92727, 32.975219, -86.033523 union all
select 149721, 35.747349, -81.600247 union all
select 128938, 36.910283, -84.151748 union all
select 117884, 31.175661, -83.761096 union all
select 170492, 33.944384, -80.872422 union all
select 187349, 36.723162, -76.306552 union all
select 144644, 33.861489, -89.845143 union all
select 146835, 35.614203, -78.417171 union all
select 173862, 36.407449, -84.061731 union all
select 131876, 31.411548, -92.484183 union all
select 91964, 33.349216, -86.630084 union all
select 184604, 29.760234, -96.222666 union all
select 186122, 40.711612, -112.092649 union all
select 113490, 28.786037, -81.213418 union all
select 132248, 29.753041, -90.728791 union all
select 112188, 29.800916, -82.971156 union all
select 128676, 37.639736, -82.754373 union all
select 160306, 39.290126, -84.299362 union all
select 145608, 33.634041, -88.659506 union all
select 181377, 32.957081, -97.281689 union all
select 93365, 34.437895, -88.136507 union all
select 108272, 39.071608, -75.552508 union all
select 142417, 39.200071, -94.549261 union all
select 163957, 36.90637, -100.531321 union all
select 131658, 29.692917, -91.178069 union all
select 194924, 39.270732, -80.325573 union all
select 139797, 44.72632676, -85.6460406 union all
select 141359, 47.056912, -93.92367 union all
select 187811, 38.28155, -77.448162


declare @fixed_stores_with_old table (store_id int, latitude decimal(9, 6), longitude decimal(9, 6), bad_lat decimal(9, 6), bad_long decimal(9, 6))
insert into @fixed_stores_with_old
select fix.store_id, fix.latitude as good_lat, fix.longitude as good_long,
	a.latitude as bad_lat, a.longitude as bad_lat
from @fixed_stores fix
inner join stores s on s.store_id = fix.store_id
inner join addresses a on a.address_id = s.address_id


select distinct
	cast(s.company_id as varchar(100)) + ',' + cast(s.store_id as varchar(100))
from @fixed_stores_with_old fix
inner join addresses a on 
	((a.latitude between fix.latitude - 0.3 and fix.latitude + 0.3) and (a.longitude between fix.longitude - 0.3 and fix.longitude + 0.3))
	or
	((a.latitude between fix.bad_lat - 0.3 and fix.bad_lat + 0.3) and (a.longitude between fix.bad_long - 0.3 and fix.bad_long + 0.3))
inner join stores s on s.address_id = a.address_id and s.store_id <> fix.store_id
where s.company_id in (70, 81, 67, 65, 80, 71, 64, 77)

--select t.store_id, count(*)
--from 
--(
--	select fix.store_id
--	from @fixed_stores_with_old fix
--	inner join addresses a on 
--		((a.latitude between fix.latitude - 0.3 and fix.latitude + 0.3) and (a.longitude between fix.longitude - 0.3 and fix.longitude + 0.3))
--		or
--		((a.latitude between fix.bad_lat - 0.3 and fix.bad_lat + 0.3) and (a.longitude between fix.bad_long - 0.3 and fix.bad_long + 0.3))
--	inner join stores s on s.address_id = a.address_id and s.store_id <> fix.store_id
--) t
--group by t.store_id
--order by count(*) desc