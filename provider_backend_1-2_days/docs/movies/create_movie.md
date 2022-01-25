# Movies API

## POST

### POST /movies
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>POST /movies</pre>

#### Body

<pre>{"name":"Test Movie","description":"Test description","image_url":"http://example.com/image.jpeg"}</pre>

### Response

#### Headers

<pre>Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>200 OK</pre>

#### Body

<pre>{
  "data": {
    "id": 3,
    "type": "movies",
    "attributes": {
      "name": "Test Movie",
      "description": "Test description",
      "image_url": "http://example.com/image.jpeg"
    }
  }
}</pre>
