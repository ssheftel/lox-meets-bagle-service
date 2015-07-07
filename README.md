#lox-meets-bagel-service


##Python Virtualenv

1. `virtualenv venv`
2. `source venv/bin/activate`

##Python virtualenvwraper

1. `mkvirtualenv lox-meets-bagel-service`
2. `workon lox-meets-bagel-service`
3. `pip freeze > requirements.txt`
4. `pip install -r requirements.txt`

#runpip

1. `chmod +x runpip`
2. `chmod +x start`

#Running Localy

1. `pip install honcho`
2. `honcho start `

#Symlinking to frontend

1. `cd ~/********/lox-meets-bagel-service/app`
2. `ln -s ../../lox-meets-bagel-web/www static`


#Heroku Notes

##Setup
1. `heroku create lox-meets-bagel-service`
2. `git push heroku master`
3. `heroku ps:scale web=1`
4. `heroku open`
5. `heroku logs`
6. `heroku run python`

##Setting Env Vars
1. `heroku config:set WEB_CONCURRENCY=3`

#Data Modle

##AppConfig
- name StringField, required, uneque
- value StringField, default=''
- bool BooleanField, default=True

#API Brainstorm

##Objects

- `UserSummary`
    - `{first_name: 'first', last_name: 'L' id: 123, has_photo: False}`
- `MatchedUserSummary`
    - {first_name: 'first', last_name: 'last'  id: 123, email: 'first.last@aol.com'}


##User

- `GET /user?gender=M` -> `[]UserSummary`
- `GET /user/{userId}` -> `UserObj` but must be self or admin user
- `POST /user` -> UserObj
    - creates a new user
    - must be admin
- `PUT /user/reissue` ->
    - {email}
    - no auth required


-------------------------------------


- `PUT /user/{userId}` -> UserObj
    - edits a user
    - must be either the user or a admin
- `DELETE /user/{userId}` -> 204
    - Deleates a user
    - must be admin
- `DELETE /user` -> deletes all users
    - must be admin

##Profile

`POST /profile/photo`
`POST /profile/bio`


##Likes

- `GET /user/{userId}/like` -> []user_id
- `POST,PUT /user/{userId}/like/{userId}` -> []user_id
- `POST,PUT /user/{userId}/dislike/{userId}`

##Matches

- `GET /user/{userId/match` -> {userId: MatchedUserSummary}
