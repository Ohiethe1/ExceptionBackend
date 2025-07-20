import logging
from db import init_db, add_user

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

init_db()

users = [
    {"username": "12345678", "password": "password123"},
    {"username": "87654321", "password": "pass456"},
    {"username": "11223344", "password": "mypassword"},
    # add more users here
]

def export_users_to_csv(users, filename='user_logins_backup.csv'):
    import csv
    from werkzeug.security import generate_password_hash
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['username', 'password_hash']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user in users:
                writer.writerow({
                    'username': user['username'],
                    'password_hash': generate_password_hash(user['password'])
                })
        logging.info(f'User login info exported to {filename}')
    except Exception as e:
        logging.error(f'Failed to export users to CSV: {e}')

added_count = 0
exists_count = 0

for user in users:
    try:
        if add_user(user["username"], user["password"]):
            logging.info(f'User {user["username"]} added.')
            added_count += 1
        else:
            logging.warning(f'User {user["username"]} already exists.')
            exists_count += 1
    except Exception as e:
        logging.error(f'Error adding user {user["username"]}: {e}')

logging.info(f'Total users processed: {len(users)}')
logging.info(f'Users added: {added_count}')
logging.info(f'Users already existed: {exists_count}')

export_users_to_csv(users)