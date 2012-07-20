# Chicago (ORD)ata

This library is for accessing Chicago related data via Python.  I'd prefer to focus on web APIs but I'm gonna go where the data is.

## CTA Traintracker

To start, I'm implementing Train Tracker API.

    import cta
    train = cta.Train(apikey='YOURKEYHERE')
    train.arrivals(mapid=40380)

I intend to make the data more well formed and parsed, validated etc later.  It implements a thin little caching layer to conserve API usage.

# Dependencies

* git://github.com/martinblech/xmltodict.git
* Everything in requirements.txt
