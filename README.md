# Le club sentinel api

A python falcon api for processing logs from elasticsearch and influxdb.

Aim to be used to make proxy temporary bans using ip score and to provided insight about compromised customers accounts.

## How to

Clone the repo, set the desired dns hostname in ```docker-compose.yml``` for the falcon-api service. Traefik will serve the api for this hostname on port 80.

Set elastic search parameters in ```.env```

Run the containers with ```docker-compose up```

## Using it

Assuming api fqdn is sentinel.service.leclub, you can run a query using a HTTP GET on sentine.service.leclub/abuse to get IP addresses performing unusual activity according to your parameters.

The following url parameters are accepted:
* ```dt_start```: a timestamp utc to define the start of search
* ```dt_end```: a timestamp utc to define the end of search
* ```scan_interval_minutes``` : the time interval for slicing the search
* ```aggr_size```: the n top most requesting ip addresses per slice
* ```max_success_ratio```: the max login success percentage
* ```min_calls```: the minimal calls to the api during a slice

if no parameters are passed in the url, then the defaults apply:
* ```dt_start```: today at 00:00:00
* ```dt_end```: Now
* ```scan_interval_minutes``` : 60
* ```aggr_size```: 100
* ```max_success_ratio```: 0.1
* ```min_calls```: 100

The api returns a report in json format with query parameters, summaries for ip addresses and possible compromised accounts, and a result entry per slicing interval.

