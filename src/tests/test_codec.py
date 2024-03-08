import pytest

from src.codec import Codec
from src.charset import URLCharset

@pytest.fixture
def url_charset() -> URLCharset:
    return URLCharset(numeric=True, lowercase_ascii=True, uppercase_ascii=True, special=False)

@pytest.fixture
def codec(url_charset: URLCharset) -> Codec:
    return Codec(charset=url_charset)

def test_encode_decode_symmetry(codec: Codec):
    for i in range(10000):
        encoded = codec.encode(i)
        decoded = codec.decode(encoded)
        assert i == decoded
        
def test_encoding_of_zero(codec: Codec):
    assert codec.encode(0) == codec.charset[0]

def test_decoding_of_zero_character(codec: Codec):
    decoded = codec.decode(codec.charset[0])
    assert decoded == 0

def test_large_number(codec: Codec):
    large_number = 123456789
    encoded = codec.encode(large_number)
    decoded = codec.decode(encoded)
    assert large_number == decoded

def test_invalid_encode_input(codec: Codec):
    with pytest.raises(TypeError):
        codec.encode('not an integer!')

def test_invalid_decode_input(codec: Codec):
    with pytest.raises(ValueError):
        codec.decode('invalid string!')

def test_is_value_url_valid_url(codec: Codec):
    assert codec.is_value_url('https://www.google.com') == True
    assert codec.is_value_url('http://www.google.com') == True
    assert codec.is_value_url('https://google.com') == True
    assert codec.is_value_url('www.google.com') == True
    assert codec.is_value_url('google.com') == True
    assert codec.is_value_url('https://www.google.com/search?q=python') == True
    assert codec.is_value_url('https://www.google.com/search?q=python&rlz=1C1GCEU_enUS832US832&oq=python&aqs=chrome..69i57j0l5.1234j0j7&sourceid=chrome&ie=UTF-8') == True
    
    
def test_is_value_url_not_url(codec: Codec):
    assert codec.is_value_url('Hello World!') == False
    assert codec.is_value_url('1234567890') == False
    assert codec.is_value_url('!@#$%^&*()') == False