
class MockMDSAccess(object):
    def __init__(self):
        self.entities = {}
        self.params_entities = {}


    def call_delete_reset_database(self):
        self.entities = {}
        self.params_entities = {}


    def call_get_entity(self, entity_type, entity_id, params = None):
        if params:
            return self.params_entities[entity_type][entity_id][params]
        else:
            return self.entities[entity_type][entity_id]


    def call_update_entity(self,
                           entity_type,
                           entity_id,
                           context_rec,
                           field_name = None,
                           field_value = None,
                           field_data = None):
        entity = self.entities[entity_type][entity_id]

        if field_data:
            for key in field_data.iterkeys():
                entity[key] = field_data[key]
        else:
            entity[field_name] = field_value


    def add_params_entity(self, entity_type, entity_id, params, entity):
        if entity_type not in self.params_entities:
            self.params_entities[entity_type] = {}
        if entity_id not in self.params_entities[entity_type]:
            self.params_entities[entity_type][entity_id] = {}
        self.params_entities[entity_type][entity_id][str(params)] = entity