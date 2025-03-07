import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
import pytz

# Define the Jerusalem timezone
jerusalem_tz = pytz.timezone('Asia/Jerusalem')

# 🔹 Get API Key (Check Streamlit Secrets or Environment Variable)
API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY"))
if not API_KEY:
    st.error("⚠️ API key is missing! Please add it to `.streamlit/secrets.toml` or set it as an environment variable.")

# API Base URLs
BASE_URL = "http://api.weatherapi.com/v1/current.json"
BASE_URL_FORECAST = "http://api.weatherapi.com/v1/forecast.json"
BASE_URL_HISTORY = "http://api.weatherapi.com/v1/history.json"


def fetch_weather(city):
    """Fetch current weather data for the given city."""
    url = f"{BASE_URL}?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_forecast(city, days=4):
    """Fetch forecast data for the given city."""
    url = f"{BASE_URL_FORECAST}?key={API_KEY}&q={city}&days={days}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def fetch_historical(city, date):
    """Fetch historical weather data for a given city and date using WeatherAPI."""
    url = f"{BASE_URL_HISTORY}?key={API_KEY}&q={city}&dt={date}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        st.write("📊 **API Response for Historical Data:**", data)  # Debugging output
        return data
    else:
        st.write("❌ **API Error:**", response.status_code, response.text)  # Debugging output
        return None




# 🔹 Streamlit UI
st.title("🌍 Welcome to the Best Weather App")
st.markdown("### Enter the city name to check the weather:")

city = st.text_input("City Name", "", max_chars=25)

# Auto-correct for Holon to default to Israel
if city.lower() == "holon":
    city = "Holon, Israel"

# 🔹 Fetch Weather Data
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

        # 🔹 Fetch Forecast Data
        forecast_data = fetch_forecast(city, days=4)
        if forecast_data:
            forecast_days = forecast_data['forecast']['forecastday']
            today_date = datetime.now().strftime('%Y-%m-%d')
            future_days = [day for day in forecast_days if day['date'] != today_date][:3]

            # Determine most frequent weather condition
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

            # Summary Sentence
            rain_text = "with a high chance of rain. ☔" if avg_rain_chance > 50 else "with no rain expectancy. ☀️"
            st.write(f"The next 3 days are expected to be mostly {most_frequent_condition} {rain_text}")

            # 🔹 Ensure clear figure before plotting
            plt.clf()
            forecast_df.set_index("Date", inplace=True)
            forecast_df.plot(kind='bar', figsize=(8, 5), color=["#1f77b4", "#ff7f0e"])
            plt.title("Temperature Forecast (°C)")
            plt.ylabel("Temperature (°C)")
            plt.xlabel("Date")
            plt.xticks(rotation=0)
            st.pyplot(plt)

        # 🔹 Fetch Historical Data
        st.subheader("📊 Historical Temperature Comparison")
        past_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        historical_data = fetch_historical(city, past_date)

        if historical_data and "forecast" in historical_data:
            try:
                historical_temp = historical_data['forecast']['forecastday'][0]['day'].get('avgtemp_c', None)

                if historical_temp is None:
                    st.warning("⚠️ No historical temperature data available for this date.")
                else:
                    temp_difference = temp_c - historical_temp
                    difference_text = (
                        f"📈 Today is **warmer** by {temp_difference:.1f}°C compared to last year."
                        if temp_difference > 0
                        else f"📉 Today is **colder** by {abs(temp_difference):.1f}°C compared to last year."
                    )

                    # 🔹 Clear figure before plotting
                    plt.clf()

                    # Historical comparison bar chart
                    history_df = pd.DataFrame({
                        "Date": ["Today", "Last Year"],
                        "Temperature (°C)": [temp_c, historical_temp]
                    })
                    history_df.set_index("Date", inplace=True)

                    st.write(difference_text)
                    history_df.plot(kind='bar', color=["#1f77b4", "#ff7f0e"], figsize=(5, 4))
                    plt.title("Temperature Comparison (°C)")
                    plt.ylabel("Temperature (°C)")
                    plt.xticks(rotation=0)
                    st.pyplot(plt)

            except (KeyError, IndexError):
                st.warning("⚠️ Historical data format is incorrect or missing.")
        else:
            st.warning("⚠️ No historical data available for this city/date.")

    else:
        st.error("❌ Failed to fetch weather data. Please check the city name and try again.")
