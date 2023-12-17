class ProfileNotFoundError(Exception):
    message = "The you profile you spcecified does not exist."

    def __str__(self):
        return ProfileNotFoundError.message


class ProfilesNotFoundError(Exception):
    message = "No you profiles were found."

    def __str__(self):
        return ProfilesNotFoundError.message
