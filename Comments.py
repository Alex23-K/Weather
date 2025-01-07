import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Constants
API_KEY = "YOUR_API_KEY"
BASE_URL_CURRENT = "http://api.weatherapi.com/v1/current.json"
BASE_URL_FORECAST = "http://api.weatherapi.com/v1/forecast.json"
BASE_URL_HISTORY = "http://api.weatherapi.com/v1/history.json"

# Helper functions
def fetch_weather(city):
    """
    Fetch weather data for the given city using WeatherAPI.
    """
    url = f"{BASE_URL_CURRENT}?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_forecast(city, days=3):
    """
    Fetch forecast data for the given city using WeatherAPI.
    """
    url = f"{BASE_URL_FORECAST}?key={API_KEY}&q={city}&days={days}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_historical(city, date):
    """
    Fetch historical weather data for a given city and date using WeatherAPI.
    """
    url = f"{BASE_URL_HISTORY}?key={API_KEY}&q={city}&dt={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Streamlit UI
st.title("Enhanced Weather Checker Application")

# Make the input prompt larger
st.markdown("### What is the city's name you would like to check?")

# Adjust the input field width
city = st.text_input("", "", max_chars=50)

# Auto-correct for Holon to default to Israel
if city.lower() == "holon":
    city = "Holon, Israel"

if city:
    weather_data = fetch_weather(city)
    if weather_data:
        # Current Weather
        location = f"{weather_data['location']['name']}, {weather_data['location']['country']}"
        temp_c = weather_data['current']['temp_c']
        feels_like = weather_data['current']['feelslike_c']
        condition = weather_data['current']['condition']['text']
        icon_url = f"https:{weather_data['current']['condition']['icon']}"

        st.subheader(f"Weather in {location}")
        st.image(icon_url, width=100)
        st.write(f"**Temperature:** {temp_c}°C")
        st.write(f"**Feels Like:** {feels_like}°C")
        st.write(f"**Condition:** {condition}")

        # Forecast
        forecast_data = fetch_forecast(city)
        if forecast_data:
            st.subheader("Rainy Days Forecast")
            forecast_days = forecast_data['forecast']['forecastday']
            rainy_days = [
                f"On {datetime.strptime(day['date'], '%Y-%m-%d').strftime('%d/%m/%Y')}, it will be rainy with a condition: {day['day']['condition']['text']}."
                for day in forecast_days if day['day']['daily_chance_of_rain'] > 50
            ]

            if rainy_days:
                for message in rainy_days:
                    st.write(message)
            else:
                st.write("No rainy days are expected in the forecast.")

            # 3-Day Forecast Table
            st.subheader("3-Day Forecast")
            forecast_df = pd.DataFrame([
                {
                    "Date": datetime.strptime(day['date'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                    "Max Temp (°C)": day['day']['maxtemp_c'],
                    "Min Temp (°C)": day['day']['mintemp_c']
                }
                for day in forecast_days
            ])
            # Format numerical columns explicitly
            forecast_df["Max Temp (°C)"] = forecast_df["Max Temp (°C)"].map("{:.1f}".format)
            forecast_df["Min Temp (°C)"] = forecast_df["Min Temp (°C)"].map("{:.1f}".format)
            st.table(forecast_df)

            # Bar Graph for Forecast
            st.subheader("Temperature Forecast")
            forecast_df.set_index("Date", inplace=True)
            forecast_df.plot(kind='bar', figsize=(8, 5))
            plt.title("Temperature Forecast (°C)")
            plt.ylabel("Temperature (°C)")
            plt.xlabel("Date")
            plt.xticks(rotation=0)  # Horizontal x-axis labels
            st.pyplot(plt)

        # Historical Data
        st.subheader("Historical Comparison")
        today = datetime.now()
        past_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        historical_data = fetch_historical(city, past_date)
        if historical_data:
            historical_temp = historical_data['forecast']['forecastday'][0]['day']['avgtemp_c']
            temp_difference = temp_c - historical_temp
            if temp_difference > 0:
                st.write(f"**Today is warmer by {temp_difference:.1f}°C compared to the same week one year ago (was {historical_temp:.1f}°C).**")
            else:
                st.write(f"**Today is colder by {abs(temp_difference):.1f}°C compared to the same week one year ago (was {historical_temp:.1f}°C).**")
    else:
        st.error("Failed to fetch weather data. Please check the city name and try again.")
