#!/usr/bin/env python3
"""Create or update an admin user for the TradeSOS app.

Usage:
  python scripts/create_admin.py --email admin@example.com

If --password is not provided the script will prompt you to enter one securely.
"""
import argparse
import getpass
from app import app, db
from models import User


def main():
    parser = argparse.ArgumentParser(description='Create or update an admin user')
    parser.add_argument('--email', required=True, help='Admin email address')
    parser.add_argument('--password', help='Password (if omitted you will be prompted)')
    args = parser.parse_args()

    email = args.email.strip().lower()
    password = args.password
    if not password:
        password = getpass.getpass('Password: ')
        password2 = getpass.getpass('Confirm password: ')
        if password != password2:
            print('Error: passwords do not match')
            return

    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            print(f'Found existing user {email}, updating role to admin and setting password')
            user.role = 'admin'
            user.set_password(password)
        else:
            print(f'Creating new admin user {email}')
            user = User(email=email, role='admin')
            user.set_password(password)
            db.session.add(user)

        db.session.commit()
        print('Admin user is ready.')


if __name__ == '__main__':
    main()
