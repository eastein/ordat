# Chicago (ORD)ata

This library is for accessing Chicago related data via Python.  I'd prefer to focus on web APIs but I'm gonna go where the data is.

## CTA Traintracker

To start, I'm implementing Train Tracker API.  Below is a cursory usage example.

### To start up, just instantiate an instance of the Train class to initialize the connection to the API.

    >>> import cta
    >>> train = cta.Train(key='YOURKEYHERE')

### Get Arrivals by mapid

    >>> train.arrivals(mapid=40380)
    [Blue Line/Clark/Lake run 139 to O'Hare at 03:00:00, Blue Line/Clark/Lake run 225 to Forest Park at 03:06:52]

### Advanced Mode: Find All Scheduled/Active Runs

    >>> # get arrivals for every station in the system
    >>> all_arrivals = reduce(lambda a1,a2: a1+a2, [station.arrivals() for station in cta.Station.all])
    >>> # get the run numbers of every active train in the system at the current time
    >>> run_nums = set([arrival.run_number for arrival in all_arrivals])
    >>> len(run_nums)
    16

This was run late at night, so it found far less than normal!

### Station Search, Station Arrivals, Stop Arrivals

    >>> # Find a station, and then check its arrivals
    >>> cta.Station.find('Clark/Lake')[0].arrivals()
    [Blue Line/Clark/Lake run 139 to O'Hare at 03:00:00, Blue Line/Clark/Lake run 225 to Forest Park at 03:05:53]
    >>> # Check what lines a station services
    >>> cta.Station.find('Clark/Lake')[0].lines
    [Pink Line, Blue Line, Purple Express Line, Orange Line, Brown Line, Green Line]
    >>> cl_stops = cta.Station.find('Clark/Lake')[0].stops
    >>> cl_stops
    [E-bound Stop Clark/Lake (Inner Loop) at Station Clark/Lake, W-bound Stop Clark/Lake (Outer Loop) at Station Clark/Lake, S-bound Stop Clark/Lake (Forest Pk-bound) at Station Clark/Lake, N-bound Stop Clark/Lake (O'Hare-bound) at Station Clark/Lake]
    >>> cl_stops[-1].arrivals()
    [Blue Line/Clark/Lake run 139 to O'Hare at 03:00:00]

I intend to make the data more well formed and parsed, validated etc later.  It implements a thin little caching layer to conserve API usage for requests for the same information placed in quick succession.

This is a quick wrapper around http://www.transitchicago.com/assets/1/developer_center/cta_Train_Tracker_API_documentation_v1_2.pdf

To add:

* Finding closest stations by lat/long, line, name, etc
* inbuilt code for acquiring data about stop-to-stop transit timings
* ability to understand delays, scheduled stops, faults in the system
* Unit testing for all of above
* Relate responses and requests on the arrivals API to my object hierarchy
* Color codes on lines
* Directionality of lines
* Determine 'next' stops for each stop (platform)

# Dependencies

* git://github.com/martinblech/xmltodict.git
* Everything in requirements.txt

# Tests

    PYTHONPATH=../xmltodict:~/pyenvs/cta/lib/python2.7/site-packages/ nosetests -vv tests

The above is just an example, I'm not sure why virtualenv isn't picking up the requests module just by sourcing activate.
