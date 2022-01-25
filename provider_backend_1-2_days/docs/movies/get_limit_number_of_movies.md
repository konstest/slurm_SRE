# Movies API

## GET with max_results params

### GET /movies
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>GET /movies?max_results=1</pre>

#### Query Parameters

<pre>max_results: 1</pre>

### Response

#### Headers

Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>200 OK</pre>

#### Body

<pre>{
  "data": [
    {
      "id": 2,
      "name": "Movie name two",
      "imageUrl": "http://example.com/movies/2.jpg",
      "comingSoon": false
    }
  ]
}</pre>