# Seances API

## POST

### POST /movies/:movie_id/seances
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>POST /movies/1/seances</pre>

#### Body

<pre>{"datetime":"2020-01-18T00:00:00.000Z","price":250}</pre>

### Response

#### Headers

<pre>Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>200 OK</pre>

#### Body

<pre>{
  "data": {
    "id": 3,
    "type": "seances",
    "attributes": {
      "datetime": "2020-01-18T00:00:00.000Z",
      "price": 250
    },
    "seats": [
      {
        "id": 0,
        "vacant": true
      },
      {
        "id": 1,
        "vacant": true
      }
    ]
  }
}</pre>
