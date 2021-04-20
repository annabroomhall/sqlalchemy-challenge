import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, render_template

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
connection = engine.connect()
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement
session = Session(engine)

hard_date = dt.date(2017, 8 ,23)
year_ago = hard_date - dt.timedelta(days=365)
active_station = "USC00519281"

#Set columns into variable
precip_sel = [Measurement.date, Measurement.prcp]
station_sel = [Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
tobs_sel = [Measurement.date, Measurement.tobs]

#Define variable to calculate min/max/avg of temps
temp_start = [Measurement.date, 
       func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]


# Dictionary 
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    return (
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation <br/>"
    f"/api/v1.0/stations <br/>"
    f"/api/v1.0/tobs <br/>"
    f"/api/v1.0/fromstart/ <br/>"
    "To generate a list of minimum temperature, maximum temperature and average temperature greater than and equal to a particular date, enter the date in the format of yy-mm-dd after the URL above. <br/>"
    f"/api/v1.0/between_dates/ <br/>"
    "To generate a list of minimum temperature, maximum temperature and average temperature for a date range (inclusive), enter the start date followed by the end date separated by a '/' in the format of yy-mm-dd after the URL above. <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    precip_last_year = session.query(*precip_sel).\
        filter(func.strftime(Measurement.date) >= year_ago).all()
    session.close()

    all_precip = list(np.ravel(precip_last_year))   
    return jsonify(all_precip)
       
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(*station_sel).all()    
    session.close()  

    all_stations = list(np.ravel(stations))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs_most_active = session.query(*tobs_sel).\
        filter(Measurement.station == active_station).\
        filter(func.strftime(Measurement.date) >= year_ago).all()
    session.close()

    active_tobs = list(np.ravel(tobs_most_active))   
    return jsonify(active_tobs)
        
@app.route("/api/v1.0/fromstart/<start_date>")
def start(start_date):
    from_start_sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    from_start = (session.query(*from_start_sel).\
                filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).\
                group_by(Measurement.date).\
                order_by(Measurement.date).all())
    session.close()

    from_start_temps = list(np.ravel(from_start))  
    return jsonify(from_start_temps)  

@app.route("/api/v1.0/between_dates/<temp_start>/<temp_end>")
def between(temp_start, temp_end):
    between_dates_sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    between_dates = (session.query(*between_dates_sel).\
                filter(func.strftime("%Y-%m-%d", Measurement.date) >= temp_start).\
                filter(func.strftime("%Y-%m-%d", Measurement.date) <= temp_end).\
                group_by(Measurement.date).\
                order_by(Measurement.date).all())
    session.close()

    between_dates_temps = list(np.ravel(between_dates))  
    return jsonify(between_dates_temps)  


if __name__ == "__main__":
    app.run(debug=True)
