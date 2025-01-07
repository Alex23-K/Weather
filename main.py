import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta


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
st.title("Welcome to the best weather App \n"
         "Check the weather in any city worldwide")

# Make the input prompt larger
st.markdown("### What is the city's name you would like to check?")

# Adjust the input field width
city = st.text_input("", "", max_chars=25)


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
        st.write(f"**Current temperature:** {temp_c}°C")
        st.write(f"**Feels Like:** {feels_like}°C")
        st.write(f"**Condition:** {condition}")


        # Forecast
        forecast_data = fetch_forecast(city)
        if forecast_data:

            forecast_days = forecast_data['forecast']['forecastday']

            # Calculate average chance of rain
            avg_rain_chance = sum(day['day']['daily_chance_of_rain'] for day in forecast_days) / len(forecast_days)

            # Determine the most frequent weather condition
            conditions = [day['day']['condition']['text'] for day in forecast_days]
            most_frequent_condition = max(set(conditions), key=conditions.count).lower()



            # 3-Day Forecast Table

            forecast_df = pd.DataFrame([
                {
                    "Date": datetime.strptime(day['date'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                    "Max Temp (°C)": day['day']['maxtemp_c'],
                    "Min Temp (°C)": day['day']['mintemp_c']
                }
                for day in forecast_days
            ])


            # 3 daya forecast and the Bar chart

            st.subheader("3-Day temperature forecast")
            # Ensure proper rounding for display
            forecast_df[["Max Temp (°C)", "Min Temp (°C)"]] = forecast_df[["Max Temp (°C)", "Min Temp (°C)"]].round(1)

            # Generate summary sentence
            if avg_rain_chance > 50:
                st.write(
                    f"The next 3 days are expected to be mostly {most_frequent_condition} with a high chance of rain.")
            else:
                st.write(
                    f"The next 3 days are expected to be mostly {most_frequent_condition} with no rain expectancy.")


            forecast_df.set_index("Date", inplace=True)
            forecast_df.plot(kind='bar', figsize=(8, 5))
            plt.title("Temperature Forecast (°C)")
            plt.ylabel("Temperature (°C)")
            plt.xlabel("Date")
            plt.xticks(rotation=0)  # Horizontal x-axis labels
            st.pyplot(plt)

        # Historical Data
        st.subheader("Historical data comparison")
        today = datetime.now()
        past_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        historical_data = fetch_historical(city, past_date)
        if historical_data:
            historical_temp = historical_data['forecast']['forecastday'][0]['day']['avgtemp_c']
            temp_difference = temp_c - historical_temp
            if temp_difference > 0:
                st.write(f"**Today is warmer by {temp_difference:.1f}°C compared to the previous year in the same week (was {historical_temp:.1f}°C).**")
            else:
                st.write(f"**Today is colder by {abs(temp_difference):.1f}°C compared to the previous year in the same week (was {historical_temp:.1f}°C).**")
    else:
        st.error("Failed to fetch weather data. Please check the city name and try again.")
