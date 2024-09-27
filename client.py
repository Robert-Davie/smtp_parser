import smtplib

server = smtplib.SMTP("localhost", port=1025)
server.set_debuglevel(1)
# server.sendmail("sender_x", "recipient_y", "a pretend email")
server.helo("robert.com")
