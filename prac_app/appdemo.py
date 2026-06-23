from flask import Flask, request,render_template
import requests
import os 
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")


@app.route('/', methods=["POST", "GET"])
def index():
    weather = None
    error = None
    if request.method == "POST":
        city = request.form.get("city")

        if not city:
            error = "Please Enter a City Name."
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

            if response.status_code == "200":
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
                error = data.get("message", "City not Found.")
        except Exception as e:
            error = f"Error: {e}"
    
    return render_template(
        "index.html",
        weather=weather,
        error=error
    )

if __name__ == "__main__":
    ()