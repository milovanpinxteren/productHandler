import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def send_email(self, beers_df):
        csv_filename = 'importbestand_producten_microcash.txt'
        beers_df.to_csv(csv_filename, index=False, sep='\t')
        sender_email = 'info@ristaiuto.it'
        reciever_email = 'info@gerijptebieren.nl'

        # Create a MIMEText object for the email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = reciever_email
        message['Subject'] = 'Bestand voor Microcash import'

        # Attach the email content (text)
        message.attach(MIMEText('zie bijlage', 'plain'))

        with open(csv_filename, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % csv_filename)
            message.attach(part)


        # SMTP server configuration (for Gmail)
        smtp_server = 'smtp.hostinger.com'
        smtp_port = 587  # Port for TLS
        smtp_username = 'info@ristaiuto.it'
        smtp_password = 'Afbhsghkjl562!'

        # Create an SMTP server connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, reciever_email, message.as_string())

        # Close the SMTP server
        server.quit()

        print('Email sent successfully')