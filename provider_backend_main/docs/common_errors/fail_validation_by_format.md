# Bookings API

## Success response

### Any POST handler (i.e. movies/:movie_id/seances) 
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>POST /movies/1/seances</pre>

#### Body

<pre>{"datetime":"IT IS NOT A DATETIMEZ!","price":250}</pre>

### Response

#### Headers

<pre>Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>422 Unprocessable Entity</pre>

#### Body

<pre>"errors": [
    {
      "title": "Validation failed",
      "detail": "'IT IS NOT A DATETIMEZ!' is not a 'datetimez'"
    }
  ]</pre>
