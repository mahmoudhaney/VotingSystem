## Description
A voting System is an application where the user (a voter) is allowed to vote in a specific election. A voter can vote for the candidate only once, the system will not allow the user to vote a second time. 
The system will allow the admins to add elections and add the candidates’ names and photos (those who are nominated for an election). Admins only have the right to add candidates’ names, photos, and other personal info.

Admins will register the voter’s name by verifying the voter/user through his/her identity proof (and then the admin will register the voter). The candidates added to the system by the admins will be automatically deleted after the completion of an election. 
Admins must add the date on which an election is going to end. Once a user has received the user ID and password from the admin, the user can log in and vote for a candidate from those who are nominated.

The system will allow the user to vote for only one candidate. The system will allow the user to vote once in a particular election. Admins can add any number of candidates when a new election is announced. 
Admins can also view an election’s result by using the election ID. A user can also view an election’s result.

## Technologies
- `Django 5.0.4`
- `Django Rest Framework 3.15.1`
- DB `PostgreSQL`

## Setup
**1. Make sure you have [Docker](https://www.docker.com/) installed on your PC and it's running.**

**2. Clone the repository or download a `ZIP`:**
```bash
git clone https://github.com/mahmoudhaney/VotingSystem.git

```

**3. Navigate to the directory where the application is installed, create a `.env` file with the following variables:**
```
SECRET_KEY = 'type_your_seceret_key_here'

DEV_DB_NAME = 'developmentdb'
DEV_DB_USER = 'postgres'
DEV_DB_PASSWORD = 'developmentpassword'
DEV_DB_HOST = 'postgres'
DEV_DB_PORT = '5432'

PROD_DB_NAME = 'productiondb'
PROD_DB_USER = 'postgres'
PROD_DB_PASSWORD = 'productionpassword'
PROD_DB_HOST = 'postgres'
PROD_DB_PORT = '5432'

EMAIL_HOST_USER = 'test_email@example.com'
EMAIL_HOST_PASSWORD = 'your_email_host_password_here'
```

**4. Run the project in a development environment**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

```

> ⚠ Then, the development server will be started at http://127.0.0.1:8000/

#

## How To Use
After running the server you can use [Postman](https://www.postman.com/downloads/) to try the APIs
1. Open Postman
2. Import the [APIs File](VotingSystem.postman_collection.json) into your workspace
3. Use APIs to add some Users, Categories, Jobs, and Applications

> ⚠ You can choose whatever you want to run the System APIs

## Copyrights
> ⚠ Copyright ©2024 All rights reserved

