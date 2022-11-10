from smtplib import SMTP
from email.mime.text import MIMEText
import json
import os
import pika

def main() -> None:
    def callback(ch, method, properties, body) -> None:
        with SMTP(os.environ["SMTP_DOMAIN"], int(os.environ["SMTP_PORT"])) as server:
            server.starttls()

            server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            
            data = json.loads(body.decode())
            
            match data["type"]:
                case "register":
                    msg = MIMEText(data["msg"])
                    msg["Subject"]= "Confirm your email"
                    msg["From"]   = os.environ["SMTP_SENDER"]

                    print(f" [*] Sending register email to: {data['email']}")
                case "confirm":
                    msg = MIMEText(data["msg"])
                    msg["Subject"]= "Token"
                    msg["From"]   = os.environ["SMTP_SENDER"]

                    print(f" [*] Sending confirm email to: {data['email']}")
                case "delete":
                    msg = MIMEText(data["msg"])
                    msg["Subject"]= "Delete user"
                    msg["From"]   = os.environ["SMTP_SENDER"]

                    print(f" [*] Sending delete email to: {data['email']}")

            server.sendmail(os.environ["SMTP_SENDER"], data["email"], msg.as_string())

    credentials = pika.PlainCredentials(os.environ["PIKA_USER"], os.environ["PIKA_PASS"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ["PIKA_URL"], int(os.environ["PIKA_PORT"]), "/", credentials))
    channel = connection.channel()

    channel.queue_declare(queue="email")

    channel.basic_consume(queue="email", on_message_callback=callback, auto_ack=True)

    print(" [*] Waiting for messages.")
    
    channel.start_consuming()

if __name__ == "__main__":
    main()