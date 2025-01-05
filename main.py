
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests



# API Key and Base URL
API_KEY = "f935fae84b5f4044931182757250501"
BASE_URL = "http://api.weatherapi.com/v1/current.json"
BASE_URL_FORECAST = "http://api.weatherapi.com/v1/forecast.json"
BASE_URL_HISTORY = "http://api.weatherapi.com/v1/history.json"


def fetch_weather(city):
    """
    Fetch weather data for the given city using WeatherAPI.
    """
    url = f"{BASE_URL}?key={API_KEY}&q={city}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
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
st.title("Weather App - check the weather in any city worldwide")

# Input for city name
city = st.text_input("What is the city's name to check?", "")

if city:
    weather_data = fetch_weather(city)
    if weather_data:
        country = weather_data['location']['country']
        if country == "Iran":
            st.error("Weather data for Iran is not available.")
        else:
            # Current Weather
            location = f"{weather_data['location']['name']}, {country}"
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
                st.subheader("3-Day Forecast")
                forecast_days = forecast_data['forecast']['forecastday']
                forecast_df = pd.DataFrame([
                    {
                        "Date": day['date'],
                        "Max Temp (°C)": day['day']['maxtemp_c'],
                        "Min Temp (°C)": day['day']['mintemp_c']
                    }
                    for day in forecast_days
                ])
                st.table(forecast_df)

                # Plotting Forecast
                st.subheader("Temperature Forecast")
                plt.figure(figsize=(8, 5))
                plt.plot(forecast_df['Date'], forecast_df['Max Temp (°C)'], marker='o', label="Max Temp")
                plt.plot(forecast_df['Date'], forecast_df['Min Temp (°C)'], marker='o', label="Min Temp")
                plt.title("Temperature Forecast (°C)")
                plt.xlabel("Date")
                plt.ylabel("Temperature (°C)")
                plt.legend()
                st.pyplot(plt)

            # Historical Data
            st.subheader("Historical Comparison")
            from datetime import datetime, timedelta
            today = datetime.now()
            past_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
            historical_data = fetch_historical(city, past_date)
            if historical_data:
                historical_temp = historical_data['forecast']['forecastday'][0]['day']['avgtemp_c']
                st.write(f"**Historical Avg Temp (1 year ago):** {historical_temp}°C")
                st.write(f"**Temperature Difference:** {temp_c - historical_temp:.1f}°C")
    else:
        st.error("Failed to fetch weather data. Please check the city name and try again.")