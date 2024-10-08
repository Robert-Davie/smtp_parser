"""constants from RFC5321"""

response_codes = {
    211: "System Status",
    214: "Help",
    220: "Service Ready",
    221: "Service Closing",
    235: "Authorization Successful",
    250: "OK",
    251: "User Not Local",
    252: "Cannot Verify User But Will Attempt Delivery",
    334: "Authorization Security Mechanism Accepted",
    354: "Start Mail Input (End With <CLRF>.<CLRF>)",
    421: "Service Not Available - Closing Transmission Channel",
    422: "Action Not Taken: Recipient Has Insufficient Storage",
    431: "File Overload To Domain",
    441: "No Response From Recipient Server",
    442: "Connection Dropped",
    446: "Internal Loop Has Occurred",
    450: "Not OK, Action Not Taken",
    451: "Action Aborted: Local Error",
    452: "Action Not Taken: Insufficient Storage",
    454: "TLS Temporarily Unavailable",
    455: "Parameters Cannot Be Accommodated",
    471: "Mail Server Error Due To Spam Filter",
    500: "Syntax Error (Command Not Found)",
    501: "Syntax Error (Params/Args Not Found)",
    502: "Command Not Implemented",
    503: "Bad Command Sequence",
    504: "Command Param Not Implemented",
    510: "Invalid Email Address",
    512: "DNS Error",
    523: "Size Of Mail Exceeds Recipient Server Limit",
    530: "Authentication Problem Needing STARTTLS",
    535: "Authentication Failed",
    538: "Encryption Required",
    541: "Message Rejected By Spam Filter",
    550: "Action Not Taken: Mailbox Unavailable",
    551: "User Not Local - Please Try Forward",
    552: "Action Aborted: Exceeded Storage Allocation",
    553: "Action Not Taken: Mailbox Name Not Allowed",
    554: "Transaction Failed",
    555: "Parameters Not Recognized",
}


# SEND, SOML, SAML, RELAY, TURN and TLS are obsolete

# EXPN means Expand
# NOOP is used to prevent timeout and ensure connection still present

commands = (
    "HELO",
    "EHLO",
    "MAIL",
    "RCPT",
    "DATA",
    "RSET",
    "VRFY",
    "EXPN",
    "HELP",
    "NOOP",
    "QUIT",
    "AUTH",
    "STARTTLS",
)
