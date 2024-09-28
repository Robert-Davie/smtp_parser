"""client.py is used for testing parser functionality with a MailHog server"""

from modified_smtplib import RememberSMTP
from src import parser


server = RememberSMTP("localhost", port=1025)
server.set_debuglevel(1)

# pretend conversation

server.connect(port=1025)
server.ehlo_or_helo_if_needed()
server.verify("robert")
server.rset()
server.ehlo("robert.example.com")
server.help()
server.docmd("NOOP")
server.docmd("mail robert")
server.noop()
server.login("robert", "123")  # pretend server authenticates anything
server.rset()
server.mail("robert@example.co.uk")
server.rcpt("person1@example.co.uk")
server.rcpt("person2@example.co.uk")
server.rcpt("person3@example.co.uk")
server.data("Subject: Hello\n" "Hello\n" "How are you?\n" "From Robert\n")
server.quit()


outcome = server.output
print("*" * 80)
my_parser = parser.SmtpParser()
for message in outcome:
    my_parser.read(message[1])
my_parser.print()

# output should look like this and raise one warning (due to testing intentionally bad mail command) with email queue
# name being different each time program is run

# CONVERSATION
#                       SEQUENCE [220, 'EHLO', 250, 250, 250, 'VRFY', 500, 'RSET', 250, 'EHLO', 250, 250, 250, 'HELP',
#                       500, 'NOOP', 250, 'MAIL', 550, 'NOOP', 250, 'AUTH', 235, 'RSET', 250, 'MAIL', 250, 'RCPT', 250,
#                       'RCPT', 250, 'RCPT', 250, 'DATA', 354, 250, 'QUIT', 221]
#                       COMMANDS ['EHLO', 'VRFY', 'RSET', 'EHLO', 'HELP', 'NOOP', 'MAIL', 'NOOP', 'AUTH', 'RSET',
#                       'MAIL', 'RCPT', 'RCPT', 'RCPT', 'DATA', 'QUIT']
#                      RESPONSES [220, 250, 250, 250, 500, 250, 250, 250, 250, 500, 250, 550, 250, 235, 250, 250, 250,
#                      250, 250, 354, 250, 221]
# EMAIL INFO
#          SENDER (REVERSE PATH) robert@example.co.uk
#                     RECIPIENTS ['person1@example.co.uk', 'person2@example.co.uk', 'person3@example.co.uk']
#                           DATA ['Subject: Hello', 'Hello', 'How are you?', 'From Robert', '.']
#               EMAIL QUEUE NAME
# CONNECTION INFO
#              CONNECTION ACTIVE False
#                         SERVER mailhog.example
#                         CLIENT robert.example.com
#                   SERVER READY True
#                    SERVER INFO {'commands': [], 'Hello': ['robert.example.com'], 'PIPELINING': None,
#                    'AUTH': ['PLAIN']}
#               IS AUTHENTICATED False
#                   IS ENCRYPTED False
#       CURRENTLY ACCEPTING DATA False
#                 VRFY RESPONSES {}
#                 EXPN RESPONSES {}
