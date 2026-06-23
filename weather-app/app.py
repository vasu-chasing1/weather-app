from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import json

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")

@app.route('/', methods=["GET", "POST"])
def index():
    city = "Delhi"

    weather = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")
    if not city:
         error = "Please enter a city name."
    elif not API_KEY:
         error = "API key not configured. Set API_KEY in your .env file."
    else:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={API_KEY}&units=metric"

        )

        try:
             response = requests.get(url)
             data = response.json()
             print(data)
             
             if response.status_code == 200:
                weather = {
                    "city": data.get("name"),
                    "country": data.get("sys", {}).get("country"),
                    "temperature": data.get("main", {}).get("temp"),
                    "feels_like": data.get("main", {}).get("feels_like"),
                    "humidity": data.get("main", {}).get("humidity"),
                    "description": data.get("weather", [{}])[0].get("description", "").title(),
                    "wind_speed": data.get("wind", {}).get("speed"),
                    "icon": data.get("weather", [{}])[0].get("icon"),
                    "temp_min": data["main"]["temp_min"],
                    "temp_max": data["main"]["temp_max"],
                    "pressure": data["main"]["pressure"],
                    "visibility": data["visibility"] / 1000,
                    "updated": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    }
             else:
                 # prefer API message when available
                 error = "Location not found. Try a nearby city or check the spelling."
        except Exception as e:
             error = f"Error: {e}"

    return render_template(
        "index.html",
        weather=weather,
        error=error
    )

@app.route("/forecast")
def forecast():
    city = request.args.get("city")
    if not city:
        return "No city provided"
    
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises error for bad status codes
        data = response.json()
        
        if "list" not in data:
            return "Invalid city name or API error"
        
        forecasts = []
        for item in data["list"]:
            if "12:00:00" in item["dt_txt"]:
                date_obj = datetime.strptime(
                    item["dt_txt"],
                    "%Y-%m-%d %H:%M:%S"
                )
                formatted_date = date_obj.strftime("%d %b")
                forecast = {
                    "date": formatted_date,
                    "temp": item["main"]["temp"],
                    "description": item["weather"][0]["description"].title(),
                    "icon": item["weather"][0]["icon"]
                }
                forecasts.append(forecast)
        
        return render_template("forecast.html", forecasts=forecasts)
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching forecast: {str(e)}"

        
    
if __name__ == "__main__":
    app.run(debug=True, port=5001)


