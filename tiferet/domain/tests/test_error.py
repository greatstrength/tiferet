# *** imports 

# ** infra
import pytest

# ** app
from . import *


# *** 

# ** test: test_error_message_new
def test_error_message_new(test_error_message):

    # Check if the ErrorMessage is correctly instantiated
    assert test_error_message.lang == 'en_US'
    assert test_error_message.text == 'An error occurred.'


# ** test: test_error_message_format
def test_error_message_format(test_error_message, test_formatted_error_message):

    # Test basic formatting
    assert test_error_message.format() == 'An error occurred.'
    # Test formatting with arguments
    assert test_formatted_error_message.format('Check for bugs.') == 'An error occurred: Check for bugs.'


# ** test: test_error_new
def test_error_new(test_error):

    # Check if the Error object is correctly instantiated
    assert test_error.name == 'MY_ERROR'
    assert test_error.id == 'MY_ERROR'
    assert test_error.error_code == 'MY_ERROR'
    assert len(test_error.message) == 1
    assert test_error.message[0].lang == 'en_US'


# ** test: test_error_format_method
def test_error_format_method(test_error, test_error_with_formatted_message):
   
    # Test formatting with arguments
    assert test_error.format('en_US') == 'An error occurred.'

    # Test formatting with arguments
    assert test_error_with_formatted_message.format('en_US', 'Check for bugs.') == 'An error occurred: Check for bugs.'


# ** test: test_error_id_and_code_customization
def test_error_id_and_code_customization(test_error_with_custom_id_and_code):
    
   # Check if the custom ID and error code are set correctly
    assert test_error_with_custom_id_and_code.name == 'CUSTOM_ERROR'
    assert test_error_with_custom_id_and_code.id == 'CUSTOM_ERROR'
    assert test_error_with_custom_id_and_code.error_code == 'CUSTOM_ERR'
