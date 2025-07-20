from db import init_db, add_user

init_db()

users = [
    {"username": "12345678", "password": "password123"},
    {"username": "87654321", "password": "pass456"},
    {"username": "11223344", "password": "mypassword"},
    # add more users here
]

for user in users:
    if add_user(user["username"], user["password"]):
        print(f'User {user["username"]} added.')
    else:
        print(f'User {user["username"]} already exists.')
