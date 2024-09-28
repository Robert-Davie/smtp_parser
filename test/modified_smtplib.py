"""modified version of the smtplib provided in the standard library so output can be stored for the parser in
client.py"""

import re
from smtplib import (
    SMTP,
    SMTPServerDisconnected,
    SMTPResponseException,
    SMTPDataError,
    bCRLF,
    CRLF,
)
import socket
import sys


_MAXLINE: int = 8192


def _quote_periods(bindata):
    return re.sub(rb"(?m)^\.", b"..", bindata)


def _fix_eols(data):
    return re.sub(r"(?:\r\n|\n|\r(?!\n))", CRLF, data)


class RememberSMTP(SMTP):
    output = []

    def _print_debug(self, *args):
        """modified from parent class so output can be stored"""
        self.output.append(args)

    def getreply(self):
        """modified from parent class so does not print message"""
        resp = []
        if self.file is None:
            self.file = self.sock.makefile("rb")
        while 1:
            try:
                line = self.file.readline(_MAXLINE + 1)
            except OSError as e:
                self.close()
                raise SMTPServerDisconnected(
                    "Connection unexpectedly closed: " + str(e)
                )
            if not line:
                self.close()
                raise SMTPServerDisconnected("Connection unexpectedly closed")
            if self.debuglevel > 0:
                self._print_debug("reply:", repr(line))
            if len(line) > _MAXLINE:
                self.close()
                raise SMTPResponseException(500, "Line too long.")
            resp.append(line[4:].strip(b" \t\r\n"))
            code = line[:3]
            # Check that the error code is syntactically correct.
            # Don't attempt to read a continuation line if it is broken.
            try:
                errcode = int(code)
            except ValueError:
                errcode = -1
                break
            # Check if multiline response.
            if line[3:4] != b"-":
                break

        errmsg = b"\n".join(resp)
        return errcode, errmsg

    def connect(self, host="localhost", port=0, source_address=None):
        """modified version of connect method to remove stating connection"""

        if source_address:
            self.source_address = source_address

        if not port and (host.find(":") == host.rfind(":")):
            i = host.rfind(":")
            if i >= 0:
                host, port = host[:i], host[i + 1 :]
                try:
                    port = int(port)
                except ValueError:
                    raise OSError("nonnumeric port")
        if not port:
            port = self.default_port
        sys.audit("smtplib.connect", self, host, port)
        self.sock = self._get_socket(host, port, self.timeout)
        self.file = None
        (code, msg) = self.getreply()
        return (code, msg)

    def _get_socket(self, host, port, timeout):
        """modified to remove the call to print debug"""

        if timeout is not None and not timeout:
            raise ValueError("Non-blocking socket (timeout=0) is not supported")
        return socket.create_connection((host, port), timeout, self.source_address)

    def data(self, msg):
        """again remove print debug statement from original method"""
        self.putcmd("data")
        (code, repl) = self.getreply()
        if code != 354:
            raise SMTPDataError(code, repl)
        else:
            if isinstance(msg, str):
                msg = _fix_eols(msg).encode("ascii")
            q = _quote_periods(msg)
            if q[-2:] != bCRLF:
                q = q + bCRLF
            q = q + b"." + bCRLF
            self.send(q)
            (code, msg) = self.getreply()
            return (code, msg)
