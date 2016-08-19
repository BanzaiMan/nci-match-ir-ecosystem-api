class DictionaryHelper(object):

    def __init__(self, dict):
        self.dict = dict

    def has_values(self):
        for key, value in self.dict.iteritems():
            if value is not None:
                return True

        return False

    # Given a list of keys, checks to ensure each key has a value associated with it.
    def keys_have_value(self, keys):
        for key in keys:
            # Ensure key exist
            if key not in self.dict.keys():
                return False
            # Ensure key has value
            if self.dict[key] is None:
                return False

        return True

