# Bookings API

## Success response

### Any handler (i.e. movies/:movie_id/seances) 
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>POST /movies/1/seances</pre>

#### Body

<pre>{"datetime":"2020-01-18T00:00:00.000Z"}</pre>

### Response

#### Headers

<pre>Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>500 Internal Server Error</pre>

#### Body

<pre>"errors": [
    {
      "title": "error: []",
    }
  ]</pre>
