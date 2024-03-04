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
    def _scrambled_charset(self) -> str:
        """Scramble the charset based on the hashed passphrase"""
        
        # Hash the passphrase to create a more unpredictable seed
        hashed_passphrase = hashlib.sha256(self.passphrase.encode()).hexdigest()
        
        random.seed(hashed_passphrase)
        original_charset = list(self.charset)
        scrambled_charset = original_charset.copy()
        random.shuffle(scrambled_charset)
        
        return ''.join(scrambled_charset)
    
    @property
    def _shift(self) -> int:
        """Shift value based on the passphrase's sum of indexes"""
        
        shift: int = sum(
            self._scrambled_charset.index(char)
            for char
            in self.passphrase
        ) % self._base # <- Ensures wrap-around within the (scrambled) charset
        
        return shift
    
    @property
    def _scrambled_adjusted(self) -> str:
        """Scramble the charset and adjust it based on the shift value"""
        
        scrambled_charset = self._scrambled_charset
        shift = self._shift
        
        return scrambled_charset[shift:] + scrambled_charset[:shift]
        
    def _translate(self, input: str, shift: int) -> str:
        """Applies a translation to a string based on the codec's charset."""
        
        input = self._validate_input(input)
        
        translation: str = str()
        
        for char in input:
            pos: int        = self._scrambled_charset.index(char)
            shifted: int = (pos + shift) % self._base # <- Ensures wrap-around
            
            translation += self._scrambled_charset[shifted]
    
        return translation
    
    def transform(self, input: int) -> str:
        """Applies the passphrase-based obfuscation on the input."""
        
        return self._translate(input, self._shift)
    
    def restore(self, input: str) -> int:
        """Reverse the passphrase-based obfuscation on the input."""
        
        return self._translate(input, -self._shift)
    
    
charset = URLCharset(numeric=True, lowercase_ascii=True, uppercase_ascii=True, special=False)
obfuscator = Obfuscator(charset, "snippy")
print(f"Charset: {obfuscator.charset}")
print(f"Scrambled charset: {obfuscator._scrambled_charset}")
print(f"Passphrase: {obfuscator.passphrase}")
print("-" * 80)
source = 1
obfuscated = obfuscator.transform(source)
deobfuscated = obfuscator.restore(obfuscated)

print(f"Source: {source}")
print(f"Obfuscated: {obfuscated}")
print(f"Deobfuscated: {deobfuscated}")
print("=" * 20)

source = 2
obfuscated = obfuscator.transform(source)
deobfuscated = obfuscator.restore(obfuscated)

print(f"Source: {source}")
print(f"Obfuscated: {obfuscated}")
print(f"Deobfuscated: {deobfuscated}")