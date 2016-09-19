from werkzeug.datastructures import ImmutableMultiDict


class DictionaryHelper(object):

    @staticmethod
    def get_projection(dictionary):
        if type(dictionary) is ImmutableMultiDict or type(dictionary) is dict and dictionary is not None:
            projection_list = list()
            non_projection_dictionary = dict()
            for key, value in dictionary.iteritems():
                if key == 'projection':
                    projection_list = dictionary.getlist(key)
                else:
                    non_projection_dictionary[key] = value
            return projection_list, non_projection_dictionary
        else:
            raise Exception("Must pass in a ImmutableMultiDict or dict")

    @staticmethod
    def has_values(dictionary):
        if type(dictionary) is ImmutableMultiDict or type(dictionary) is dict:
            if dictionary is not None:
                for key, value in dictionary.iteritems():
                    if value is not None:
                        return True
                    else:
                        return False
        return False

    # Given a list of keys, checks to ensure each key has a value associated with it.
    @staticmethod
    def keys_have_value(dictionary, keys):
        if type(dictionary) is ImmutableMultiDict or type(dictionary) is dict and type(keys) is dict:
            for key in keys:
                # Ensure key exist
                if key not in dictionary.keys():
                    return False
                # Ensure key has value
                if dictionary[key] is None:
                    return False
            return True
        return False
