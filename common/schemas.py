class Schemas(object):

    @staticmethod
    def get_sequencer_schema():
        return {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "name": {"type": "string"}
            }
        }
