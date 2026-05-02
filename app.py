import requests
import streamlit as st
import random
import time

API_KEY = "96b611a7cf5b169339daf2387127668c"


# ---------------- THEME ----------------
st.set_page_config(
    NimbusAI="",
    page_icon="https://chatgpt.com/s/m_69f56085e94c81919644b871d5dcf1c5",
    layout="centered"
)

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}

.stChatMessage {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- AI PERSONALITY ----------------
def ai_intro():
    return random.choice([
        "I’m your friendly weather assistant ☀️",
        "Let’s pick the perfect outfit for today 🌦️",
        "I read the skies so you don’t have to 🌤️",
        "Weather? Consider it handled 😎"
    ])


def ai_comment(temp, condition):
    condition = condition.lower()

    if temp < 5:
        return "🥶 Brrr… I’m feeling cold just looking at this."
    elif temp > 30:
        return "🔥 It’s hot enough to melt ice cream fast!"
    elif "rain" in condition:
        return "☔ Rain alert—don’t forget your umbrella!"
    elif "snow" in condition:
        return "❄️ Snow day vibes!"
    elif "cloud" in condition:
        return "☁️ A little gloomy, but still nice."
    else:
        return "🙂 Pretty normal weather today."


# ---------------- LOCATION AUTO-DETECT ----------------
def get_location():
    try:
        r = requests.get(
            "https://ipinfo.io/json",
            timeout=5
        )

        data = r.json()

        return data.get("city")

    except Exception:
        return None


# ---------------- WEATHER ----------------
def get_weather(city, unit="metric"):

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={API_KEY}"
        f"&units={unit}"
    )

    try:
        r = requests.get(url, timeout=5)
        data = r.json()

        if r.status_code != 200:
            return None

        return data

    except Exception:
        return None


def get_forecast(city, unit="metric"):

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}"
        f"&appid={API_KEY}"
        f"&units={unit}"
    )

    try:
        r = requests.get(url, timeout=5)
        data = r.json()

        if r.status_code != 200:
            return None

        forecast = []

        # every 8th item ≈ 24 hours
        for i in range(0, len(data["list"]), 8):

            day = data["list"][i]

            forecast.append({
                "date": day["dt_txt"].split(" ")[0],
                "temp": round(day["main"]["temp"], 1),
                "desc": day["weather"][0]["description"]
            })

        return forecast[:5]

    except Exception:
        return None


# ---------------- OUTFIT AI ----------------
def outfit_ai(weather):

    temp = weather["main"]["temp"]
    condition = weather["weather"][0]["description"].lower()
    wind = weather["wind"]["speed"]

    outfit = []

    if temp < 5:
        outfit += [
            "🧥 Heavy coat",
            "🧤 Gloves",
            "🧣 Scarf"
        ]

    elif temp < 15:
        outfit += [
            "🧥 Jacket",
            "👖 Jeans"
        ]

    elif temp < 25:
        outfit += [
            "👕 T-shirt",
            "👖 Light pants"
        ]

    else:
        outfit += [
            "🩳 Shorts",
            "👕 Light shirt",
            "🧢 Cap"
        ]

    if "rain" in condition:
        outfit += [
            "☔ Umbrella",
            "👟 Waterproof shoes"
        ]

    if "snow" in condition:
        outfit += [
            "❄️ Snow boots",
            "🧦 Thick layers"
        ]

    if wind > 8:
        outfit += [
            "🌬️ Windbreaker"
        ]

    return outfit


# ---------------- RESPONSE BUILDER ----------------
def build_weather_response(weather, forecast, symbol):

    outfit = outfit_ai(weather)

    temp = weather["main"]["temp"]
    desc = weather["weather"][0]["description"]

    response = f"""
🌍 **City:** {weather['name']}  
🌡️ **Temp:** {temp}{symbol}  
☁️ **Condition:** {desc}  

🧠 **AI says:** {ai_comment(temp, desc)}

👕 **What to wear:**  
"""

    response += "\n".join([f"- {item}" for item in outfit])

    response += "\n\n📊 **5-Day Forecast:**\n"

    if forecast:
        for f in forecast:
            response += (
                f"- {f['date']}: "
                f"{f['temp']}{symbol}, "
                f"{f['desc']}\n"
            )

    return response


# ---------------- CHAT UI ----------------
st.title("🌤️ AI Weather Assistant")

st.write(ai_intro())


# session memory
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------- UNIT TOGGLE ----------------
unit = st.radio(
    "Select unit",
    ["Celsius (°C)", "Fahrenheit (°F)"]
)

unit_param = (
    "metric"
    if "Celsius" in unit
    else "imperial"
)

symbol = (
    "°C"
    if "Celsius" in unit
    else "°F"
)


# ---------------- DISPLAY OLD CHAT ----------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------- USE MY LOCATION BUTTON ----------------
if st.button("📍 Use my location"):

    city = get_location()

    with st.chat_message("user"):

        if city:
            st.markdown(f"📍 {city}")
        else:
            st.markdown("📍 Unable to detect location")

    if city:

        weather = get_weather(city, unit_param)

        with st.chat_message("assistant"):

            if not weather:

                response = (
                    "❌ Couldn't fetch weather "
                    "for your location."
                )

            else:

                forecast = get_forecast(
                    city,
                    unit_param
                )

                response = build_weather_response(
                    weather,
                    forecast,
                    symbol
                )

            placeholder = st.empty()
            text = ""

            for word in response.split():
                text += word + " "
                time.sleep(0.01)
                placeholder.markdown(text + "▌")

            placeholder.markdown(text)

        st.session_state.messages.append({
            "role": "user",
            "content": f"📍 {city}"
        })

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })


# ---------------- CHAT INPUT ----------------
if prompt := st.chat_input(
    "Enter city name..."
):

    city = prompt.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": city
    })

    with st.chat_message("user"):
        st.markdown(city)

    weather = get_weather(
        city,
        unit_param
    )

    with st.chat_message("assistant"):

        if not weather:

            response = (
                "❌ I couldn’t find that city."
            )

        else:

            forecast = get_forecast(
                city,
                unit_param
            )

            response = build_weather_response(
                weather,
                forecast,
                symbol
            )

        placeholder = st.empty()
        text = ""

        for word in response.split():

            text += word + " "

            time.sleep(0.01)

            placeholder.markdown(text + "▌")

        placeholder.markdown(text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
