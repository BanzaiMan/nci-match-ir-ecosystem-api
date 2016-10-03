from resources.generic_file import GenericFile


class MiscFile(GenericFile):

    def get(self, molecular_id, file_name):
        return self.get_file_url(molecular_id, str(file_name)+ "_name")
