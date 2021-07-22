import getpass

import click
from flask import Blueprint, current_app


usersbp = Blueprint('users', __name__)


@usersbp.cli.command('create-superuser')
@click.argument("name")
def create_superuser(name):
    print("Enter email:")
    email = input()
    pswd = getpass.getpass(f"""Enter password for user {name}:""")
    user = current_app.user_manager.create_user(**{"username": name, "password": pswd, "email": email})
    current_app.user_manager.add_role(user, "superuser")
    print(f"""Superuser '{name}' created successfully""")
