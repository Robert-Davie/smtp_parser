from parser import SmtpParser
import pytest


def test_get_response_code_valid():
    response = b'221 Bye\r\n'
    p = SmtpParser()
    assert p.get_response_code(response) == 221


def test_get_response_code_valid_string():
    response = '221 Bye\r\n'
    p = SmtpParser()
    assert p.get_response_code(response) == 221


def test_get_response_code_and_message():
    response = '221 Bye\r\n'
    p = SmtpParser()
    assert p.response_to_code_and_message(response) == (221, "Bye")


def test_get_response_message():
    response = '221 Bye\r\n'
    p = SmtpParser()
    assert p.get_response_message(response) == "Bye"


def test_last_response_code():
    response = '221 Bye\r\n'
    p = SmtpParser()
    p.response_to_code_and_message(response)
    assert p.get_last_response_code() == 221


def test_get_all_response_codes():
    p = SmtpParser()
    p.response_to_code_and_message('250 OK\r\n')
    p.response_to_code_and_message('221 Bye\r\n')
    assert p.get_all_response_codes() == [250, 221]


def test_get_response_code_no_code():
    response = b'Bye\r\n'
    p = SmtpParser()
    with pytest.raises(ValueError):
        p.get_response_code(response)


def test_get_meaning_of_250_code():
    assert SmtpParser.response_code_to_meaning(250) == "OK"
