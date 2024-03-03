from dataclasses import dataclass, field
import string

@dataclass(frozen=True) # Makes the class immutable
class URLCharset():
    """String representation of a character set ready to be used
    for a codec, and that is URL-safe.
    
    Args:
        numeric (bool): Adds [0-9] to the charset.
        lowercase_ascii (bool): Adds [a-z] to the charset.
        uppercase_ascii (bool): Adds [A-Z] to the charset.
        special (bool): Adds URL-valid special characters [~_-.] to the charset.
    
    Usage:
        custom_charset = URLCharset(numeric=True, lowercase_ascii=True)
        print(custom_charset)
        $ 0123456789abcdefghijklmnopqrstuvwxyz
    """
    
    numeric: bool
    lowercase_ascii: bool
    uppercase_ascii: bool
    special: bool
    
    charset: str = field(init=False, repr=False, default_factory=str)
    
    def __post_init__(self):
        """Sets the charset attribute after the object's initialization due to
        the immutability of the class. See PEP 557#frozen-instances:
        https://peps.python.org/pep-0557/#frozen-instances"""
        
        included = (
            string.digits           if self.numeric         == True else '',
            string.ascii_lowercase  if self.lowercase_ascii == True else '',
            string.ascii_uppercase  if self.uppercase_ascii == True else '',
            "~_-."                  if self.special         == True else '',
        )
        
        # Join the included character sets and define the 'charset' attribute
        object.__setattr__(self, 'charset', ''.join(included))

    def __str__(self) -> str:
        return self.charset