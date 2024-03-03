import string
from itertools import product

import pytest

from codec import URLCharset

CHARSETS = {
    "numeric":          string.digits,
    "lowercase_ascii":  string.ascii_lowercase,
    "uppercase_ascii":  string.ascii_uppercase,
    "special":          "~_-." # URL-valid special characters
}

BOOL_COMBINATIONS = [
    # Generates a dict with the format charset_type: bool
    {key: value for key, value in zip(CHARSETS.keys(), combination)}
    # for each charset
    for combination
    # for each combination of True/False
    in product([True, False], repeat=len(CHARSETS))
]

def match_charset(combination: dict) -> str:
    """Computes the charset that matches the given combination of requirements
    
    Example:
        >>> match_charset({'numeric': False, 'lowercase_ascii': False, 'uppercase_ascii': True, 'special': True})
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ~_-.'
    """
    
    return ''.join(
        [CHARSETS[key] for key, value 
        in combination.items()
        if value]
    )

def test_charset_wrong_arg_format():
    with pytest.raises(TypeError):
        URLCharset()
        
def test_charset():
    for combination in BOOL_COMBINATIONS:
        charset = match_charset(combination)
        
        # If the produced charset is empty, (all properties set to false)
        # the object should raise a ValueError
        if all(combination.values()) is False:
            with pytest.raises(ValueError):
                URLCharset(**combination)
        else:
            assert charset == str(URLCharset(**combination))
        
def test_charset_immutable():
    custom_charset = URLCharset(**BOOL_COMBINATIONS[0])
    with pytest.raises(AttributeError):
        custom_charset.charset = '0123456789abcdefghijklmnopqrstuvwxyz'
        
def test_charset_repr():
    custom_charset = URLCharset(**BOOL_COMBINATIONS[0])
    assert repr(custom_charset) == "URLCharset(numeric=True, lowercase_ascii=True, uppercase_ascii=True, special=True)"
    
def test_charset_post_init():
    custom_charset = URLCharset(**BOOL_COMBINATIONS[0])
    assert custom_charset.charset == str(custom_charset)
    
def test_charset_wrong_type():
    with pytest.raises(TypeError):
        URLCharset(numeric="test", lowercase_ascii=True, uppercase_ascii=True, special=True)
