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


def test_get_all_response_codes():
    p = SmtpParser()
    p.response_to_code_and_message('250 OK\r\n')
    p.response_to_code_and_message('221 Bye\r\n')
    assert p.response_codes == [250, 221]


def test_get_response_code_no_code():
    response = b'Bye\r\n'
    p = SmtpParser()
    with pytest.raises(ValueError):
        p.get_response_code(response)


def test_get_meaning_of_250_code():
    assert SmtpParser.response_code_to_meaning(250) == "OK"


def test_get_command_valid_command():
    p = SmtpParser()
    assert p.set_command("EHLO bar.com") == "EHLO"


def test_get_command_invalid_command():
    p = SmtpParser()
    with pytest.raises(Exception):
        p.set_command("ZZZZ bar.com")


def test_get_mail_from():
    p = SmtpParser()
    p.set_mail_from("MAIL FROM: < someone@gmail.com >")
    assert p.mail_from == "someone@gmail.com"


def test_get_mail_from_alt_format():
    p = SmtpParser()
    p.set_mail_from("MAIL FROM: <someone@cs.cf.ac.uk>.")
    assert p.mail_from == "someone@cs.cf.ac.uk"


def test_220_response():
    p = SmtpParser()
    p.resolve_response("220 foo.com Simple Mail Transfer Service Ready")
    assert all([
        p.server == "foo.com",
        p.server_ready,
        p.response_codes == [220],
    ])


def test_221_response():
    p = SmtpParser()
    p.connection_active = True
    p.resolve_response("221 foo.com Service closing transmission channel")
    assert not p.connection_active
