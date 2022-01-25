# Bookings API

## Success response

### Any POST handler (i.e. movies/:movie_id/seances) 
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

<pre>400 Bad Request</pre>

#### Body

<pre>"errors": [
    {
      "title": "Validation failed",
      "detail": "'price' is a required property"
    }
  ]</pre>
