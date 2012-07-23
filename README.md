<A name="toc1-0" title="Chicago (ORD)ata" />
# Chicago (ORD)ata

This library is for accessing Chicago related data via Python.  I'd prefer to focus on web APIs but I'm gonna go where the data is.

<A name="toc2-5" title="CTA Traintracker" />
## CTA Traintracker

To start, I'm implementing Train Tracker API.  Below is a cursory usage example.

    import cta
    train = cta.Train(key='YOURKEYHERE')
    # get arrivals for a specific station
    train.arrivals(mapid=40380)

    # get arrivals for every station in the system
    all_arrivals = reduce(lambda a1,a2: a1+a2, [station.arrivals() for station in cta.Station.all])

    # get the run numbers of every active train in the system at the current time
    run_nums = set([arrival.run_number for arrival in all_arrivals])

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

<A name="toc1-36" title="Dependencies" />
# Dependencies

* git://github.com/martinblech/xmltodict.git
* Everything in requirements.txt
