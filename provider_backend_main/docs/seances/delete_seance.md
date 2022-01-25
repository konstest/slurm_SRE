# Seances API

## DELETE

### DELETE /movies/:movie_id/seances/:seance_id
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>DELETE /movies/1/seances/1</pre>

#### Body

<pre>{}</pre>

### Response

#### Headers

<pre>Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>200 OK</pre>

#### Body

<pre>{
  "data": [
    {
      "id": "1",
      "type": "seances"
    }
  ]
}</pre>
