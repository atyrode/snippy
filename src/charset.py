from dataclasses import dataclass
import string
from typing import Any

@dataclass(frozen=True) # Makes the class immutable
class URLCharset():
    """Immutable string that represents an URL-safe character set.
    
    Args:
        numeric (bool): Defines if it contains [0-9]
        lowercase_ascii (bool): Defines if it contains  [a-z]
        uppercase_ascii (bool): Defines if it contains  [A-Z]
        special (bool): Defines if it contains [~_-.]
    
    Example:
        >>> custom_charset = URLCharset(numeric=True, lowercase_ascii=True, uppercase_ascii=True, special=True)
        >>> print(custom_charset)
        $ 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ~_-.
    """
    
    numeric: bool
    lowercase_ascii: bool
    uppercase_ascii: bool
    special: bool
    
    # Enforces clear intent of its composition
    def __post_init__(self):
        
        for value in self.__dict__.values():
            if type(value) is not bool: # <- 'is' proves intent, '==' wouldn't
                raise TypeError("URLCharset arguments must be of type boolean")
            
        if not any(self.__dict__.values()) is True:
            raise ValueError("At least one charset type must be True for URLCharset")
    
    @property
    def charset(self) -> str:
        comp: str = str()
        comp += string.digits           if self.numeric         == True else ''
        comp += string.ascii_lowercase  if self.lowercase_ascii == True else ''
        comp += string.ascii_uppercase  if self.uppercase_ascii == True else ''
        comp += "~_-."                  if self.special         == True else ''
        
        return comp
    
    # The redefinition of the dunders below helps URLCharset to behave 
    # like a string while keeping the immutability of the character set.
    def __getitem__(self, index: Any) -> str:
        return self.charset[index]
    
    def __getattr__ (self, name: str) -> Any:
        return getattr(self.charset, name)
    
    def __len__(self) -> int:
        return len(self.charset)

    def __str__(self) -> str:
        return self.charset