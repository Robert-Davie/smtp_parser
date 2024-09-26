from typing import Optional
from constants import response_codes, commands

class SmtpParser:
    def __init__(self):
        self.responses: list = []
        self.commands: list = []

        self.server: str = ""
        self.client: str = ""

        self.reverse_path: str = ""
        self.recipients: [str] = []
        self.data = [str]

        self.connection_active: bool = False
        self.authenticated: bool = False
        self.encrypted: bool = False
        self.ehlo_info: {str: Optional[list | int]} = {}
        self.vrfy: {str: str} = {}
        self.expn: {str: list} = {}
        self.email_queue_name: str = ""

    def set_command(self, message: str | bytes) -> (str, str):
        if type(message) == bytes:
            message = message.decode("utf-8")
        command = message.split()[0].upper()
        if command in commands:
            self.current_command = command
            self.commands.append(command)
            return command, message[len(command):].strip()
        else:
            raise Exception(f"Command {command} Not Valid")

    def get_reverse_path(self, message: str) -> None:
        start = message.index("<") + 1
        end = message.index(">")
        self.reverse_path = message[start:end].strip()

    def get_recipient(self, message: str) -> None:
        start = message.index("<") + 1
        end = message.index(">")
        self.recipients.append(message[start:end].strip())

    def resolve_command(self, response: str | bytes):
        command, remainder = self.set_command(response)
        match command:
            case "HELO":
                self.client = remainder.split()[0]
            case "MAIL":
                self.get_reverse_path(remainder)
            case "RCPT":
                self.get_recipient(remainder)
            case "NOOP":
                pass
            case "QUIT":
                pass

    def resolve_response(self, response: str | bytes):
        response_code, remainder = self.response_to_code_and_message(response)
        last_command = self.last_command()

        if response_code // 100 == 5:
            match self.commands[-1]:
                case "MAIL":
                    self.reverse_path = ""
        match response_code:
            case 220:
                self.server = remainder.split()[0]
                self.server_ready = True
            case 221:
                self.connection_active = False
            case 250:
                if last_command == "EHLO":
                    remainder = remainder.strip("-").split()
                    if len(remainder) == 1:
                        self.ehlo_info[remainder[0]] = None
                    elif len(remainder) > 1:
                        self.ehlo_info[remainder[0]] = remainder[1:]
            case 354:
                pass
            case 452:
                if last_command == "RCPT":
                    self.recipients.pop()
            case _:
                pass

    def last_command(self) -> Optional[str]:
        if len(self.commands) > 0:
            return self.commands[-1]
        else:
            return None

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
            self.responses.append(response_code)
            return response_code, response_message
        except ValueError:
            raise

    @staticmethod
    def response_code_to_meaning(code: int) -> str:
        try:
            return response_codes[code]
        except KeyError:
            raise
