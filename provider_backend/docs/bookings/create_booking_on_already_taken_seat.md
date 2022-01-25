# Bookings API

## 409 response

### POST /bookings
### Request

#### Headers

<pre>Content-Type: application/json</pre>

#### Route

<pre>POST /bookings</pre>

#### Body

<pre>{"email":"hello@test.com","seatsIds":[1],"seance_id":1}</pre>

### Response

#### Headers

Content-Type: application/json; charset=utf-8</pre>

#### Status

<pre>409 Conflict</pre>

#### Body

<pre>{
  "errors": [
    {
      "title": "Seat already taken",
      "detail": "Taken seats: 1"
    }
  ]
}</pre>
