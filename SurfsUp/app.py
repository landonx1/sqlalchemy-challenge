# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# # reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine)

# reflect the tables
# Base.metadata.tables
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# #################################################
# # Flask Setup
# #################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
baseRoute = "/api/v1.0"
route_percip = f"{baseRoute}/precipitation"
route_stations = f"{baseRoute}/stations"
route_tobs = f"{baseRoute}/tobs"
route_start = f"{baseRoute}<start>"
route_startstop = f"{baseRoute}/<start>/<stop>"

@app.route("/")
def index():
    """List all available routes"""
    return (
        f"Available Routes:<br/>"
        f"{route_percip}<br/>"
        f"{route_stations}<br/>"
        f"{route_tobs}<br/>"
        f"{route_start}<br/>"
        f"{route_startstop}"
    )

@app.route(route_percip)
def percip():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {"Date":date,"Precipitation":prcp}
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route(route_stations)
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {"Station":station,"Name":name,"Lat":lat,"Lon":lon,"Elevation":el}
        stations.append(station_dict)

    return jsonify(stations)

@app.route(route_tobs)
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {"Date":date,"Tobs":tobs}
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route(route_start)
def get_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {"Min":min,"Average":avg,"Max":max}
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route(route_startstop)
def get_start_stop(start, stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {"Min":min,"Average":avg,"Max":max}
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


# Run the Flask application
if __name__ == '__main__':
    app.run()
