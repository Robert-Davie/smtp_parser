"""the SmtpParser is the most important class for the project"""

from typing import Optional
from src.constants import commands
import warnings


class SmtpParser:
    def __init__(self):
        self.conversation_in_order: list = []  # N.B. responses may be received after other commands are given
        self.responses: list = []
        self.commands: list = []

        self.server: str = ""
        self.client: str = ""

        self.reverse_path: str = ""
        self.recipients: [str] = []
        self.data: [str] = []

        self.server_ready = False
        self.data_mode: bool = False
        self.connection_active: bool = False
        self.authenticated: bool = False
        self.encrypted: bool = False
        self.server_info: {str: Optional[list | int]} = {}  # contains estmp features
        self.vrfy: {str: str} = {}
        self.expn: {str: list} = {}
        self.email_queue_name: str = ""

        self.server_info["commands"] = []

    def output(self) -> dict:
        return {
            "CONVERSATION": {
                "SEQUENCE": self.conversation_in_order,
                "COMMANDS": self.commands,
                "RESPONSES": self.responses,
            },
            "EMAIL INFO": {
                "SENDER (REVERSE PATH)": self.reverse_path,
                "RECIPIENTS": self.recipients,
                "DATA": self.data,
                "EMAIL QUEUE NAME": self.email_queue_name,
            },
            "CONNECTION INFO": {
                "CONNECTION ACTIVE": self.connection_active,
                "SERVER": self.server,
                "CLIENT": self.client,
                "SERVER READY": self.server_ready,
                "SERVER INFO": self.server_info,  # used for checking EHLO response
                "IS AUTHENTICATED": self.authenticated,
                "IS ENCRYPTED": self.encrypted,
                "CURRENTLY ACCEPTING DATA": self.data_mode,
                "VRFY RESPONSES": self.vrfy,
                "EXPN RESPONSES": self.expn,
            },
        }

    def __str__(self) -> [str]:
        return str(self.output())

    def print(self) -> None:
        for key1, value1 in self.output().items():
            print(key1)
            for key2, value2 in value1.items():
                print(key2.rjust(30), value2)

    def read(self, message: str | bytes):
        if type(message) is bytes:
            message = message.decode("utf-8")
        message = str(message)
        if message[0] == "b":
            message = message[1:]
        if message[-4:].upper() == "R\\N'":
            message = message[:-4]
        message = message.strip("'\\")
        first_word = message.split()[0][:3]
        for letter in first_word:
            if letter not in "0123456789":
                if self.data_mode:
                    return self.resolve_data(message)
                return self.resolve_command(message)
        return self.resolve_response(message)

    def set_command(self, message: str | bytes) -> (str, str):
        if type(message) is bytes:
            message = message.decode("utf-8")
        message = message.strip("'")
        command = message.split()[0].upper()
        if command not in commands:
            warnings.warn(f"Command {command} Not Valid", UserWarning)
        self.current_command = command
        self.commands.append(command)
        self.conversation_in_order.append(command)
        return command, message[len(command) :].strip()

    def get_reverse_path(self, message: str) -> None:
        start = message.index("<") + 1
        end = message.index(">")
        self.reverse_path = message[start:end].strip()

    def get_recipient(self, message: str) -> None:
        start = message.index("<") + 1
        end = message.index(">")
        self.recipients.append(message[start:end].strip())

    def resolve_data(self, message: str | bytes):
        if type(message) is bytes:
            message = message.decode("utf-8")
        if self.data_mode:
            if message == ".":
                self.data_mode = False
            else:
                self.data.append(message)

    def resolve_command(self, response: str | bytes):
        command, remainder = self.set_command(response)
        match command:
            case "HELO":
                if len(remainder) > 0:
                    self.client = remainder.split()[0]
            case "EHLO":
                if len(remainder) > 0:
                    self.client = remainder.split()[0]
            case "MAIL":
                try:
                    self.get_reverse_path(remainder)
                except ValueError:
                    self.reverse_path = "PATH NOT FOUND"
                    warnings.warn(
                        "mail address not in correct format, missing '<' and '>'"
                    )
            case "RCPT":
                self.get_recipient(remainder)
            case "DATA":
                pass
            case "RSET":
                pass
            case "VRFY":
                pass
            case "EXPN":
                pass
            case "HELP":
                pass
            case "NOOP":
                pass
            case "QUIT":
                pass
            case "AUTH":
                pass
            case _ as unknown_command:
                warnings.warn(
                    f"command {unknown_command} not currently supported by this parser",
                    UserWarning,
                )

    def resolve_response(self, response: str | bytes):
        response_code, remainder = self.response_to_code_and_message(response)
        last_command = self.last_command()

        if response_code // 100 in {4, 5}:
            match self.commands[-1]:
                case "RCPT":
                    self.recipients.pop()
                case "MAIL":
                    self.reverse_path = ""
        elif response_code != 221:
            self.connection_active = True
            self.server_ready = True

        match response_code:
            case 214:
                self.server_info["commands"].extend(
                    remainder.strip(" -").upper().split()
                )
            case 220:
                self.server = remainder.split()[0]
                self.server_ready = True
            case 221:
                self.connection_active = False
            case 235:
                self.authenticated = True
            case 250:
                if last_command == "EHLO":
                    remainder = remainder.strip("-").split()
                    if len(remainder) == 1:
                        self.server_info[remainder[0]] = None
                    elif len(remainder) > 1:
                        self.server_info[remainder[0]] = remainder[1:]
                if last_command == "RSET":
                    self.recipients = []
                    self.reverse_path = ""
                    self.data = []
                    self.data_mode = False
                    self.encrypted = False
                    self.authenticated = False
                if last_command == "DATA":
                    self.data_mode = False
                    self.email_queue_name = remainder[
                        remainder.find("queued as ") + 10 :
                    ].split()[0]
                    if len(self.data) == 1:
                        self.data = self.data[0].split("\\r\\n")
            case 354:
                self.data_mode = True
            case 451:
                self.connection_active = False
            case 452:
                pass
            case 550:
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
        if type(message) is bytes:
            message = message.decode("utf-8")
        message = message.strip("'")
        try:
            response_code = int(message[:3])
            response_message = message[3:].strip()
            self.responses.append(response_code)
            self.conversation_in_order.append(response_code)
            return response_code, response_message
        except ValueError:
            raise
