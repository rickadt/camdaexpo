#!/usr/bin/env python3

from flask import Flask
# from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# from flask_bootstrap import Bootstrap
from flask_security import SQLAlchemyUserDatastore, Security, login_required
from .db import db
from .models import User, Role
# from .admin import configure_admin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'é muito secreto esse bilete ;-)'
app.config['DEBUG'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_PASSWORD_SALT'] = app.config['SECRET_KEY']


db.init_app(app)
migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
# configure_admin(app)


# from .blueprints.login import login_bp
# from .blueprints.home import home_bp
# from .blueprints.pedidos import pedidos_bp
# from .blueprints.lottery import lottery_bp

# login_manager = LoginManager()
# login_manager.init_app(app)

# app.register_blueprint(login_bp)
# app.register_blueprint(home_bp)
# app.register_blueprint(pedidos_bp)
# app.register_blueprint(lottery_bp)


# ao rodas o programa pela primeira vez, verifica se os usuários e grupo de
# usuários existem, se não existem, os cria
@app.before_first_request
def create_admin_user():

    # testa para ver se o usuário Admin existe
    admin = User.query.get(1)
    if admin is None:
        # Cria o usuário admin quando o sistema é executado pela primeira vez
        user_datastore.create_role(name='admin', description='Administrador')
        user_datastore.create_user(
            name='Admin',
            email='admin@local',
            password='Camda@3000',
            roles=['admin'])
        db.session.commit()

        user_datastore.create_role(name='users', description='Usuários')
        user_datastore.create_user(
            name='User 1',
            email='user1',
            password='camda2019',
            roles=['users'])
        user_datastore.create_user(
            name='Filial Adamantina',
            email='filial01',
            password='camda2019',
            roles=['users'])
        db.session.commit()


@app.route('/')
@login_required
def teste():
    return('hello world')


if __name__ == '__main__':
    manager.run()
