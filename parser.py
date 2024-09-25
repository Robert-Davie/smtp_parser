from typing import Optional

from constants import response_codes, commands


class SmtpParser:
    def __init__(self):
        self.response_codes: list = []
        self.commands_given: list = []
        self.server: str = ""
        self.client: str = ""
        self.mail_from: str = ""
        self.recipients: [str] = []
        self.data = [str]
        self.server_ready: bool = False
        self.connection_active: bool = False
        self.authenticated: bool = False
        self.encrypted: bool = False
        self.max_size: Optional[bool] = None
        self.vrfy: {str: str} = {}
        self.expn: {str: list} = {}
        self.speaking: Optional[str] = None
        self.current_command = ""
        self.current_arguments: [str] = []
        self.save = True

    def set_command(self, message: str | bytes) -> str:
        if type(message) == bytes:
            message = message.decode("utf-8")
        command = message.split()[0].upper()
        if command in commands:
            if self.save:
                self.current_command = command
                self.commands_given.append(command)
            return command
        else:
            raise Exception(f"Command {command} Not Valid")

    def set_mail_from(self, message: str) -> None:
        elements = message.split()
        if elements[2] == "<":
            mail_from = elements[3]
        else:
            mail_from = elements[2].strip("<>.")
        assert "@" in mail_from
        self.mail_from = mail_from

    def set_save(self, save: bool) -> None:
        self.save = save

    def resolve_response(self, response: str | bytes):
        response_code, response_message = self.response_to_code_and_message(response)
        match response_code:
            case 220:
                self.server = response_message.split()[0]
                self.server_ready = True
            case 221:
                self.connection_active = False
            case _:
                pass

    def get_response_code(self, response: str | bytes) -> int:
        response_code, _ = self.response_to_code_and_message(response)
        return response_code

    def get_response_message(self, response: str | bytes) -> int:
        _, response_message = self.response_to_code_and_message(response)
        return response_message

    def response_to_code_and_message(self, message: str | bytes) -> (int, str):
        if type(message) == bytes:
            message = message.decode("utf-8")
        try:
            response_code = int(message[:3])
            response_message = message[3:].strip()
            if self.save:
                self.response_codes.append(response_code)
            return response_code, response_message
        except ValueError:
            raise

    @staticmethod
    def response_code_to_meaning(code: int) -> str:
        try:
            return response_codes[code]
        except KeyError:
            raise
