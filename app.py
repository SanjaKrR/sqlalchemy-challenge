# Import the dependencies.
# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Import the datetime module
from datetime import datetime, timedelta

# Import json 
import json

# Define one_year_ago at the top of the script, so it is accessible throughout
one_year_ago = datetime.now() - timedelta(days=365)


#################################################
# Database Setup
#################################################


# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()


# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)


# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session

#################################################
# Flask Setup

app = Flask(__name__)

#################################################


#################################################
# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent, "%Y-%m-%d")
    year_ago = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= year_ago).all()
    session.close()

    precip_data = {date: prcp for date, prcp in results}
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    stations_list = [station[0] for station in results]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Find most active station
    most_active = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()[0]

    most_recent = session.query(func.max(Measurement.date))\
        .filter(Measurement.station == most_active).scalar()
    most_recent_date = dt.datetime.strptime(most_recent, "%Y-%m-%d")
    year_ago = most_recent_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active)\
        .filter(Measurement.date >= year_ago).all()
    session.close()

    temp_data = [{date: tobs} for date, tobs in results]
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    stats = session.query(func.min(Measurement.tobs),
                          func.avg(Measurement.tobs),
                          func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).all()
    session.close()

    result = {
        "Start Date": start,
        "Min Temp": stats[0][0],
        "Avg Temp": round(stats[0][1], 1),
        "Max Temp": stats[0][2]
    }
    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    stats = session.query(func.min(Measurement.tobs),
                          func.avg(Measurement.tobs),
                          func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()
    session.close()

    result = {
        "Start Date": start,
        "End Date": end,
        "Min Temp": stats[0][0],
        "Avg Temp": round(stats[0][1], 1),
        "Max Temp": stats[0][2]
    }
    return jsonify(result)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)