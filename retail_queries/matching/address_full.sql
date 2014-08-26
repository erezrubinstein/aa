select c.name, s0.id as june2011_store_id, s0.phone_number, a.*
from addresses_vw a
inner join stores s0 on s0.id = a.store_id
inner join companies c on c.id = s0.company_id