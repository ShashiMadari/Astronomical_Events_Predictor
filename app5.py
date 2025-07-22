from flask import Flask, request, render_template, redirect, url_for, jsonify # type: ignore
import pandas as pd # type: ignore
import joblib # type: ignore
from datetime import datetime, timedelta
from skyfield.api import load, utc, Topos# type: ignore
import numpy as np # type: ignore
from pvlib import solarposition # type: ignore

app = Flask(__name__)

# Function to calculate day of year
def calculate_day_of_year(year, month, day):
    date = datetime(year, month, day)
    return date.timetuple().tm_yday  # Returns the day of the year

# Function to calculate solar declination (δ) using an approximation
def calculate_solar_declination(day_of_year):
    return 23.44 * np.sin(np.radians((360/365) * (day_of_year - 81)))

# Function to calculate solar position (altitude & azimuth)
def calculate_solar_position(year, month, day, latitude, longitude):
    date = datetime(year, month, day)
    solar_pos = solarposition.get_solarposition(pd.Timestamp(date), latitude, longitude)
    return solar_pos['elevation'].iloc[0], solar_pos['azimuth'].iloc[0]

# Function to calculate lunar details (phase, altitude, earth-moon distance)
def calculate_lunar_details(year, month, day, latitude, longitude):
    planets = load('de440s.bsp')
    earth, moon, sun = planets['earth'], planets['moon'], planets['sun']
    ts = load.timescale()
    t = ts.utc(year, month, day)

    observer = earth + Topos(latitude_degrees=latitude, longitude_degrees=longitude)
    moon_pos = observer.at(t).observe(moon).apparent()
    sun_pos = observer.at(t).observe(sun).apparent()

    # Lunar Phase Calculation
    moon_sun_angle = moon_pos.separation_from(sun_pos)
    lunar_phase = 180 - moon_sun_angle.degrees  # 0° = New Moon, 180° = Full Moon

    # Compute altitude and azimuth
    alt, az, d = moon_pos.altaz()
    lunar_altitude = alt.degrees

    # Earth-Moon Distance
    distance_to_moon = moon_pos.distance().km

    return lunar_phase, lunar_altitude, distance_to_moon

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/first', methods=['GET', 'POST'])
def first_page():
    if request.method == 'POST':
        year, month, day = int(request.form['year']), int(request.form['month']), int(request.form['day'])
        location_name = request.form['location']
        date = datetime(year, month, day)

        # Load location data
        location_df = pd.read_csv("location.csv")
        location_data = location_df[location_df['Place'].str.lower() == location_name.lower()]
        if location_data.empty:
            return "Location not found. Please check the name and try again."

        latitude, longitude = location_data['Latitude'].values[0], location_data['Longitude'].values[0]

        # Compute astronomical parameters
        day_of_year = calculate_day_of_year(year, month, day)
        solar_declination = calculate_solar_declination(day_of_year)
        solar_altitude, solar_azimuth = calculate_solar_position(year, month, day, latitude, longitude)
        lunar_phase, lunar_altitude, distance_to_moon = calculate_lunar_details(year, month, day, latitude, longitude)

        # Prepare input data for Tidal Intensity Prediction
        input_data = [[lunar_phase, distance_to_moon]]  # Assuming lunar phase & distance are inputs

        # Load tidal intensity model & scaler
        tidal_model = joblib.load("tidal_intensity_model.pkl")
        scaler = joblib.load("scaler.pkl")  # Load the scaler used during training

        # Normalize input data
        input_scaled = scaler.transform(input_data)
        tidal_intensity_pred = tidal_model.predict(input_scaled)

        # Extract the predicted tidal intensity
        tidal_intensity = tidal_intensity_pred[0]

        # Categorize tidal intensity
        if tidal_intensity < 2.5:
            intensity_category = "Low"
        elif 2.5 <= tidal_intensity < 3.5:
            intensity_category = "Moderate"
        else:
            intensity_category = "High"

        return redirect(url_for('second_page', 
                                year=year, month=month, day=day, location=location_name,
                                day_of_year=day_of_year, solar_declination=solar_declination,
                                solar_altitude=solar_altitude, solar_azimuth=solar_azimuth,
                                lunar_phase=lunar_phase, lunar_altitude=lunar_altitude,
                                distance_to_moon=distance_to_moon,
                                tidal_intensity=tidal_intensity, intensity_category=intensity_category))

    return render_template('first_page1.html')

@app.route('/second', methods=['GET', 'POST'])
def second_page():
    year, month, day = int(request.args['year']), int(request.args['month']), int(request.args['day'])
    location = request.args['location']
    day_of_year = int(request.args['day_of_year'])
    solar_declination = float(request.args['solar_declination'])
    solar_altitude = float(request.args['solar_altitude'])
    solar_azimuth = float(request.args['solar_azimuth'])
    lunar_phase = float(request.args['lunar_phase'])
    lunar_altitude = float(request.args['lunar_altitude'])
    distance_to_moon = float(request.args['distance_to_moon'])
    tidal_intensity = float(request.args['tidal_intensity'])
    intensity_category = request.args['intensity_category']

    if request.method == 'POST':
        # Prepare input data for event prediction
        input_data = [[year, month, day, day_of_year,lunar_phase,solar_declination,lunar_altitude,solar_altitude,distance_to_moon]]

        # Load event prediction model & encoders
        model = joblib.load("astronomical_event.pkl")
        event_type_encoder = joblib.load("event_type_encoder.pkl")
        intensity_encoder = joblib.load("intensity_encoder.pkl")
        location_encoder = joblib.load("location_encoder.pkl")

        # Predict event type, intensity, and visible location
        prediction = model.predict(input_data)
        event_type = event_type_encoder.inverse_transform([prediction[0][0]])[0]
        intensity = intensity_encoder.inverse_transform([prediction[0][1]])[0]
        visible_location = location_encoder.inverse_transform([prediction[0][2]])[0]

        if intensity == "-":
            intensity = "Not Applicable"

        return redirect(url_for('result',
                                year=year, month=month, day=day,
                                event_type=event_type, event_intensity=intensity,
                                visible_location=visible_location))

    return render_template('second_page3.html',
                           year=year, month=month, day=day, location=location,
                           day_of_year=day_of_year, solar_declination=solar_declination,
                           solar_altitude=solar_altitude, solar_azimuth=solar_azimuth,
                           lunar_phase=lunar_phase, lunar_altitude=lunar_altitude,
                           distance_to_moon=distance_to_moon,
                           tidal_intensity=tidal_intensity, intensity_category=intensity_category)

@app.route('/result')
def result():
    year, month, day = request.args['year'], request.args['month'], request.args['day']
    event_type = request.args['event_type']
    event_intensity = request.args['event_intensity']
    visible_location = request.args['visible_location']

    return render_template('result1.html', year=year, month=month, day=day,
                           event_type=event_type, event_intensity=event_intensity,
                           visible_location=visible_location)

if __name__ == '__main__':
    app.run(debug=True)
