from dataclasses import dataclass, field
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
    
    # Excluded of __repr__ since it actually represents the computation of __repr__
    charset: str = field(init=False, repr=False)
    
    def __post_init__(self):
        """Enforces clear intent of its composition and sets it as an 
        instance attribute"""
        
        for value in self.__dict__.values():
            if type(value) is not bool: # <- 'is' proves intent, '==' wouldn't
                raise TypeError("URLCharset arguments must be of type boolean")

        comp: str = str()
        comp += string.digits           if self.numeric         == True else ''
        comp += string.ascii_lowercase  if self.lowercase_ascii == True else ''
        comp += string.ascii_uppercase  if self.uppercase_ascii == True else ''
        comp += "~_-."                  if self.special         == True else ''
        
        if len(comp) == 0:
            raise ValueError("At least one charset type must be True for URLCharset")

        # See PEP 557: https://peps.python.org/pep-0557/#frozen-instances
        object.__setattr__(self, 'charset', comp)
    
    
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