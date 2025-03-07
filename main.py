import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
import pytz

# Define the Jerusalem timezone
jerusalem_tz = pytz.timezone('Asia/Jerusalem')

# API Key and Base URL
API_KEY = st.secrets["API_KEY"]

BASE_URL = "http://api.weatherapi.com/v1/current.json"
BASE_URL_FORECAST = "http://api.weatherapi.com/v1/forecast.json"
BASE_URL_HISTORY = "http://api.weatherapi.com/v1/history.json"


# Function to fetch current weather
def fetch_weather(city):
    """
    Fetch weather data for the given city using WeatherAPI.
    """
    url = f"{BASE_URL}?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch forecast data
def fetch_forecast(city, days=4):
    """
    Fetch forecast data for the given city using WeatherAPI.
    """
    url = f"{BASE_URL_FORECAST}?key={API_KEY}&q={city}&days={days}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Function to fetch historical weather data
def fetch_historical(city, date):
    """
    Fetch historical weather data for a given city and date using WeatherAPI.
    """
    url = f"{BASE_URL_HISTORY}?key={API_KEY}&q={city}&dt={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Streamlit UI Title
st.title("🌍 Welcome to the Best Weather App")
st.markdown("### Enter the city name to check the weather:")

# Input Field for City Name
city = st.text_input("City Name", "", max_chars=25)

# Auto-correct for Holon to default to Israel
if city.lower() == "holon":
    city = "Holon, Israel"

# Fetch Weather Data
if city:
    weather_data = fetch_weather(city)
    if weather_data:
        # Extract Weather Data
        location = f"{weather_data['location']['name']}, {weather_data['location']['country']}"
        temp_c = weather_data['current']['temp_c']
        feels_like = weather_data['current']['feelslike_c']
        condition = weather_data['current']['condition']['text']
        icon_url = f"https:{weather_data['current']['condition']['icon']}"

        # Display Weather Data
        st.subheader(f"Weather in {location}")
        st.image(icon_url, width=100)
        st.write(f"🌡️ **Current Temperature:** {temp_c}°C")
        st.write(f"🌬️ **Feels Like:** {feels_like}°C")
        st.write(f"☁️ **Condition:** {condition}")

        # Fetch Forecast Data
        forecast_data = fetch_forecast(city, days=4)
        if forecast_data:
            forecast_days = forecast_data['forecast']['forecastday']

            # Exclude today's forecast
            today_date = datetime.now().strftime('%Y-%m-%d')
            future_days = [day for day in forecast_days if day['date'] != today_date][:3]  # Keep only 3 future days

            # Determine the most frequent weather condition
            conditions = [day['day']['condition']['text'] for day in future_days]
            most_frequent_condition = max(set(conditions), key=conditions.count).lower()

            # Prepare Data for Forecast Chart
            forecast_df = pd.DataFrame([
                {
                    "Date": datetime.strptime(day['date'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                    "Max Temp (°C)": day['day']['maxtemp_c'],
                    "Min Temp (°C)": day['day']['mintemp_c']
                }
                for day in future_days
            ])

            # Calculate Average Rain Chance
            avg_rain_chance = sum(day['day']['daily_chance_of_rain'] for day in future_days) / len(future_days)

            st.subheader("📅 3-Day Temperature Forecast")

            # Generate Summary Sentence
            if avg_rain_chance > 50:
                st.write(
                    f"The next 3 days are expected to be mostly {most_frequent_condition} with a high chance of rain. ☔")
            else:
                st.write(
                    f"The next 3 days are expected to be mostly {most_frequent_condition} with no rain expectancy. ☀️")

            # Ensure clear figure before plotting
            plt.clf()
            forecast_df.set_index("Date", inplace=True)
            forecast_df.plot(kind='bar', figsize=(8, 5), color=["#1f77b4", "#ff7f0e"])
            plt.title("Temperature Forecast (°C)")
            plt.ylabel("Temperature (°C)")
            plt.xlabel("Date")
            plt.xticks(rotation=0)  # Horizontal x-axis labels
            st.pyplot(plt)

        # Fetch Historical Data
        st.subheader("📊 Historical Temperature Comparison")
        past_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        historical_data = fetch_historical(city, past_date)

        if historical_data and "forecast" in historical_data:
            try:
                historical_temp = historical_data['forecast']['forecastday'][0]['day']['avgtemp_c']
                temp_difference = temp_c - historical_temp

                # Generate Difference Text
                difference_text = (
                    f"📈 Today is **warmer** by {temp_difference:.1f}°C compared to last year."
                    if temp_difference > 0
                    else f"📉 Today is **colder** by {abs(temp_difference):.1f}°C compared to last year."
                )

                # Clear Figure Before Plotting
                plt.clf()

                # Historical Comparison Bar Chart
                history_df = pd.DataFrame({
                    "Date": ["Today", "Last Year"],
                    "Temperature (°C)": [temp_c, historical_temp]
                })
                history_df.set_index("Date", inplace=True)

                # Display Difference Text & Chart
                st.write(difference_text)
                history_df.plot(kind='bar', color=["#1f77b4", "#ff7f0e"], figsize=(5, 4))
                plt.title("Temperature Comparison (°C)")
                plt.ylabel("Temperature (°C)")
                plt.xticks(rotation=0)
                st.pyplot(plt)

            except (KeyError, IndexError):
                st.warning("⚠️ Historical data is unavailable for this date.")
        else:
            st.warning("⚠️ Failed to fetch historical data.")

    else:
        st.error("❌ Failed to fetch weather data. Please check the city name and try again.")
