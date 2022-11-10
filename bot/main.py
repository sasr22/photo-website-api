import base64
import json
import os
from time import sleep
from io import BytesIO
from PIL import Image
import pika
from selenium import webdriver
from selenium.webdriver.common.by import By
import minio
import psycopg

def main() -> None:
    s3_client = minio.Minio(
        endpoint=os.environ["S3_ENDPOINT"],
        access_key=os.environ["S3_ACCESS_KEY"],
        secret_key=os.environ["S3_SECRET_KEY"],
        secure=os.environ["S3_SECURE"] == "TRUE"
    )

    db = psycopg.connect(os.environ["DB_URI"])

    options = webdriver.FirefoxOptions()

    options.add_argument("--headless")

    browser = webdriver.Firefox(options=options)

    def callback(ch, method, properties, body) -> None:
        data = json.loads(body.decode())

        print(f" [*] Visiting: {data['url']}")
        
        browser.get(data["url"])

        sleep(data["timeout"])

        el = browser.find_element(By.TAG_NAME, "body")

        image = Image.open(BytesIO(base64.b64decode(el.screenshot_as_base64))).convert("RGB")
            
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format=data["format"])
        img_byte_arr.seek(0)

        match data["format"]:
            case "png":
                mimetype = "image/png"
            case "jpg":
                mimetype = "image/jpeg"
            case "webp":
                mimetype = "image/webp"

        s3_client.put_object(os.environ["S3_BUCKET"], f"{data['api_uuid']}/{data['uuid']}.{data['format']}", img_byte_arr, len(img_byte_arr.getvalue()), mimetype)

        db.cursor().execute("INSERT INTO images VALUES(%s, %s, %s, %s)", (data["uuid"], data["api_uuid"], f"{data['api_uuid']}/{data['uuid']}.{data['format']}", mimetype,))

        db.commit()

    credentials = pika.PlainCredentials(os.environ["PIKA_USER"], os.environ["PIKA_PASS"])
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ["PIKA_URL"], int(os.environ["PIKA_PORT"]), "/", credentials))
    channel = connection.channel()

    channel.queue_declare(queue="photo")

    channel.basic_consume(queue="photo", on_message_callback=callback, auto_ack=True)

    print(" [*] Waiting for messages.")
    
    channel.start_consuming()    

    browser.close()

    db.close()

if __name__ == "__main__":
    main()