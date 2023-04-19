# Le club sentinel api

A python falcon api for processing logs from elasticsearch and influxdb.

Aim to be used to make proxy temporary bans using ip score and to provided insight about compromised customers accounts.

## How to

Clone the repo, set the desired dns hostname in ```docker-compose.yml``` for the falcon-api service. Traefik will serve the api for this hostname on port 80.

Set elastic search parameters in ```.env```

Run the containers with ```docker-compose up```
