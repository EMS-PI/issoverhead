import requests
import datetime as dt
import smtplib
from email.message import EmailMessage
import os
import ast

MY_LATITUDE = float(os.environ.get("MY_LATITUDE"))
MY_LONGITUDE = float(os.environ.get("MY_LONGITUDE"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
VERBOSE = ast.literal_eval(os.environ.get("VERBOSE"))
DEBUG = ast.literal_eval(os.environ.get("DEBUG"))
PORT = 587


def iss_position():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    print(data)

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    timestamp = dt.datetime.fromtimestamp(data["timestamp"])

    return iss_latitude, iss_longitude, timestamp


def is_night_time():
    parameters = {
        "lat": MY_LATITUDE,
        "lng": MY_LONGITUDE,
        "formatted": 0
    }
    response = requests.get(url="https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    if VERBOSE:
        print(response.json())
    response_json = response.json()
    sunrise_str = response_json["results"]["sunrise"].split("T")[1].split(":")
    sunrise = dt.time(hour=int(sunrise_str[0]), minute=int(sunrise_str[1]))
    sunset_str = response_json["results"]["sunset"].split("T")[1].split(":")
    sunset = dt.time(hour=int(sunset_str[0]), minute=int(sunset_str[1]))

    now = dt.datetime.utcnow()
    now_time = dt.time(hour=now.hour, minute=now.minute)

    return sunrise < now_time < sunset


def send_email():
    email_body = f"ISS is overhead. Go Out! ({iss_pos[2]})"
    email_msg = EmailMessage()
    email_msg.set_content(email_body)
    email_msg['Subject'] = "ISS is here!"
    email_msg['From'] = SENDER_EMAIL
    email_msg['To'] = RECIPIENT_EMAIL
    email_msg['Bcc'] = SENDER_EMAIL

    with smtplib.SMTP(host=SMTP_SERVER, port=PORT) as connection:
        connection.starttls()
        connection.login(user=SENDER_EMAIL, password=SENDER_PASSWORD)
        connection.send_message(msg=email_msg)


iss_pos = iss_position()
if VERBOSE:
    print(iss_pos)
    print(abs(iss_pos[0] - MY_LATITUDE))
    print(abs(iss_pos[1] - MY_LONGITUDE))

if (abs(iss_pos[0] - MY_LATITUDE) < 5 and abs(iss_pos[1] - MY_LONGITUDE) < 5) or DEBUG:
    if is_night_time() or DEBUG:
        if VERBOSE:
            print(f"ISS is here. Go out! ({iss_pos[2]})")
        send_email()
    else:
        if VERBOSE:
            print("It is daytime. Cannot see ISS.")
else:
    if VERBOSE:
        print(f"ISS is {abs(iss_pos[0] - MY_LATITUDE)} latitudes and "
              f"{abs(iss_pos[1] - MY_LONGITUDE)} longitudes away\n"
              f"({iss_pos[2]})")
