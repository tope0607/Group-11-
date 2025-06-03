# Automated Severe Weather Notifier

A Python Tkinter app that sends severe weather alerts via SMS and email based on user-input city, phone, and email.

## Features
- Fetches weather data from OpenWeatherMap API
- Sends notifications via SMS and email
- Simple GUI for user input and testing notifications
- Saves user info locally in users.json

## Setup
1. Install dependencies:
   ```bash
   pip install requests python-dotenv

2. Get an OpenWeatherMap API key from openweathermap.org.


3. For email alerts, use a Gmail account with 2-Step Verification enabled and generate an App Password.


4. Create a .env file with:

OPENWEATHER_API_KEY=your_api_key
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password


5. Run the app:

python main.py



Notes

Phone number must be in international format (e.g. +1234567890).

If you get Gmail authentication errors, check your App Password setup:
https://support.google.com/mail/?p=BadCredentials
## Contributors
Raeedah - https://github.com/Esme-raida

Agoro Temitope - https://github.com/tope0607

Abdullahi - https://github.com/Gurin885
