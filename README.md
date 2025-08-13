Astronomical Events Predictor
Project Overview
The Astronomical Events Predictor is a web-based application that predicts tidal intensity and astronomical events (e.g., eclipses, meteor showers, planetary alignments) based on user-provided date and location. It uses ML models and astronomical computations to provide accurate predictions.
•	Backend: Python, Flask
•	Frontend: HTML, CSS (Bootstrap optional)
•	Astronomical Calculations: Skyfield, pvlib
•	ML Models: scikit-learn, pandas
•	ML Features: Lunar phase, Earth-Moon distance, solar & lunar positions, day-of-year

Features
1.	Predict tidal intensity as Low, Moderate, or High.
2.	Predict astronomical events, including:
      o	Event type
      o	Event intensity
      o	Visible location
3.	Compute astronomical parameters:
      o	Lunar phase, altitude, Earth-Moon distance
      o	Solar altitude, azimuth, solar declination
4.	User-friendly web interface for input and output.
5.	Optional: Provides API endpoints for JSON responses.

Requirements
Python 3.8+
Libraries:
    Flask
    pandas
    numpy
    joblib
    skyfield
    pvlib
    scikit-learn
    

Install dependencies using:
pip install -r requirements.txt


Project Structure
Astronomical-Events-Predictor/
│
├── app.py                   # Main Flask application
├── templates/
│   ├── home.html            # Landing page
│   ├── first_page1.html     # Input date & location
│   ├── second_page3.html    # Display tidal & lunar/solar parameters
│   └── result1.html         # Final prediction results
├── static/                  # Optional: CSS/JS files
├── tidal_intensity_model.pkl # ML model for tidal prediction
├── scaler.pkl               # Scaler used for tidal intensity model
├── astronomical_event.pkl   # ML model for astronomical events
├── event_type_encoder.pkl   # Encoder for event type
├── intensity_encoder.pkl    # Encoder for intensity
├── location_encoder.pkl     # Encoder for visible location
├── location.csv             # CSV containing Place, Latitude, Longitude
└── README.txt               # Project documentation

Usage Instructions
Run Flask App
python app.py
Open browser and go to:

http://127.0.0.1:5000/
Home Page: Click “Start Prediction”.

First Page: Enter Date and Location.
The app computes tidal intensity, solar, and lunar parameters.
Second Page: View computed parameters and predict astronomical events.
Result Page: Displays final event type, intensity, and visible location.

How it Works
Input: Date & location from user.

Astronomical Computation:
Calculate day-of-year, solar declination, solar & lunar positions using Skyfield and pvlib.

Tidal Intensity Prediction:
ML model predicts tidal intensity using lunar phase and Earth-Moon distance.

Astronomical Event Prediction:
ML model predicts event type, intensity, visible location based on features.
Output: Display all predictions on result page.

Notes
Make sure location.csv contains all location names with exact spelling.
Ensure ML models (.pkl) and encoders are trained and saved before running the app.
For large date ranges, Skyfield computations may take a few seconds.
Optional: Use session storage to handle intermediate data for cleaner URLs.

Future Improvements
Autocomplete for location input.
Add graphical visualization (moon phases, sun paths).
Deploy on Heroku or Docker for cloud access.
Add API endpoint for programmatic access: /api/predict.
Enhance ML model with more features (other planetary positions, time series models).

Author
Shashi Madari
Email: shashimadari44@gmail.com
