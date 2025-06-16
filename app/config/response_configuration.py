class ResponseConfiguration:
    """
    Configuration class for response handling.
    """

    def __init__(self, mime_type: str = "application/json", response_schema: dict = None):
        self._response_schema = response_schema or {}
        self._response_mime_type = mime_type
    
    def get_response_schema(self) -> dict:
        """
        Returns the response schema.
        
        :return: Response schema as a dictionary.
        """
        return self._response_schema
    def get_response_mime_type(self):
        """
        Returns the MIME type for the response.
        
        :return: MIME type as a string.
        """
        return self._response_mime_type