# Density Human Counting API Prototype

This is the starting point for an API to return a real time count of people in rooms.

## Running the API

First, you'll need to install Docker.

Once that's up and running, you can do a:

```bash
$ docker-compose up
```

And the API defaults to running on port `9090` on your host machine.

## Sending Test Data

There's a `send_test_data.py` file in the repo. Running that will send each of the lines of the `dpu_data.csv` to the remote server as JSON. It assumes you have requests installed locally. No need to run it inside of your container.

```bash
$ python3 send_test_data.py
```

## Querying Totals for Rooms

Finally, to query a total for one of the rooms, you can just curl the endpoint with the name of the space:

```bash
$ curl http://localhost:9090/v1/room_count/space_b
{
  "human_count": 8
}

```

## Note About Current Implementation / DB Design

Most of the database design is implemented inside of the code already. It's running in the InfluxDB time series database that gets built alongside the main container.

Due to time constraints, the current POC implementation doesn't implement things the "right" way.

Instead of just tagging incoming events with `dpu_id`s, the API should also be tagging doorways for each of the current events.

With this, we no longer need to know if a room's DPU is flipped, because we store the room graph in each of the doorways. [IE a list where the 0th element is the room the unit is facing into. The 1st element would be the -1].

By tagging with doorways, we can keep track and do our queries via doorways over time. A doorway can be removed, but our `SUM` accumulation of all the space's doorways should still with doorways should still work. 

## Tracking at a Specific Time

With the tags for our timestamp, adding or recreating a specific point in time is easy enough. Doorways 'events' are immutable, along with the doorway's graph at a point in time. 

With this, we walk all the history of doorways in order to recreate any specific count in time.

## Working in Production

Something like InfluxDB or Amazon's Redshift as a store for the events over time should work properly.

Using PostgreSQL to track and store the history of the DPUs associated doorways, and rooms will help to recreate and reference the proper history.

Besides this, the obvious load balancer in front of the API to ingest the data, depending on the number of requests.


