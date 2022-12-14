# Formplus test
___

This repository includes the code for the formplus test.

## Retreive code
___

- `git clone https://github.com/Loldozen/formplus.git` 

### Installing
___

- Create a PostgresSQL database following the configurations 
    - `sudo -u postgres psql`
    - `postgres=# create database <database_name>;`
    - `postgres=# create user <user_name> with encrypted password '<password>';`
    - `postgres=# grant all privileges on database <database_name> to <user_name>;`
- ` python3 -m venv venvironment`
- `source venvironment/bin/activate`
- `cd formplus && pip install requirements.txt`
- ` python manage.py makemigrations`
- ` python manage.py migrate`

### Test
___
The api docs is available at `http://127.0.0.1:8000/api/docs/`


## Note
___
- Sample Request for ceeating product
``{
    "name": "iPhone Xr",
    "category": "phones",
    "description": "An old flagship phone",
    "owner": "Ahmad Usman",
    "labels": {
        "0": {
            "type": "color",
            "value": "black",
            "price": 20000,
            "number_in_stock": 300
        },
        "1": {
            "type": "color",
            "value": "blue",
            "price": 25000,
            "number_in_stock": 320
        },
        "2": {
            "type": "color",
            "value": "yellow",
            "price": 30000,
            "number_in_stock": 200
        }
    }
}``
- Sample request body for order creation
``{
    "owner": "ololade",
    "total_amount": 45000,
    "order_state": "carted",
    "variation_and_quantity" : {
        "0": {
            "var_id": "VAR-tL1mB0",
            "quantity": 4
        },
        "1": {
            "var_id": "VAR-XZAT1E",
            "quantity": 1
        }
    }
}``