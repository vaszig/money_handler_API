# **Money Handler API**

_API built in Django framework for economic transactions management. It creates and modifies income and expenses based on date and type of each category. It has been built with minimum third party libraries (without using DRF) and without implementing user authentication._

## How to setup

Install the requirements

> `pip install -r requirements`

Run the migrations

> `python manage.py migrate`

## How to run

> `python manage.py runserver`

## How to run tests

> `python manage.py test`

## CI/CD - Github action

There is a CI/CD pipeline on every push to master branch which tests the code, pushes it to dockerhub and deploys it to heroku if the all previous jobs have passed. The file cicd.yml must be in the root of the project (/.github/workflows/cicd.yml)

## Usage

API can be used via _https://money-handler-api.herokuapp.com/_ (It returns the current balance)
The following urls can be used:

POST Request

- _admin/_  
  admin page (accessed by an admin user)
- _add/_  
  adds an income or an expense based on a positive or negative amount(required fields: amount, category, transaction_at in json format)
- _update/_  
  updates an existing income or expense (required fields: id, amount, category, transaction_at in json format)
- _delete/_  
  deletes an existing income or expense (required fields: id in json format)

GET Request

- _get/income_  
  fetches total income from a date range given (required fields: start_date, end_date in json format)
- _get/expenses_  
  fetches total expenses from a date range given (required fields: start_date, end_date in json format)
- _get/transactions_  
  fetches all transactions from a given date or category (optional fields: transaction_at, category in json format)
