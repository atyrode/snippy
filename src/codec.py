import re

from dataclasses import dataclass

from .charset import URLCharset
    
# Codec class isn't the best definition of a 'dataclass' as it contains logic
# but it benefits from immutability without having to manually define it.
@dataclass(frozen=True) 
class Codec():
    """Translates an integer to a URL-safe string and vice-versa based on
    the provided URLCharset and its base.
    """
    
    charset: URLCharset
    
    def __post__init__(self):        
        if not isinstance(self.charset, URLCharset):
            raise TypeError(f"Expected URLCharset, got {type(self.charset).__name__}")
    
    @property
    def _base(self) -> int:
        return len(self.charset)
    
    def is_value_url(self, value: str) -> bool:
        """Returns True if the value matches the URL regex pattern.
        False means the value should be treated as text."""
        regex = r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
        return re.match(regex, value) is not None
    
    def encode(self, id: int) -> str:
        encoded: str    = str()
        remainder: int  = int()
        
        if id == 0:
            return self.charset[0]
        
        while id > 0:
            id, remainder = divmod(id, self._base)
            encoded = self.charset[remainder] + encoded
        
        return encoded

    def decode(self, encoded: str) -> int:
        decoded: int = int()
        
        for char in encoded:
            decoded = decoded * self._base + self.charset.index(char)

        return decoded