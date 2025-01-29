from expections import Exception

class BaseError(Exception):
    def __init__(self, message: str,code :str = None,details :dict = None,previous_error:Exception = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.previous_error = previous_error
    def __str__(self):
        return f"{self.__class__.__name__} code: {self.code}) message: {self.message} details: {self.details}"

    def __repr__(self):
        return f"{self.__class__.__name__} code: {self.code}) message: {self.message} details: {self.details}"
    def to_dict(self):
        error_dict = {
            'code': self.code.value,
            'type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }
        
        if self.previous_error:
            error_dict['previous_error'] = str(self.previous_error)
            
        return error_dict
    
    
class ValidationError(BaseError):
    pass

class TemplateValidationError(ValidationError):
    pass



