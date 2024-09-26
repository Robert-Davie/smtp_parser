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
    assert p.responses == [250, 221]


def test_get_response_code_no_code():
    response = b'Bye\r\n'
    p = SmtpParser()
    with pytest.raises(ValueError):
        p.get_response_code(response)


def test_get_meaning_of_250_code():
    assert SmtpParser.response_code_to_meaning(250) == "OK"


def test_get_command_valid_command():
    p = SmtpParser()
    assert p.set_command("EHLO bar.com") == ("EHLO", "bar.com")


def test_get_command_invalid_command():
    p = SmtpParser()
    with pytest.raises(Exception):
        p.set_command("ZZZZ bar.com")


def test_get_mail_from():
    p = SmtpParser()
    p.get_reverse_path("MAIL FROM: < someone@gmail.com >")
    assert p.reverse_path == "someone@gmail.com"


def test_get_mail_from_alt_2():
    p = SmtpParser()
    p.get_reverse_path("MAIL FROM:<person@mail.com>")
    assert p.reverse_path == "person@mail.com"


def test_get_mail_from_alt_format():
    p = SmtpParser()
    p.get_reverse_path("MAIL FROM: <someone@cs.cf.ac.uk>.")
    assert p.reverse_path == "someone@cs.cf.ac.uk"


def test_220_response():
    p = SmtpParser()
    p.resolve_response("220 foo.com Simple Mail Transfer Service Ready")
    assert all([
        p.server == "foo.com",
        p.server_ready,
        p.responses == [220],
    ])


def test_221_response():
    p = SmtpParser()
    p.connection_active = True
    p.resolve_response("221 foo.com Service closing transmission channel")
    assert not p.connection_active


def test_set_client():
    p = SmtpParser()
    p.resolve_command("HELO client.example.com")
    assert p.client == "client.example.com"


def test_get_recipient():
    p = SmtpParser()
    p.resolve_command("RCPT TO:<person@mail.com>")
    assert p.recipients == ["person@mail.com"]


def test_bad_sequence_order():
    p = SmtpParser()
    p.resolve_response("220 server.example.com ESMTP")
    p.resolve_command("MAIL FROM:<person@mail.com>")
    p.resolve_response("503 5.5.2 Send hello first")
    assert all([
        p.server == "server.example.com",
        p.commands == ["MAIL"],
        p.responses == [220, 503],
        p.reverse_path == "",
    ])


def test_response_code_with_hyphen():
    p = SmtpParser()
    p.resolve_response("250-EXPN")
    assert p.responses == [250]


def test_get_ehlo_info():
    p = SmtpParser()
    p.resolve_command("EHLO server.example.com")
    p.resolve_response("250 - PIPELINING")
    p.resolve_response("250 - SIZE 10240000")
    p.resolve_response("250 - VRFY")
    assert p.ehlo_info == {
        "PIPELINING": None,
        "SIZE": ["10240000"],
        "VRFY": None,
    }


def test_ehlo_info_with_hyphen():
    p = SmtpParser()
    p.resolve_command("EHLO server.example.com")
    p.resolve_response("250-X-LINK2STATE")
    assert p.ehlo_info == {
        "X-LINK2STATE": None
    }


def test_too_many_recipients():
    p = SmtpParser()
    p.resolve_command("RCPT TO:<person1@mail.com>")
    p.resolve_response("250 OK")
    p.resolve_command("RCPT TO:<person2@mail.com>")
    p.resolve_response("452 4.5.3 Error: too many recipients")
    assert p.recipients == ["person1@mail.com"]
