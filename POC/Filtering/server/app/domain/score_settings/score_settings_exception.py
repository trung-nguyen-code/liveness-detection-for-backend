class BadFormatError(Exception):
    message = "The setting you spcecified may not correct."

    def __str__(self):
        return BadFormatError.message
