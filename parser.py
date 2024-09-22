from constants import response_codes, commands


class SmtpParser:
    def __init__(self):
        self.response_codes = []

    def get_response_code(self, response: str | bytes, save=True) -> int:
        response_code, _ = self.response_to_code_and_message(response, save)
        return response_code

    def get_response_message(self, response: str | bytes, save=True) -> int:
        _, response_message = self.response_to_code_and_message(response, save)
        return response_message

    def response_to_code_and_message(self, message: str | bytes, save=True) -> (int, str):
        if type(message) == bytes:
            message = message.decode("utf-8")
        try:
            response_code = int(message[:3])
            response_message = message[3:].strip()
            if save:
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

    def get_all_response_codes(self) -> list[int]:
        return self.response_codes

    def get_last_response_code(self) -> int:
        return self.response_codes[-1]
