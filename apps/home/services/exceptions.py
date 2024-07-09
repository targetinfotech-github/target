class CustomException(Exception):
    pass

class ModelNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'DetailedDataError: {self.message}'

class NoResultsFoundError(Exception):
    pass

class MissingQueryError(Exception):
    pass