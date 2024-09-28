# smtp_parser

## What is it?
This project contains a class to parse SMTP conversations into a convenient dictionary object.

## Background
SMTP is a mail protocol used to send mail from server to server and from user to server.

SMTP works by using a server-client model. The client connects to the appropriate port on the server to
form a connection. The server sends responses in the form of a response code and additional information
e.g. ```250 OK ```. Users communicate to the server by sending commands such as ```EHLO computer1.com```.

The typical SMTP conversation looks something like ```220, EHLO, 250, MAIL, 250, RCPT, 250, DATA, 354, message
, 250, QUIT, 221```.

## How to use the smtp_parser
The parser.py file contains a class ```SmtpParser``` which reads a single message (of either ```str``` or ```
bytes``` format) via the ```.read()``` method. To retrieve output use either the 
```.output()``` method to retrieve the resulting object, or ```.print()``` method to print the object nicely.

example usage
```
# example messages
message1 = "QUIT"
message2 = "221 Bye"

parser = SmtpParser()
parser.read(message1)
parser.read(message2)
parser.print()
```

result:
```
CONVERSATION
                      SEQUENCE [221, 'QUIT']
                      COMMANDS ['QUIT']
                     RESPONSES [221]
EMAIL INFO
         SENDER (REVERSE PATH) 
                    RECIPIENTS 
                          DATA 
              EMAIL QUEUE NAME 
CONNECTION ACTIVE False
                        SERVER 
                        CLIENT 
                  SERVER READY True
                   SERVER INFO {'commands': []}
              IS AUTHENTICATED False
                  IS ENCRYPTED False
      CURRENTLY ACCEPTING DATA False
                VRFY RESPONSES {}
                EXPN RESPONSES {}
```