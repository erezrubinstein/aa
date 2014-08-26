CREATE TABLE #t (t_a_id int);

INSERT INTO #t (t_a_id) 
SELECT     trade_area_id
FROM         demographic_numvalues
GROUP BY trade_area_id
HAVING     (COUNT(trade_area_id) < 251 and COUNT(trade_area_id) > 200);

SELECT convert(varchar(250), stores.id) + ', ' + convert(varchar(250), stores.company_id) 
FROM stores
INNER JOIN trade_areas on stores.id = trade_areas.store_id
INNER JOIN #t on #t.t_a_id = trade_areas.id;

DROP TABLE #t;