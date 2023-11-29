# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import date


#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    '''List all available api routes'''
    return (
        f'Available routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f"/api/v1.0/start - Modify the URL by replacing 'start' with a date using the format: yyyy-mm-dd<br/>"
        f"/api/v1.0/start/end - Modify this URL by replacing 'start/end' with 'startDate/endDate' using the format: yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    '''Show precipitation data'''

    session = Session(engine) # added session = '' and session.quit() in each route to enable using the same page/route multiple times for queries

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= dt.date(2016, 8, 23), Measurement.date <= dt.date(2017, 8, 23)).all()
    
    precipitation = list(np.ravel(results))

    return(jsonify(precipitation))

    session.quit()

@app.route('/api/v1.0/stations')
def stations():
    '''List of stations in the dataset'''

    session = Session(engine)

    results = session.query(func.distinct(Measurement.station)).all()

    stations = list(np.ravel(results))

    return(jsonify(stations))

    session.quit()

@app.route('/api/v1.0/tobs')
def tobs():
    '''List of temperatures observed in the last year for the most active station'''

    session = Session(engine)

    results =  session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281', Measurement.date >= dt.date(2016, 8, 23), Measurement.date <= dt.date(2017, 8, 23)).all()

    tobs = list(np.ravel(results))

    return(jsonify(tobs))

    session.quit()

@app.route('/api/v1.0/<start>')
def searchFromStart(start):
    '''Temperature stats starting from a certain date'''

    session = Session(engine)
    #startDate = dt.date(int(start[:4]), int(start[5:7]), int(start[8:]))

    def minimumTemp(start):
        results = session.query(func.min(Measurement.tobs).filter(Measurement.date >= start)).all()
        minTemp = list(np.ravel(results))
        return(f'Minimum temperature since {start}: {minTemp} <br/>')

    # avg rounded to 2 decimal points
    def averageTemp(start):
        results = session.query(func.round(func.avg(Measurement.tobs).filter(Measurement.date >= start), 2)).all()
        avgTemp = list(np.ravel(results))
        return(f'Average temperature since {start}: {avgTemp} <br/>')

    def maximumTemp(start):
        results = session.query(func.max(Measurement.tobs).filter(Measurement.date >= start)).all()
        maxTemp = list(np.ravel(results))
        return(f'Maximum temperature since {start}: {maxTemp} <br/>')
    
    return(
        f'Modify the URL by adding a date using the format: yyyy-mm-dd <br/> <br/>'
        f'{minimumTemp(start)} <br/>'
        f'{averageTemp(start)} <br/>'
        f'{maximumTemp(start)} <br/>'
    )
    session.quit()



@app.route('/api/v1.0/<start>/<end>')
def searchWithinRange(start, end):
    '''Temperature stats between a range of two dates'''

    session = Session(engine)
    
    def minimumTemp(start, end):
        results = session.query(func.min(Measurement.tobs).filter(Measurement.date >= start, Measurement.date <= end)).all()
        minTemp = list(np.ravel(results))
        return(f'Minimum temperature between {start} and {end}: {minTemp} <br/>')

    # avg rounded to 2 decimal points
    def averageTemp(start, end):
        results = session.query(func.round(func.avg(Measurement.tobs).filter(Measurement.date >= start, Measurement.date <= end), 2)).all()
        avgTemp = list(np.ravel(results))
        return(f'Average temperature between {start} and {end}: {avgTemp} <br/>')

    def maximumTemp(start, end):
        results = session.query(func.max(Measurement.tobs).filter(Measurement.date >= start, Measurement.date <= end)).all()
        maxTemp = list(np.ravel(results))
        return(f'Maximum temperature between {start} and {end}: {maxTemp} <br/>')
    
    return(
        f"Modify the URL by adding 'startDate/endDate' using the format: yyyy-mm-dd <br/> <br/>"
        f'{minimumTemp(start, end)} <br/>'
        f'{averageTemp(start, end)} <br/>'
        f'{maximumTemp(start, end)} <br/>'
    )
    session.quit()



if __name__ == '__main__':
    app.run(debug=True)