#add all imports
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#set up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base=automap_base()
Base.prepare(engine, reflect=True)
#make classes for each of the tables
Measurement = Base.classes.measurement
Station= Base.classes.station
#set up flask
app = Flask(__name__)

#routes
@app.route("/")
def welcome():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>" 
        f"/api/v1.0/<start>/<end>"

    )

@app.route("/api/v1.0/precipitation")
def percipitation():
    session = Session(engine)
    dates = session.query(Measurement.date).order_by(Measurement.date.desc()).all()
    date_most_recent =dates[0]
    year_before_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_percp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_before_recent).order_by(Measurement.date).all()
    session.close()

    percipitation_total = []
    for result in year_percp:
        row = {}
        row["date"] = result[0]
        row["prcp"] = result[1]
        percipitation_total.append(row)
    return jsonify(percipitation_total)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)

    station_activity = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc())
    most_active=station_activity[0][0]
    year_before_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_tobs = session.query(Measurement.tobs).\
    filter(Measurement.station == most_active).\
    filter(Measurement.date >= year_before_recent).\
    order_by(Measurement.date.desc()).all()
    session.close()
    all_temps = list(np.ravel(most_active_tobs))
    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def end_date(startdate=None,enddate = None):
    session = Session(engine)
    sel=[func.min(Measurement.tobs),
    func.max(Measurement.tobs),
    func.avg(Measurement.tobs)]
    if not enddate:
        startdate=dt.datetime.strptime(startdate, "%Y%m%d")
        results=session.query(*sel).filter(Measurement.date >= startdate).all()
        temps=list(np.ravel(results))
        return jsonify(results) 
        session.close()
    Else:
        results= session.query(*sel).filter(Measurement.date >= startdate, Measurement.date <= enddate).all() 
        temps = list(np.ravel(results))
        return jsonify(temps)
        session.close()  
    

if __name__ == '__main__':
    app.run(debug=True)