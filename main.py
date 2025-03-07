import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
import pytz

# Define the Jerusalem timezone
jerusalem_tz = pytz.timezone('Asia/Jerusalem')

# API Key and Base URL (using HTTPS)
API_KEY = st.secrets["API_KEY"]

BASE_URL = "https://api.weatherapi.com/v1/current.json"
BASE_URL_FORECAST = "https://api.weatherapi.com/v1/forecast.json"
BASE_URL_HISTORY = "https://api.weatherapi.com/v1/history.json"


def fetch_weather(city):
    """
    Fetch current weather data for the given city.
    """
    url = f"{BASE_URL}?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_forecast(city, days=4):
    """
    Fetch forecast data for the given city.
    """
    url = f"{BASE_URL_FORECAST}?key={API_KEY}&q={city}&days={days}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_historical(city, date):
    """
    Fetch historical weather data for the given city and date.
    """
    url = f"{BASE_URL_HISTORY}?key={API_KEY}&q={city}&dt={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Streamlit UI
st.title("Welcome to the Best Weather App\nCheck the weather in any city worldwide")
st.markdown("### What is the city's name you would like to check?")
city = st.text_input("", "", max_chars=25)

# Auto-correct for Holon to default to Israel
if city.lower() == "holon":
    city = "Holon, Israel"

if city:
    weather_data = fetch_weather(city)
    if weather_data:
        # Display current weather
        location = f"{weather_data['location']['name']}, {weather_data['location']['country']}"
        temp_c = weather_data['current']['temp_c']
        feels_like = weather_data['current']['feelslike_c']
        condition = weather_data['current']['condition']['text']
        icon_url = f"https:{weather_data['current']['condition']['icon']}"

        st.subheader(f"Weather in {location}")
        st.image(icon_url, width=100)
        st.write(f"**Current temperature:** {temp_c}°C")
        st.write(f"**Feels Like:** {feels_like}°C")
        st.write(f"**Condition:** {condition}")

        # Forecast
        forecast_data = fetch_forecast(city, days=4)  # Fetch 4 days to have 3 future days after excluding today
        if forecast_data:
            forecast_days = forecast_data['forecast']['forecastday']
            today_date = datetime.now().strftime('%Y-%m-%d')
            future_days = [day for day in forecast_days if day['date'] != today_date][:3]

            # Determine the most frequent weather condition
            conditions = [day['day']['condition']['text'] for day in future_days]
            most_frequent_condition = max(set(conditions), key=conditions.count).lower()

            # Prepare DataFrame for the forecast
            forecast_df = pd.DataFrame([
                {
                    "Date": datetime.strptime(day['date'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                    "Max Temp (°C)": day['day']['maxtemp_c'],
                    "Min Temp (°C)": day['day']['mintemp_c']
                }
                for day in future_days
            ])

            # Calculate average chance of rain
            avg_rain_chance = sum(day['day']['daily_chance_of_rain'] for day in future_days) / len(future_days)

            st.subheader("3-Day Temperature Forecast")
            if avg_rain_chance > 50:
                st.write(
                    f"The next 3 days are expected to be mostly {most_frequent_condition} with a high chance of rain.")
            else:
                st.write(
                    f"The next 3 days are expected to be mostly {most_frequent_condition} with no rain expectancy.")

            forecast_df[["Max Temp (°C)", "Min Temp (°C)"]] = forecast_df[["Max Temp (°C)", "Min Temp (°C)"]].round(1)
            forecast_df.set_index("Date", inplace=True)

            # Create a new figure for the forecast chart
            fig, ax = plt.subplots(figsize=(8, 5))
            forecast_df.plot(kind='bar', ax=ax)
            ax.set_title("Temperature Forecast (°C)")
            ax.set_ylabel("Temperature (°C)")
            ax.set_xlabel("Date")
            ax.set_xticklabels(forecast_df.index, rotation=0)
            st.pyplot(fig)

        # Historical Data Comparison
        st.subheader("Historical Data Comparison")
        past_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # Same day last year
        historical_data = fetch_historical(city, past_date)
        if historical_data:
            historical_temp = historical_data['forecast']['forecastday'][0]['day']['avgtemp_c']
            temp_difference = temp_c - historical_temp
            if temp_difference > 0:
                st.write(
                    f"**Today is warmer by {temp_difference:.1f}°C compared to the same day last year (was {historical_temp:.1f}°C).**")
            else:
                st.write(
                    f"**Today is colder by {abs(temp_difference):.1f}°C compared to the same day last year (was {historical_temp:.1f}°C).**")
        else:
            st.error("Failed to fetch historical data.")
    else:
        st.error("Failed to fetch weather data. Please check the city name and try again.")
