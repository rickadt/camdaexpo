#!/usr/bin/env python3

from flask import Flask
# from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# from flask_bootstrap import Bootstrap
from flask_security import SQLAlchemyUserDatastore, Security, login_required
from flask_security.utils import encrypt_password
from .db import db
from .models import User, Role
from .admin import configure_admin
from .populate import (add_admin, add_users, add_filiais, add_vendedores,
                       add_cooperados)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://postgres:camdacpd@localhost:5432/camdaexpo1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'é muito secreto esse bilete ;-)'
app.config['DEBUG'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_PASSWORD_SALT'] = app.config['SECRET_KEY']
app.config['SECURITY_REGISTERABLE'] = False
app.config['SECURITY_TRACKABLE'] = True


db.init_app(app)
migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
configure_admin(app)


# from .blueprints.login import login_bp
# from .blueprints.home import home_bp
from .blueprints.pedidos import pedidos_bp
# from .blueprints.lottery import lottery_bp

# login_manager = LoginManager()
# login_manager.init_app(app)

# app.register_blueprint(login_bp)
# app.register_blueprint(home_bp)
app.register_blueprint(pedidos_bp)
# app.register_blueprint(lottery_bp)


# ao rodas o programa pela primeira vez, verifica se os usuários e grupo de
# usuários existem, se não existem, os cria
@app.before_first_request
def create_admin_user():
    # testa para ver se o usuário Admin existe
    admin = User.query.first()
    print('\n\n\n\t\tadmin:', admin)
    if admin is None:
        # Cria o usuário admin quando o sistema é executado pela primeira vez
        add_admin()

        # adiciona as filiais
        add_filiais()

        # cria os usuários para usu nas filiais e no ModelView_Lancamento
        add_users()

        # adiciona os add_vendedores
        add_vendedores()

        # adiciona os cooperados
        add_cooperados()

@app.route('/')
@login_required
def home():
    return('hello world')


if __name__ == '__main__':
    manager.run()
