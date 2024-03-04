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
        
        self._validate_input(self.passphrase)

    @property
    def _base(self) -> int:
        return len(self.charset)
    
    @property
    def _shift(self) -> int:
        """Shift value based on the passphrase's sum of indexes"""
        
        shift: int = sum(
            self.charset.index(char)
            for char
            in self.passphrase
        ) % self._base # <- Ensures wrap-around within the charset
        
        return shift
    
    def _validate_input(self, input: str) -> None:
        """Validates the input to ensure it's fully within the charset."""
        
        if set(input).difference(self.charset) != set():
            raise ValueError(f"The input ({input}) contains characters not in the defined charset ({(str(self.charset))})")
        
    def _translate(self, input: str, shift: int) -> str:
        """Applies a translation to a string based on the codec's charset."""
        
        self._validate_input(input)
        
        translation: str = str()
        
        for char in input:
            pos: int        = self.charset.index(char)
            shifted: int = (pos + shift) % self._base # <- Ensures wrap-around
            
            translation += self.charset[shifted]
    
        return translation
    
    def transform(self, input: str) -> str:
        """Applies the passphrase-based obfuscation on the input."""
        
        return self._translate(input, self._transform_shift)
    
    def restore(self, input: str) -> str:
        """Reverse the passphrase-based obfuscation on the input."""
        
        return self._translate(input, -self._transform_shift)