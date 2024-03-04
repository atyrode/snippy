import random
import hashlib
from dataclasses import dataclass

from charset import URLCharset

@dataclass(frozen=True) # Makes the class immutable
class Obfuscator():
    charset: URLCharset
    passphrase: str

    # Enforces passphrase charset compatibility and type safety
    def __post_init__(self):
        if not isinstance(self.charset, URLCharset):
            raise TypeError(f"Expected URLCharset, got {type(self.charset).__name__}")
        
        valid_passphrase: str = self._validate_input(self.passphrase)
        object.__setattr__(self, "passphrase", valid_passphrase)

    def _validate_input(self, input: str) -> str:
        """Validates the input to ensure it's fully within the (scrambled) charset."""
        
        if set(input).difference(self.charset) != set():
            raise ValueError(f"The input ({input}) contains characters not in the defined charset ({(str(self.charset))})")
        
        return input
    
    @property
    def _base(self) -> int:
        return len(self.charset)
    
    @property
    def _forward(self) -> int:
        return 1 * len(self.passphrase)
                 # ^ Extra obfuscation
    
    @property
    def _backward(self) -> int:
        return -1 * len(self.passphrase)
    
    @property
    def _sum_passphrase_index(self) -> int:
        return sum([self.charset.index(char) for char in self.passphrase])
    
    @property
    def _scrambled_charset(self) -> str:
        """Scramble the charset based on the passphrase"""

        random.seed(self.passphrase)
        original_charset = list(self.charset)
        scrambled_charset = original_charset.copy()
        random.shuffle(scrambled_charset)
        
        return ''.join(scrambled_charset)
    

    def _translate(self, input: str, shift: int) -> str:
        """Applies a translation to a string based on the codec's charset."""
        
        input = self._validate_input(input)
        
        translated: str = str()
    
        for index, char in enumerate(input):
            # Passphrase
            pp_index: int       = index % len(self.passphrase)
            pp_char_index: int  = self.charset.index(self.passphrase[pp_index])
            translation: int    = (pp_char_index + self._sum_passphrase_index) % self._base
            old_pos: int        = self._scrambled_charset.index(char)
            new_pos: int        = old_pos + (translation * shift)
            new_char: str       = self._scrambled_charset[new_pos % self._base]
            
            translated += new_char
    
        return translated
    
    def transform(self, input: int) -> str:
        """Applies the passphrase-based obfuscation on the input."""
        
        return self._translate(input, self._forward)
    
    def restore(self, input: str) -> int:
        """Reverse the passphrase-based obfuscation on the input."""
        
        return self._translate(input, self._backward)
