# Bookings API

## Success response

### POST /bookings
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

 1. <pre>POST /bookings</pre>
 2. <pre>POST /{movie_id}/seances/{seance_id}/bookings</pre>

#### Body

1. <pre>{"email":"hello@test.com","seatsIds":[0],"seance_id":1}</pre>
2. <pre>{"email":"hello@test.com","seatsIds":[0]}</pre>

### Response

#### Headers

Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>200 OK</pre>

#### Body

<pre>{
  "data": [
    0
  ]
}</pre>
