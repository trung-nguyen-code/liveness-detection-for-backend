class UserInteractionNotFoundError(Exception):
    message = "The user interactions you spcecified does not exist."

    def __str__(self):
        return UserInteractionNotFoundError.message
