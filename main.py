# This file will be called by Windows Task Scheduler every 30 minutes

# Import required modules and classes
from weather_api import WeatherService  # Import the weather service class for weather data
from send_alert import AlertSender  # Import the alert sender class for notifications
import os  # Import os module for environment variables
import json  # Import json module for handling JSON data
import datetime  # Import datetime for time-based checks
from dotenv import load_dotenv  # Import function to load environment variables


def load_users_data():
    """
    Load user data from users.json file
    Returns a dictionary containing user information or empty dict if error occurs
    """
    try:
        # Open and read the users.json file
        with open("users.json") as user_info:
            # Convert JSON data to Python dictionary
            data = json.load(user_info)
        return data
    except Exception as e:
        # Print error message if file reading fails
        print(f"Error loading user data JSON: {e}")
        return {}


def run_scheduled_check():
    """Main function that runs every 30 minutes to check weather conditions"""
    # Load environment variables from .env file
    load_dotenv()

    # Get the OpenWeather API key from environment variables
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    # Check if API key exists, exit if missing
    if not API_KEY:
        print("API key missing. Please check your .env file.")
        return

    # Check if it's 5 AM hour (between 5:00 and 5:59)
# Check if it's between 5:00 and 5:30 AM
    now = datetime.datetime.now()
    check_future_weather = (now.hour == 5 and now.minute <= 30)

    try:
        # Load all user data from JSON file
        all_user_data = load_users_data()

        # Process each user's data
        for user_data in all_user_data:
            # Extract user's city, phone, and email from their data
            CITY = user_data.get("city", "YourCity")  # Default to 'YourCity' if not specified
            PHONE = user_data.get("phone", "+1234567890")  # Default phone if not specified
            EMAIL = user_data.get("email", "your@email.com")  # Default email if not specified

            try:
                # Initialize weather service and alert sender
                weather_service = WeatherService(API_KEY)
                alert_sender = AlertSender()

                # Get latitude and longitude for the user's city
                lat, lon = weather_service.get_coordinates(CITY)
                if not lat or not lon:
                    print(f"[ERROR] Could not retrieve coordinates for {CITY}")
                    continue

                # Fetch current weather data using coordinates
                raw_data = weather_service.fetch_weather_data(lat, lon)
                if not raw_data:
                    print("[ERROR] Weather data fetch failed.")
                    continue

                # Extract relevant weather information from raw data
                relevant_data = weather_service.extract_relevant_data(raw_data)
                if not relevant_data:
                    print("[ERROR] Weather data extraction failed.")
                    continue

                # Check current weather conditions
                current = relevant_data["current"]

                # Check if current weather is severe
                is_severe, category = weather_service.check_severity(current["id"])
                if is_severe:
                    # Create alert message for severe current weather
                    message = f"Severe weather alert for {CITY}!\nType: {category}\nCondition: {current['description']}"
                    # Send alert via phone and email
                    method, response = alert_sender.send_alert(PHONE, EMAIL, message)
                    print(f"[ALERT SENT via {method}]: {response}")
                    continue

                # Check weather forecast for next 12 hours ONLY if it's 5 AM
                if check_future_weather:
                    for hour in relevant_data["next_12_hours"]:
                        # Check if forecasted weather is severe
                        is_severe, category = weather_service.check_severity(hour["id"])
                        if is_severe:
                            # Create alert message for severe forecasted weather
                            message = (
                                f"Severe weather expected in the next 12 hours for {CITY}!\nType:"
                                f"{category}\nCondition: {hour['description']}"
                            )
                            # Send alert via phone and email
                            method, response = alert_sender.send_alert(PHONE, EMAIL, message)
                            print(f"[FUTURE ALERT SENT via {method}]: {response}")
                else:
                    print(f"Skipping 12-hour forecast check at {now}")
                    break

                # Print message if no severe weather is detected
                print(f"[INFO] No severe weather detected for {CITY}")

            except Exception as e:
                # Handle any errors during weather checking process
                print(f"[ERROR] Error in scheduled check: {str(e)}")
                continue

    except Exception as e:
        # Handle any errors during user data processing
        print(f"Error loading or processing user data: {e}")


# Run the main function when script is executed directly
if __name__ == "__main__":
    run_scheduled_check()