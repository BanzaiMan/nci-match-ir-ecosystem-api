class DictionaryHelper(object):

    @staticmethod
    def has_values(dictionary):
        for key, value in dictionary.iteritems():
            if value is not None:
                return True

        return False

    # Given a list of keys, checks to ensure each key has a value associated with it.
    @staticmethod
    def keys_have_value(dictionary, keys):
        for key in keys:
            # Ensure key exist
            if key not in dictionary.keys():
                return False
            # Ensure key has value
            if dictionary[key] is None:
                return False

        return True
