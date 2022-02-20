import os

from flask import Flask, request
from flask_jwt import JWT
from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
import json
from datetime import datetime
import hashlib
import bcrypt

print("hashing password")

# db = mysql.connect(
#     host="202.67.14.247",
#     user="ntmc_ccntmc",
#     passwd="0uH7kc6ceEYt",
#     database="ntmc_ccntmc"
# )

db = mysql.connect(
    host="202.67.10.238",
    user="root",
    passwd="dhe123!@#",
    database="ntmc_ccntmc"
)

cursor = db.cursor(dictionary=True)

query = "SELECT id_user_mobile, email, password from user_mobile"

## getting records from the table
cursor.execute(query,)
records = cursor.fetchall()

for x in records:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(x['password'].encode(), salt)
    update_query = "UPDATE user_mobile SET password = %s WHERE email = %s"
    result = cursor.execute(update_query,(hashed,x['email'],))
    db.commit()
    print(x)

