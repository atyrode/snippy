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
