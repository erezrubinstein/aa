select c.company_id, c.name, c.ticker, count(*) count_stores
from stores s
inner join companies c on c.company_id = s.company_id
group by c.company_id, c.name, c.ticker
order by c.company_id, c.name, c.ticker;