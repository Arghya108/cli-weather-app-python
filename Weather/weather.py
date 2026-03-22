"""
============================================================
  Weather App (CLI) — Python Project
  Author   : Built for Arghya's Portfolio
  Version  : 1.0
  API      : OpenWeatherMap (free tier)
  Libs     : Standard Python only (urllib, json, os, sys)
============================================================
  HOW TO GET YOUR FREE API KEY:
  1. Go to https://openweathermap.org/api
  2. Click "Sign Up" and create a free account
  3. Go to your profile → "My API Keys"
  4. Copy your default key (or generate a new one)
  5. Paste it in the API_KEY variable below
============================================================
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import os
import sys
import time


# ============================================================
#  CONFIGURATION — Put your API key here
# ============================================================

API_KEY  = "7bafe0b2559474f03d14152c3535ffce"         # ← Replace with your key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# ============================================================
#  COLOR HELPER — ANSI codes (no libraries needed)
# ============================================================

class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    GREY    = "\033[90m"

def c(text, color):
    """Wrap text in a color and reset."""
    return f"{color}{text}{Color.RESET}"


# ============================================================
#  WEATHER ICON MAPPER — Adds emoji based on condition
# ============================================================

def get_weather_icon(condition):
    """
    Return an emoji icon matching the weather condition string.
    Condition comes from OpenWeatherMap (e.g. 'Clear', 'Rain').
    """
    icons = {
        "clear"         : "☀️ ",
        "clouds"        : "☁️ ",
        "rain"          : "🌧️ ",
        "drizzle"       : "🌦️ ",
        "thunderstorm"  : "⛈️ ",
        "snow"          : "❄️ ",
        "mist"          : "🌫️ ",
        "smoke"         : "🌫️ ",
        "haze"          : "🌫️ ",
        "fog"           : "🌫️ ",
        "dust"          : "🌪️ ",
        "sand"          : "🌪️ ",
        "tornado"       : "🌪️ ",
    }
    # Match by lowercased first word of condition
    key = condition.lower()
    for k, icon in icons.items():
        if k in key:
            return icon
    return "🌡️ "  # Default icon


# ============================================================
#  API CALL — Fetches raw JSON from OpenWeatherMap
# ============================================================

def get_weather_data(city, unit):
    """
    Fetch weather data from OpenWeatherMap API for a given city.

    Parameters:
        city (str) : Name of the city to search
        unit (str) : 'metric' for Celsius, 'imperial' for Fahrenheit

    Returns:
        dict : Parsed JSON response from API
        None : If request fails (error handled inside)
    """

    # Build query parameters
    params = {
        "q"       : city,
        "appid"   : API_KEY,
        "units"   : unit        # 'metric' → °C | 'imperial' → °F
    }

    # Encode params into URL (handles spaces, special chars)
    query_string = urllib.parse.urlencode(params)
    full_url     = f"{BASE_URL}?{query_string}"

    try:
        # Show loading message while fetching
        print(c(f"\n  ⏳ Fetching weather data for '{city}'...", Color.GREY))

        # Open URL with a 10-second timeout
        with urllib.request.urlopen(full_url, timeout=10) as response:
            # Read raw bytes and decode to string
            raw_data = response.read().decode("utf-8")
            # Parse JSON string into Python dictionary
            return json.loads(raw_data)

    except urllib.error.HTTPError as e:
        # API returned an error status code
        if e.code == 401:
            print(c("\n  ❌ ERROR: Invalid API Key.", Color.RED))
            print(c("  → Check your API_KEY in the script.", Color.YELLOW))
        elif e.code == 404:
            print(c(f"\n  ❌ ERROR: City '{city}' not found.", Color.RED))
            print(c("  → Check spelling or try a different city name.", Color.YELLOW))
        elif e.code == 429:
            print(c("\n  ❌ ERROR: Too many requests. API limit hit.", Color.RED))
            print(c("  → Wait a few minutes and try again.", Color.YELLOW))
        else:
            print(c(f"\n  ❌ HTTP Error {e.code}: {e.reason}", Color.RED))
        return None

    except urllib.error.URLError as e:
        # Network-level error (no internet, DNS fail, etc.)
        print(c("\n  ❌ ERROR: Cannot connect to OpenWeatherMap.", Color.RED))
        print(c(f"  → Check your internet connection. ({e.reason})", Color.YELLOW))
        return None

    except json.JSONDecodeError:
        # Response wasn't valid JSON
        print(c("\n  ❌ ERROR: Unexpected response from server.", Color.RED))
        return None

    except Exception as e:
        # Catch-all for any other unexpected errors
        print(c(f"\n  ❌ Unexpected error: {e}", Color.RED))
        return None


# ============================================================
#  DATA PARSER — Extracts needed fields from JSON
# ============================================================

def parse_weather_data(data, unit):
    """
    Extract relevant fields from the raw OpenWeatherMap JSON response.

    Parameters:
        data (dict) : Raw JSON dictionary from API
        unit (str)  : 'metric' or 'imperial'

    Returns:
        dict : Clean dictionary with only the fields we need
    """

    # Determine correct unit symbol
    temp_unit   = "°C" if unit == "metric" else "°F"
    speed_unit  = "m/s" if unit == "metric" else "mph"

    # Extract fields safely using .get() with defaults
    # This prevents KeyError if a field is missing in response
    parsed = {
        "city"        : data.get("name", "Unknown"),
        "country"     : data.get("sys", {}).get("country", "??"),
        "condition"   : data.get("weather", [{}])[0].get("main", "N/A"),
        "description" : data.get("weather", [{}])[0].get("description", "N/A").capitalize(),
        "temp"        : data.get("main", {}).get("temp", 0),
        "feels_like"  : data.get("main", {}).get("feels_like", 0),
        "temp_min"    : data.get("main", {}).get("temp_min", 0),
        "temp_max"    : data.get("main", {}).get("temp_max", 0),
        "humidity"    : data.get("main", {}).get("humidity", 0),
        "wind_speed"  : data.get("wind", {}).get("speed", 0),
        "visibility"  : data.get("visibility", 0) // 1000,  # Convert m → km
        "temp_unit"   : temp_unit,
        "speed_unit"  : speed_unit,
    }

    return parsed


# ============================================================
#  DISPLAY — Prints formatted weather card to terminal
# ============================================================

def display_weather(weather):
    """
    Print a clean, formatted weather report in the terminal.

    Parameter:
        weather (dict) : Parsed weather dictionary from parse_weather_data()
    """

    icon      = get_weather_icon(weather["condition"])
    temp_unit = weather["temp_unit"]
    spd_unit  = weather["speed_unit"]

    # Color code temperature
    temp      = weather["temp"]
    if temp <= 10:
        temp_color = Color.CYAN
    elif temp <= 25:
        temp_color = Color.GREEN
    else:
        temp_color = Color.RED

    print()
    print(c("  ╔══════════════════════════════════════════╗", Color.BLUE))
    print(c(f"  ║   {icon}  WEATHER REPORT", Color.BLUE) +
          " " * 22 + c("║", Color.BLUE))
    print(c("  ╠══════════════════════════════════════════╣", Color.BLUE))

    # Location
    location = f"{weather['city']}, {weather['country']}"
    print(c("  ║", Color.BLUE) +
          f"  📍 {c(location, Color.WHITE + Color.BOLD)}" +
          " " * max(0, 38 - len(location)) +
          c("║", Color.BLUE))

    # Condition
    condition_str = f"{icon}{weather['description']}"
    print(c("  ║", Color.BLUE) +
          f"  🌤  {condition_str}" +
          " " * max(0, 38 - len(condition_str)) +
          c("║", Color.BLUE))

    print(c("  ╠══════════════════════════════════════════╣", Color.BLUE))

    # Temperature
    temp_str = f"{weather['temp']:.1f}{temp_unit}"
    feels_str = f"Feels like {weather['feels_like']:.1f}{temp_unit}"
    print(c("  ║", Color.BLUE) +
          f"  🌡  {c(temp_str, temp_color)}  {c(feels_feels := feels_str, Color.GREY)}" +
          " " * max(0, 35 - len(temp_str) - len(feels_str)) +
          c("║", Color.BLUE))

    # Min/Max
    minmax_str = f"  ↓ {weather['temp_min']:.1f}{temp_unit}   ↑ {weather['temp_max']:.1f}{temp_unit}"
    print(c("  ║", Color.BLUE) +
          f"  📊{minmax_str}" +
          " " * max(0, 37 - len(minmax_str)) +
          c("║", Color.BLUE))

    print(c("  ╠══════════════════════════════════════════╣", Color.BLUE))

    # Humidity
    hum_str = f"{weather['humidity']}%"
    print(c("  ║", Color.BLUE) +
          f"  💧 Humidity      : {c(hum_str, Color.CYAN)}" +
          " " * max(0, 22 - len(hum_str)) +
          c("║", Color.BLUE))

    # Wind
    wind_str = f"{weather['wind_speed']} {spd_unit}"
    print(c("  ║", Color.BLUE) +
          f"  💨 Wind Speed    : {c(wind_str, Color.CYAN)}" +
          " " * max(0, 22 - len(wind_str)) +
          c("║", Color.BLUE))

    # Visibility
    vis_str = f"{weather['visibility']} km"
    print(c("  ║", Color.BLUE) +
          f"  👁  Visibility   : {c(vis_str, Color.CYAN)}" +
          " " * max(0, 22 - len(vis_str)) +
          c("║", Color.BLUE))

    print(c("  ╚══════════════════════════════════════════╝", Color.BLUE))
    print()


# ============================================================
#  USER INPUT HELPERS
# ============================================================

def select_unit():
    """
    Ask the user to choose between Celsius and Fahrenheit.
    Returns 'metric' or 'imperial'.
    """
    print(c("\n  🌡  Select Temperature Unit:", Color.BOLD))
    print(f"    {c('1', Color.CYAN)}. Celsius  (°C)")
    print(f"    {c('2', Color.CYAN)}. Fahrenheit (°F)")

    while True:
        choice = input("\n  Enter choice (1/2): ").strip()
        if choice == "1":
            print(c("  ✔ Using Celsius\n", Color.GREEN))
            return "metric"
        elif choice == "2":
            print(c("  ✔ Using Fahrenheit\n", Color.GREEN))
            return "imperial"
        else:
            print(c("  ⚠  Invalid. Enter 1 or 2.", Color.YELLOW))


def get_city_input():
    """
    Prompt user to enter a city name.
    Returns the cleaned city string, or None to quit.
    """
    print(c("  Enter a city name", Color.WHITE) +
          c(" (or 'quit' to exit): ", Color.GREY), end="")
    city = input().strip()

    if city.lower() in ("quit", "q", "exit"):
        return None

    if not city:
        print(c("  ⚠  City name cannot be empty.", Color.YELLOW))
        return ""  # Return empty string to re-prompt

    return city


def print_banner():
    """Print the app welcome banner."""
    print(c("""
  ╔══════════════════════════════════════════════╗
  ║      ⛅  CLI WEATHER APPLICATION             ║
  ║      Real-time weather at your fingertips    ║
  ╚══════════════════════════════════════════════╝
    """, Color.CYAN))


def print_instructions():
    """Print brief usage instructions."""
    print(c("  📋 INSTRUCTIONS:", Color.BOLD))
    print("  • Enter any city name to get live weather data.")
    print("  • You can search multiple cities in one session.")
    print("  • Type 'quit' at any time to exit.")
    print()


def check_api_key():
    """
    Warn the user if the default placeholder API key is still set.
    Exits the program early so they know to fix it first.
    """
    if API_KEY == "YOUR_API_KEY_HERE":
        print(c("\n  ⚠  API KEY NOT SET!\n", Color.RED + Color.BOLD))
        print("  Steps to get your free API key:")
        print(c("  1. Go to → https://openweathermap.org/api", Color.CYAN))
        print("  2. Sign up for a free account")
        print("  3. Go to Profile → 'My API Keys'")
        print("  4. Copy the key and paste it in weather.py:")
        print(c('     API_KEY = "paste_your_key_here"', Color.YELLOW))
        print()
        print(c("  ⏰ Note: New API keys take ~10 minutes to activate.", Color.GREY))
        print()
        sys.exit(0)


# ============================================================
#  MAIN — Program entry point
# ============================================================

def main():
    """
    Main loop — handles multi-city search in a single session.
    """
    print_banner()
    check_api_key()       # Exit early if API key not set
    print_instructions()

    # Step 1: Choose temperature unit (once per session)
    unit = select_unit()

    # Step 2: Multi-city search loop
    while True:
        city = get_city_input()

        # User typed 'quit'
        if city is None:
            print(c("\n  👋 Thanks for using Weather App! Goodbye!\n", Color.CYAN))
            break

        # Empty input — re-prompt
        if city == "":
            continue

        # Step 3: Fetch data from API
        raw_data = get_weather_data(city, unit)

        # If fetch failed, skip display and let user try again
        if raw_data is None:
            continue

        # Step 4: Parse the JSON response
        weather = parse_weather_data(raw_data, unit)

        # Step 5: Display the formatted weather card
        display_weather(weather)

        # Ask if user wants to search another city
        again = input(c("  🔍 Search another city? (y/n): ", Color.CYAN)).strip().lower()
        if again != "y":
            print(c("\n  👋 Thanks for using Weather App! Goodbye!\n", Color.CYAN))
            break
        print()


# Run the app
if __name__ == "__main__":
    main()
