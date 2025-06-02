# Import required libraries
from tkinter import *  # Import all tkinter components for GUI creation
from tkinter import messagebox  # Import messagebox for showing popup messages
import json  # Import json for handling JSON data
import re  # Import re for regular expression operations
from weather_api import WeatherService  # Import custom weather service class
from send_alert import AlertSender  # Import custom alert sender class
import os  # Import os for file and environment operations
from dotenv import load_dotenv  # Import load_dotenv for loading environment variables

# Load environment variables from .env file
load_dotenv()


class WeatherNotifierGUI:
    def __init__(self):
        """
        Initializes the Weather Notifier GUI, sets up the main window, and initializes
        weather and alert services.
        """
        # Create and configure main window
        self.window = Tk()  # Create the main window
        self.window.title("Automated severe weather condition notifier")  # Set window title
        self.window.config(padx=20, pady=20)  # Add padding around the window edges
        self.window.geometry("700x200")  # Set window size to 700x200 pixels

        # Initialize services for weather data and alerts
        self.weather_service = WeatherService(os.getenv('OPENWEATHER_API_KEY'))  # Create weather service instance
        self.alert_sender = AlertSender()  # Create alert sender instance

        # Make the window responsive
        self.window.columnconfigure(1, weight=1)

        # Initialize GUI elements
        self.create_labels()  # Create all labels
        self.create_entries()  # Create all input fields
        self.create_button()  # Create all buttons

    def create_labels(self):
        """Create and position all labels in the GUI"""
        # Create and position city label
        self.city_label = Label(self.window, text="City name:")
        self.city_label.grid(column=0, row=0, sticky=W, padx=10, pady=10)

        # Create and position phone number label
        self.phone_number_label = Label(self.window, text="Phone number:")
        self.phone_number_label.grid(column=0, row=1, sticky=W, padx=10, pady=10)

        # Create and position email label
        self.email_label = Label(self.window, text="Email:")
        self.email_label.grid(column=0, row=2, sticky=W, padx=10, pady=10)

    def create_entries(self):
        """Create and position all input fields in the GUI"""
        # Create and position city input field
        self.city_entry = Entry(self.window, width=80)
        self.city_entry.grid(column=1, row=0, sticky="ew", padx=10, pady=10)
        self.city_entry.focus()  # Set focus to city entry by default

        # Create and position phone number input field
        self.phone_number_entry = Entry(self.window, width=80)
        self.phone_number_entry.grid(column=1, row=1, sticky="ew", padx=10, pady=10)

        # Create and position email input field
        self.email_entry = Entry(self.window, width=80)
        self.email_entry.grid(column=1, row=2, sticky="ew", padx=10, pady=10)

    def create_button(self):
        """Create and place the buttons for testing notification and saving user data"""
        # Test Notification Button
        self.testing_button = Button(
            self.window, 
            text="Test notification", 
            bg="light green", 
            command=self.test_notification
        )
        self.testing_button.grid(column=0, row=4, sticky="ew", padx=10, pady=10)

        # Save user data button
        self.save_button = Button(
            self.window,
            text="Save user data",
            bg="light blue",
            command=self.save_button_clicked
        )
        self.save_button.grid(column=1, row=4, sticky="ew", padx=10, pady=10)

    def validate_input(self, city, phone, email):
        """
        Validate the user input for city, phone number, and email.
        Returns:
            tuple: (True, "") if valid; (False, error_message) if invalid.
        """
        # Check if all fields are filled
        if not all([city, phone, email]):  # Check if any field is empty
            return False, "Please fill in all fields"

        # Basic phone number validation (international)
        if not re.match(r"^\+?\d{10,15}$", phone):  # Check phone number format
            return False, "Invalid phone number format"

        # Basic email format validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Check email format
            return False, "Invalid email format"

        return True, ""

    def save_user_data(self, city, phone, email):
        """
        Save the user input data to a JSON file.
        """
        # Create user data dictionary
        user_info = {"city": city, "phone": phone, "email": email}  # Create dictionary with user info

        try:
            # Read existing data if file exists
            if os.path.exists("users.json"):  # Check if users.json exists
                with open("users.json", "r") as user_data:  # Open file for reading
                    data = json.load(user_data)  # Load existing data
            else:
                data = []  # Create empty list if file doesn't exist

            # Append new user data and save to file
            data.append(user_info)  # Add new user data to list
            with open("users.json", "w") as user_data:  # Open file for writing
                json.dump(data, user_data, indent=4)  # Save data with nice formatting
        except Exception as e:
            print(f"Error saving user data: {e}")  # Print error if something goes wrong

    def save_button_clicked(self):
        """
        Callback for "Save user data" button. Validates inputs and saves user data.
        """
        # Get values from input fields
        city = self.city_entry.get().strip()  # Get city name and remove extra spaces
        phone = self.phone_number_entry.get()  # Get phone number
        email = self.email_entry.get()  # Get email

        # Validate the input
        valid, msg = self.validate_input(city, phone, email)  # Check if input is valid
        if not valid:
            messagebox.showerror("Validation Error", msg)  # Show error if invalid
            return

        # Save data and show success message
        self.save_user_data(city, phone, email)  # Save the data
        messagebox.showinfo("Success", "User data saved successfully.")  # Show success message

    def test_notification(self):
        """
        This function is used to test the notification system.
        It will send a test notification to the phone and email of the user.
        """
        # Get values from input fields
        city = self.city_entry.get()  # Get city name
        phone = self.phone_number_entry.get()  # Get phone number
        email = self.email_entry.get()  # Get email

        # Validate the input
        valid, msg = self.validate_input(city, phone, email)  # Check if input is valid
        if not valid:
            messagebox.showerror("Validation Error", msg)  # Show error if invalid
            return

        try:
            # Get weather data for the city
            raw_data = self.weather_service.fetch_weather_data(*self.weather_service.get_coordinates(city))  # Get weather data
            if not raw_data:  # Check if data was received
                messagebox.showerror("Error", "Could not fetch weather data")  # Show error if no data
                return

            # Extract relevant weather information
            relevant_data = self.weather_service.extract_relevant_data(raw_data)  # Process weather data
            if not relevant_data:  # Check if data was processed
                messagebox.showerror("Error", "Could not extract weather data")  # Show error if processing failed
                return

            # Get current weather information
            current = relevant_data["current"]  # Get current weather data
            temperature = raw_data["current"]["temp"]  # Get temperature
            weather_description = current["description"]  # Get weather description

            # Create detailed message for GUI display
            gui_message = f"Location Details:\n" \
                         f"City: {city}\n" \
                         f"Notification will be sent to:\n" \
                         f"Phone: {phone}\n" \
                         f"Email: {email}\n\n" \
                         f"Current Weather:\n" \
                         f"Temperature: {temperature}°C\n" \
                         f"Weather: {weather_description}"
            
            # Create simplified message for SMS and email
            notification_message = f"Weather Alert for {city}:\n" \
                                 f"Temperature: {temperature}°C\n" \
                                 f"Weather: {weather_description}"
            
            # Show detailed information in GUI
            messagebox.showinfo("Weather Test", gui_message)  # Show weather info

            # Send notification
            alert_type, response = self.alert_sender.send_alert(phone, email, notification_message)  # Send alert
            
            # Show notification status
            status_message = f"Notification Status:\nType: {alert_type}\nResponse: {response}"  # Create status message
            messagebox.showinfo("Notification Status", status_message)  # Show status

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")  # Show error if something goes wrong

    def run(self):
        """Start the GUI application"""
        self.window.mainloop()  # Start the main event loop


# Create and run the application when script is executed directly
if __name__ == "__main__":
    app = WeatherNotifierGUI()  # GUI instance
    app.run()  # Start the application