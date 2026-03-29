from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city, units="metric"):
    params = {"q": city, "appid": API_KEY, "units": units}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json(), None
    elif response.status_code == 404:
        return None, "City not found. Please try again."
    else:
        return None, "Something went wrong. Please try later."


def get_weather_emoji(condition):
    c = condition.lower()
    if "thunder" in c:   return "⛈️"
    if "drizzle" in c:   return "🌦️"
    if "rain" in c:      return "🌧️"
    if "snow" in c:      return "❄️"
    if any(x in c for x in ["mist","fog","haze"]): return "🌫️"
    if "clear" in c:     return "☀️"
    if "cloud" in c:     return "☁️"
    return "🌈"


def get_weather_class(condition):
    c = condition.lower()
    if "thunder" in c:   return "thunder"
    if "drizzle" in c:   return "drizzle"
    if "rain" in c:      return "rain"
    if "snow" in c:      return "snow"
    if "clear" in c:     return "clear"
    if any(x in c for x in ["mist","fog","haze"]): return "mist"
    if "cloud" in c:     return "cloud"
    return "default"


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    error = None
    emoji = None
    weather_class = "default"
    unit_symbol = "°C"
    units = "metric"

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        units = request.form.get("units", "metric")
        unit_symbol = "°C" if units == "metric" else "°F"

        if city:
            data, error = get_weather(city, units)
            if data:
                condition = data["weather"][0]["description"]
                weather_class = get_weather_class(condition)
                emoji = get_weather_emoji(condition)
                weather = {
                    "city":        data["name"],
                    "country":     data["sys"]["country"],
                    "temp":        round(data["main"]["temp"]),
                    "feels_like":  round(data["main"]["feels_like"]),
                    "humidity":    data["main"]["humidity"],
                    "wind":        round(data["wind"]["speed"]),
                    "description": condition.title(),
                    "visibility":  round(data.get("visibility", 0) / 1000, 1),
                    "pressure":    data["main"]["pressure"],
                }
        else:
            error = "Please enter a city name."

    return render_template("index.html",
        weather=weather, error=error, emoji=emoji,
        weather_class=weather_class, unit_symbol=unit_symbol, units=units)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)