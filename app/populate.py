# popula o banco de dados com informações básicas

from flask_security import SQLAlchemyUserDatastore, Security, login_required
from flask_security.utils import encrypt_password
# from . import user_datastore
from .models import User, Role, Filial, Vendedor, Coop
from .db import db
from .vendedores import vendedores
from .cooperados import cooperados

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

# Lista das filiais
filiais = (
    ('LOJA ADAMANTINA', '1', 'lojamatriz@camda.com.br'),
    ('LOJA JUNQUEIRÓPOLIS', '2', 'junqueiropolis@camda.com.br'),
    ('LOJA PACAEMBU', '3', 'pacaembu@camda.com.br'),
    ('CAFÉ COROMANDEL', '4', 'cafecoromandel@camda.com.br'),
    ('LOJA COROMANDEL', '8', 'coromandel@camda.com.br'),
    ('LOJA ASSIS', '9', 'assis@camda.com.br'),
    ('LOJA JAÚ', '10', 'jau@camda.com.br'),
    ('CAMPO EXPERIMENTAL', '12', 'campoexperimental@camda.com.br'),
    ('LOJA DRACENA', '13', 'dracena@camda.com.br'),
    ('LOJA ARAÇATUBA', '16', 'aracatuba@camda.com.br'),
    ('LOJA TRÊS LAGOAS', '17', 'treslagoas@camda.com.br'),
    ('LOJA ANDRADINA', '23', 'andradina@camda.com.br'),
    ('LOJA PARANAÍBA', '26', 'paranaiba@camda.com.br'),
    ('SILO LAVINIA', '27', 'lavinia@camda.com.br'),
    ('LOJA CAMPO GRANDE', '29', 'campogrande@camda.com.br'),
    ('LOJA LINS', '30', 'lins@camda.com.br'),
    ('LOJA NOVA ANDRADINA', '31', 'novaandradina@camda.com.br'),
    ('LOJA PRESIDENTE PRUDENTE', '32', 'prudente@camda.com.br'),
    ('FÁBRICA ANDRADINA', '33', 'fabricaandradina@camda.com.br'),
    ('LOJA PENÁPOLIS', '34', 'penapolis@camda.com.br'),
    ('LOJA RIO PRETO', '36', 'riopreto@camda.com.br'),
    ('LOJA LENÇÓIS PAULISTA', '37', 'lencois@camda.com.br'),
    ('LOJA BATAGUASSU', '38', 'bataguassu@camda.com.br'),
    ('LOJA RIBAS DO RIO PARDO', '39', 'ribas@camda.com.br'),
    ('LOJA MACATUBA', '40', 'macatuba@camda.com.br'),
    ('LOJA SANTA FÉ DO SUL', '42', 'santafe@camda.com.br'),
    ('LOJA OURINHOS', '43', 'ourinhos@camda.com.br'),
    ('LOJA DOURADOS', '44', 'dourados@camda.com.br'),
    ('LOJA LONDRINA', '45', 'londrina@camda.com.br'),
    ('SILO ANDRADINA', '46', 'siloandradina@camda.com.br'),
    ('LOJA COXIM', '47', 'coxim@camda.com.br'),
    ('LOJA AQUIDAUANA', '48', 'aquidauana@camda.com.br'),
    ('LOJA NAVIRAÍ', '49', 'navirai@camda.com.br'),
    ('CAFÉ JUNQUEIRÓPOLIS', '50', 'cafejunqueiropolis@camda.com.br'),
    ('LOJA ITURAMA', '52', 'iturama@camda.com.br'),
    ('LOJA QUIRINÓPOLIS', '53', 'quirinopolis@camda.com.br'),
    ('LOJA TUPACIGUARA', '56', 'tupaciguara@camda.com.br'),
    ('LOJA CAMBARA', '59', 'cambara@camda.com.br'),
    ('LOJA FRUTAL', '60', 'frutal@camda.com.br'),
    ('LOJA SÃO JOAQUIM DA BARRA', '61', 'saojoaquimdabarra@camda.com.br'),
    ('LOJA MONTE ALEGRE DE MINAS', '65', 'montealegredeminas@camda.com.br'),
    ('LOJA ITUIUTABA', '66', 'ituiutaba@camda.com.br'),
    ('LOJA UBERLÃNDIA', '67', 'uberlandia@camda.com.br'),
    ('LOJA GURINHATÃ', '68', 'gurinhata@camda.com.br'))


def add_admin():
    # cria o usuário admin quando o sistema é executado pela primeira vez
    user_datastore.create_role(name='admin', description='Administrador')
    user_datastore.create_user(
        name='Admin',
        email='admin@local',
        password=encrypt_password('Camda@3000'),
        roles=['admin'])
    db.session.commit()


def add_filiais():
    # Insert as filiais no banco de dados
    for filial in filiais:
        db.session.add(Filial(nome=filial[0], numero=filial[1]))
    db.session.commit()


def add_users():
    # usuário para uso na feira
    # este usuário pode lançar pedidos para todas filiais
    user_datastore.create_role(name='users', description='Usuários')
    user_datastore.create_user(
        name='Usuário 1',
        email='user1@local',
        password=encrypt_password('camda2019'),
        roles=['users'])
    user_datastore.create_user(
        name='Usuário 2',
        email='user2@local',
        password=encrypt_password('camda2019'),
        roles=['users'])
    user_datastore.create_user(
        name='Usuário 3',
        email='user3@local',
        password=encrypt_password('camda2019'),
        roles=['users'])
    db.session.commit()

    # usuário para uso nas filiais
    # este usuários só lança pedido para sua filial
    user_datastore.create_role(
        name='filial_user', description='Usuários de Filiais')

    # adicionar as impressoras
    for f in filiais:
        filial = Filial.query.filter_by(nome=f[0]).first()
        user_datastore.create_user(
            name=f[0], email=f[2], password=encrypt_password('camda2019'),
            roles=['filial_user'], filiais=[filial])
    db.session.commit()


def add_vendedores():
    for vendedor in vendedores:
        filial = Filial.query.filter_by(numero=vendedor[2]).first()
        db.session.add(
            Vendedor(nome=vendedor[1], codigo=vendedor[0], filial=filial))
    db.session.commit()


def add_cooperados():
    for cooperado in cooperados:
        filial = Filial.query.filter_by(numero=cooperado[3]).first()
        db.session.add(Coop(
            nome=cooperado[1], cidade=cooperado[2], matricula=cooperado[0],
            filial=filial))
    db.session.commit()
