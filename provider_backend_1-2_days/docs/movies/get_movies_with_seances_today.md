# Movies API

## GET with_seances params
Getting movies that have seances today
### GET /movies
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>GET /movies?with_seances=true</pre>

#### Query Parameters

<pre>with_seances: true</pre>

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
      "comingSoon": true
    },
    {
      "id": 1,
      "name": "Movie name one",
      "imageUrl": "http://example.com/movies/1.jpg",
      "comingSoon": true
    }
  ]
}</pre>
