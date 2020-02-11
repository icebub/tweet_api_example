
Install
-----------------
pip install -r requirements.txt

Run
-----------------
python q3.py

Documentation
-----------------

- POST /api/users
    Register a new user.
    The body must contain a JSON object that defines username and password fields
    return json result

### 1. /api/tweet/ for authorized user to POST text and one picture
- POST /api/tweet/submit
    Post new tweet and one picture must authorized by token or username password
    The body must contain a form-data
        text : [String]  (tweet text max length 256)
        image : [file]  (image attached)
        use_pic : [true|false]  (tweet has picture to display)
    return json result

### 2. /api/tweet/ be able to edit text and picture
- POST /api/tweet/modify/<int:tweet_id>
    Post existing tweet identify by tweet_id must authorized by token or username password
    The body must contain a form-data
        text : [String]  (tweet text max length 256)
        image : [file]  (image attached)
        use_pic : [true|false]  (tweet has picture to display)
    return json result

### 3. /api/tweet/ be able to search `text` with `icontains` operator
- GET /api/tweet/search/<string:search_text>/<int:limit>    
    Return json object contain tweet specific tweet text.

### 4. /api/tweet/ GET will response with nested payload. Then Frontend will not need to hit
endpoint multiple time
- GET /api/tweet/user/<string:username>/<int:limit>   
    Return json object contain tweet specific user.

- GET /api/users/<int:user_id>
    Return json object contain username.

- GET /api/token
    Return json object contain user token. must authorized by token or username password.


Example
-------

Use command "curl" create new username "ice" password "1234" :
    $ curl -i -X POST -H "Content-Type: application/json" -d "{\"username\":\"ice\",\"password\":\"1234\"}" http://127.0.0.1:5000/api/users

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 53
    Location: http://127.0.0.1:5000/api/users/4
    Server: Werkzeug/1.0.0 Python/3.7.3
    Date: Mon, 10 Feb 2020 12:40:20 GMT
    {
    "message": "successful",
    "username": "ice"
    }


post new tweet :

    $ curl -i -X POST -H "Content-Type: multipart/form-data" -F "use_pic=true" -F "text=test tweet" -F"image=@100.jpg" -u ice:1234  http://127.0.0.1:5000/api/tweet/submit

    HTTP/1.1 100 Continue

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 30
    Server: Werkzeug/1.0.0 Python/3.7.3
    Date: Mon, 10 Feb 2020 12:42:08 GMT

    {
    "message": "successful"
    }

modify tweet :

    $ curl -i -X POST -H "Content-Type: multipart/form-data" -F "use_pic=true" -F "text=test  mod tweet" -F"image=@100.jpg" -u ice:1234  http://127.0.0.1:5000/api/tweet/modify/3

    HTTP/1.1 100 Continue

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 30
    Server: Werkzeug/1.0.0 Python/3.7.3
    Date: Mon, 10 Feb 2020 12:43:44 GMT

    {
    "message": "successful"
    }

search tweet case insensitive for text "tweet" last 3 entry :

    $ curl -i -X GET  http://127.0.0.1:5000/api/tweet/search/tweet/3
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 587
    Server: Werkzeug/1.0.0 Python/3.7.3
    Date: Mon, 10 Feb 2020 13:26:52 GMT

    {
    "data": [
        {
        "id": 14,
        "img_locate": "upload\\100_1581338528.2220085_zklgjvzwll.png",
        "pub_date": "2020-02-10T12:42:08.223009",
        "tweet_text": "test tweet"
        },
        {
        "id": 12,
        "img_locate": "upload\\100_1581335845.7095168_pzurzskkhb.png",
        "pub_date": "2020-02-10T11:57:25.711505",
        "tweet_text": "test tweet from ice2"
        },
        {
        "id": 11,
        "img_locate": "upload\\100_1581335844.2785301_whkmegvwat.png",
        "pub_date": "2020-02-10T11:57:24.279519",
        "tweet_text": "test tweet from ice2"
        }
    ]
    }

get lastest 3 tweet for user "ice" :
    $ curl -i -X GET  http://127.0.0.1:5000/api/tweet/user/ice/3
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 564
    Server: Werkzeug/1.0.0 Python/3.7.3
    Date: Mon, 10 Feb 2020 13:26:23 GMT

    {
    "data": [
        {
        "id": 14,
        "img_locate": "upload\\100_1581338528.2220085_zklgjvzwll.png",
        "pub_date": "2020-02-10T12:42:08.223009",
        "tweet_text": "test tweet"
        },
        {
        "id": 13,
        "img_locate": "upload\\100_1581337064.0230126_ojctyxygwx.png",
        "pub_date": "2020-02-10T12:17:44.025014",
        "tweet_text": "test mod"
        },
        {
        "id": 8,
        "img_locate": "upload\\100_1581322125.8515356_jnnxzvavus.png",
        "pub_date": "2020-02-10T08:08:45.852537",
        "tweet_text": "test tweet"
        }
    ]
    }
