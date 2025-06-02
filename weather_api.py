# Import required libraries
import requests  # For making HTTP requests to weather API
import datetime  # For handling dates and times
import time  # For adding delays and time-based operations
import os  # For accessing environment variables
from dotenv import load_dotenv  # For loading API keys from .env file

# Load environment variables from .env file
load_dotenv()


class WeatherService:
    """
    A class that handles all weather-related operations including:
    - Getting city coordinates
    - Fetching weather data
    - Checking for severe weather conditions
    """

    def __init__(self, api_key: str):
        # Store API key and set up API endpoints
        self.api_key = api_key
        self.geo_api_url = "http://api.openweathermap.org/geo/1.0/direct"  # URL for getting city coordinates
        self.onecall_api_url = "https://api.openweathermap.org/data/3.0/onecall"  # URL for getting weather data

    def _make_api_request(self, url, params):
        """Private method to make API requests with error handling, exceptions like httpError, ConnectionError etc."""
        try:
            # Make GET request to the API
            response = requests.get(url, params=params)
            # Raise exception for bad status codes
            response.raise_for_status()
            # Convert response to JSON
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None
        except ValueError as e:
            print(f"JSON decode error: {e}")
            return None

    def get_coordinates(self, city_name):
        """This method takes city name and returns the latitude and longitude using the geocoding API"""
        # Set up parameters for the geocoding API request
        params = {
            "q": city_name,  # This is the query string, so it automatically passes in the city name
            # such as after the geo url an equal sign is passed like this ={city_name}&limit
            "limit": 1,
            "appid": self.api_key
        }
        # Make API request and extract coordinates
        data = self._make_api_request(self.geo_api_url, params)
        return (data[0]["lat"], data[0]["lon"]) if data else (None, None)

    def fetch_weather_data(self, latitude, longitude):
        """This is a method that takes the data lat and lon as arguments and passes it into latitude and longitude and uses this to
        fetch raw weather data from the One call API for the given coordinates."""
        # Set up parameters for the weather API request
        params = {
            "lat": latitude,  # Latitude coordinate
            "lon": longitude,  # Longitude coordinate
            "appid": self.api_key,  # API key for authentication
            "units": "metric",  # Use metric units (Celsius, meters)
            "exclude": "minutely",  # Don't include minute-by-minute data
        }
        return self._make_api_request(self.onecall_api_url, params)

    def extract_relevant_data(self, raw_data):
        """Extracts the relevant weather details for current weather and for the next 12 hours.
        It returns a dictionary with the weather condition IDs and descriptions."""
        try:
            # Get current weather conditions
            current = raw_data["current"]["weather"][0]
            # Get weather forecast for next 12 hours
            next_12_hours = [hour["weather"][0] for hour in raw_data["hourly"][:12]]
            return {
                "current": current,
                "next_12_hours": next_12_hours,
            }
        except (KeyError, IndexError) as e:
            print(f"Error extracting weather data: {e}")
            return None

    def check_severity(self, weather_id):
        """Check if weather condition is severe
         Severe weather categories samples
         self.severe_weather_categories = {
             (200 - 232): "Thunderstorm",
             (500 - 531): "Heavy Rain",
             (600 - 622): "Snow",
             (700 - 781): "Atmospheric Hazard",
            (900 - 906): "Extreme Weather",  Additional extreme conditions
             (957 - 962): "Strong Winds"  High wind conditions
         }"""
        try:
            # Convert weather ID to integer
            id_code = int(weather_id)
            # Check weather ID against known severe weather ranges
            if 200 <= id_code <= 232:
                return True, "Thunderstorm"
            elif 500 <= id_code <= 531:
                return True, "Rain"
            elif 600 <= id_code <= 622:
                return True, "Snow"
            elif 700 <= id_code <= 781:
                return True, "Atmospheric Condition"
            elif 900 <= id_code <= 906:
                return True, "Extreme Weather"
            return False, "Clear or Mild"
        except (ValueError, TypeError):
            return False, "Unknown"

    def check_weather(self, city_name, check_future=True):
        """Check current and future weather conditions, now using all the methods created so far"""
        # Get city coordinates
        lat, lon = self.get_coordinates(city_name)
        if not lat or not lon:
            print("Could not get coordinates")
            return

        # Get weather data
        raw_data = self.fetch_weather_data(lat, lon)
        if not raw_data:
            print("Could not fetch weather data")
            return

        # Extract relevant weather information
        relevant_data = self.extract_relevant_data(raw_data)
        if not relevant_data:
            print("Could not extract weather data")
            return

        # Check current weather conditions
        current = relevant_data["current"]
        is_severe, category = self.check_severity(current["id"])
        if is_severe:
            print(f"Severe weather alert for {city_name}! ({category} - {current['description']})")
            return

        # Check future weather if requested
        if check_future:
            for hour in relevant_data["next_12_hours"]:
                is_severe, category = self.check_severity(hour["id"])
                if is_severe:
                    print(f"Severe weather expected in next 12 hours for {city_name}! ({category} - {hour['description']})")
                    return

        # Print status if no severe weather found
        print(f"No severe weather detected for {city_name} at {datetime.datetime.now()}")


# Only run this code if the file is executed directly (not imported)
if __name__ == "__main__":
    # Get API key from environment variables
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not API_KEY:
        print("Error: Please set OPENWEATHER_API_KEY in your .env file")
        exit()

    # Set default city and start monitoring
    CITY_NAME = "Abuja"
    weather_service = WeatherService(API_KEY)
    weather_service.check_weather(CITY_NAME)