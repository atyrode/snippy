import pytest

from obfuscator import Obfuscator
from charset import URLCharset

## Fixtures ##

# Shouldn't be invalid due to its own tests and post_init checks
@pytest.fixture
def charset() -> URLCharset:
    # "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ~_-."
    return URLCharset(numeric=True, lowercase_ascii=True, uppercase_ascii=True, special=True)

@pytest.fixture
def obfuscator(charset: URLCharset) -> Obfuscator:
    return Obfuscator(charset, "snippy")

@pytest.fixture
def passphrase(obfuscator: Obfuscator) -> str:
    return obfuscator.passphrase

## Init ##

def test_valid_init(obfuscator: Obfuscator):
    assert isinstance(obfuscator, Obfuscator)

def test_invalid_init_passphrase(charset: URLCharset):
    with pytest.raises(ValueError):
        Obfuscator(charset, "invalid!") # <- '!' can't be found in any charset

def test_invalid_init_charset(passphrase: str):
    with pytest.raises(TypeError):
        Obfuscator(int(), passphrase)

## Transform & Restore ##

def test_valid_transform(obfuscator: Obfuscator):
    input: str          = "test"
    transformed: str    = obfuscator.transform(input)
    
    assert transformed != input

def test_invalid_transform(obfuscator: Obfuscator):
    input: str          = "test!"
    
    with pytest.raises(ValueError):
        obfuscator.transform(input)
        
def test_empty_string_transform(obfuscator: Obfuscator):
    input: str          = str()
    transformed: str    = obfuscator.transform(input)
    
    assert transformed == str()   

def test_valid_restore(obfuscator: Obfuscator):
    input: str          = "test"
    transformed: str    = obfuscator.transform(input)
    restored: str       = obfuscator.restore(transformed)
    
    assert restored == input
    
def test_invalid_restore(obfuscator: Obfuscator):
    input: str          = "test!"
    
    with pytest.raises(ValueError):
        obfuscator.restore(input)

def test_empty_string_restore(obfuscator: Obfuscator):
    input: str          = str()
    restored: str       = obfuscator.restore(input)
    
    assert restored == str()
    
    
## Unpredactability ##

# We ensure that we don't get the next result by increasing the charset index
# by one for the last character in the obfuscated string

def test_unpredactability(obfuscator: Obfuscator):
    input: str          = "test"
    transformed: str    = obfuscator.transform(input)
    last_char: str      = transformed[-1]
    last_char_index: int= obfuscator.charset.index(last_char)
    
    # Increase the last character index by one
    transformed = transformed[:-1] + obfuscator.charset[last_char_index + 1]
    
    restored: str       = obfuscator.restore(transformed)
    
    assert restored != input