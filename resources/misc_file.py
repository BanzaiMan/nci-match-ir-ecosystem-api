from resources.generic_file import GenericFile


class MiscFile(GenericFile):

    def get(self, molecular_id, file_name):
        # TODO: why do we put _name on the end? this was supposed to just take the file_name key in and use it.
        return self.get_file_url(molecular_id, str(file_name)+ "_name")
