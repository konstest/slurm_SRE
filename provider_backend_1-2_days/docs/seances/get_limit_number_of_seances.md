# Seances API

## GET

### GET /movies/:movie_id/seances
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>GET /movies/1/seances?max_results=2</pre>

#### Query Parameters

<pre>max_results: 2</pre>

### Response

#### Headers

Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>200 OK</pre>

#### Body

<pre>{
  "data": [
    {
      "id": 34,
      "price": 250,
      "datetime": "2020-01-30T00:00:00.000Z",
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
    },
    {
      "id": 2,
      "price": 250,
      "datetime": "2020-01-30T00:00:00.000Z",
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
  ]
}</pre>
