from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

# Flask Setup
app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2012-02-28/2012-03-05 <br/>"
        f"/api/v1.0/2012-02-28"
    )

@app.route("/api/v1.0/precipitation")
def precipitation_list():
    """Return precipitaion list in past year"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    ## use dates as global data which can be used across routes
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for d in latest_date:
        dates = d.split('-')

    start_date = dt.date(int(dates[0]), int(dates[1]), int(dates[2]))
    # Calculate the date 1 year ago from the last data point in the database
    twelve_months_ago = query_date = start_date - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    data = session.query(Measurement).filter(Measurement.date <= start_date).\
        filter(Measurement.date >= twelve_months_ago).order_by(Measurement.date.desc()).all()
    
    prcp_list = []
    for record in data:
        details = {"station": record.station,
                   "precipitaion":record.prcp,
                   "date":record.date
                  }
        prcp_list.append(details)
    if (len(prcp_list) > 0): 
        return jsonify(prcp_list)

    return jsonify({"error": f"There is no data available."}), 404

@app.route("/api/v1.0/stations")
def station_list():
    """Return List of distinct stations"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    station_list = []
    active_stations = session.query(Measurement.station).distinct(Measurement.station).all()
    for data in active_stations:
        details = {"name" : data.station}
        station_list.append(details)
    
    if (len(station_list) > 0):
        return jsonify(station_list)
    
    return jsonify({"error": f"There is no data available."}), 404

@app.route("/api/v1.0/tobs")
def temprature_list():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    ## use dates as global data which can be used across routes
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for d in latest_date:
        dates = d.split('-')

    start_date = dt.date(int(dates[0]), int(dates[1]), int(dates[2]))
    # Calculate the date 1 year ago from the last data point in the database
    twelve_months_ago = query_date = start_date - dt.timedelta(days=365)
    data = session.query(Measurement).filter(Measurement.date <= start_date).\
        filter(Measurement.date >= twelve_months_ago).order_by(Measurement.date.desc()).all()
    
    tmp_list = []
    for record in data:
        details = {"station": record.station,
                   "temp":record.tobs,
                   "date":record.date
                  }
        tmp_list.append(details)
    if (len(tmp_list) > 0): 
        return jsonify(tmp_list)

    return jsonify({"error": f"There is no data available."}), 404

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_details_by_date(start, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    if end is None:
        temp_details = session.query(Measurement).filter(Measurement.date >= start).order_by(Measurement.date).all()
    else:
        temp_details = session.query(Measurement).filter(Measurement.date >= start).filter(Measurement.date <= end).order_by(Measurement.date).all()
    details = []
    for td in temp_details:
        details.append({"station" : td.station,
                           "temprature" : td.tobs,
                           "date" : td.date})
    
    return jsonify(details)


#@app.route("/api/v1.0/<start>/<end>")
#def temp_details_by_dates(start, end):
    # Create our session (link) from Python to the DB
 #   session = Session(engine)
    
  #  temp_details = session.query(Measurement).filter(Measurement.date >= start).\
   #     filter(Measurement.date <= end).order_by(Measurement.date).all()
   # details = []
   # for td in temp_details:
   #     details.append({"station" : td.station,
   #                        "temprature" : td.tobs,
   #                        "date" : td.date})
   # return jsonify(details)

if __name__ == "__main__":
    app.run(debug=True)
