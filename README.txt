# Chicago (ORD)ata

This library is for accessing Chicago related data via Python.  I'd prefer to focus on web APIs but I'm gonna go where the data is.

## CTA Traintracker

To start, I'm implementing Train Tracker API.

    import cta
    train = cta.Train(key='YOURKEYHERE')
    train.arrivals(mapid=40380)

I intend to make the data more well formed and parsed, validated etc later.  It implements a thin little caching layer to conserve API usage.

This is a quick wrapper around http://www.transitchicago.com/assets/1/developer_center/cta_Train_Tracker_API_documentation_v1_2.pdf

To add:

* Station/Stop listings
* Finding closest stations by lat/long, line, name, etc
* Unit testing for all of above
* Relate responses and requests on the arrivals API to my object hierarchy
* Color codes on lines
* Directionality of lines
* Determine 'next' stops for each stop (platform)

# Dependencies

* git://github.com/martinblech/xmltodict.git
* Everything in requirements.txt
