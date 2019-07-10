from datetime import datetime
from .db import db
from flask_security import UserMixin, RoleMixin


class Filial(db.Model):
    __tablename__ = 'filiais'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return self.nome

    def __repr__(self):
        return "<Filial(id='{}', nome='{}')>".format(self.id, self.nome)


class Vendedor(db.Model):
    __tablename__ = 'vendedores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    codigo = db.Column(db.String(20))

    filial_id = db.Column(
        db.Integer, db.ForeignKey(Filial.id), nullable=False)
    filial = db.relationship(
        Filial, backref=db.backref('VendedorFilial', lazy=True))

    def __str__(self):
        return self.nome

    def __repr__(self):
        return "<Vendedor(id='{}', nome='{}')".format(self.nome, self.codigo)


class Coop(db.Model):
    __tablename__ = 'coops'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cidade = db.Column(db.String(255))
    matricula = db.Column(db.String(255))
    cpf = db.Column(db.String(255))

    filial_id = db.Column(
        db.Integer, db.ForeignKey('filiais.id'), nullable=False)
    filial = db.relationship(
        Filial, backref=db.backref('CoopFilial', lazy=True))

    def __str__(self):
        return self.nome

    def __repr__(self):
        return "<Coop(id='{}', nome='{}', cidade='{}', matricula='{}', "\
               "cpf='{}')>".format(self.id, self.nome, self.cidade,
                                   self.matricula, self.cpf)


class Segmento(db.Model):
    __tablename__ = 'segmentos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)

    # gera cupons a cada X reais do pedido, ex: se valor_cupon for 1000, um
    # pedido de 10.000 reais irá gerar 10 cupons
    # se for 0 não irá gerar cupons
    # se for 1 irá gerar apenas um cupon por dedido independente do valor
    valor_cupon = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return self.nome

    def __repr__(self):
        return "<Segmento(id='{}', nome='{}', valor_cupon)>".format(
            self.id, self.nome, self.valor_cupon)


class Pedido(db.Model):
    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.DECIMAL(10, 2), nullable=False)

    # sorteado = db.Column(db.Integer())  # excluir
    datahora = db.Column(db.DateTime, default=datetime.utcnow)

    # se 0 foi cadastrado na feira, se 1 foi cadastrado nas lojas
    importado = db.Column(db.Integer())

    # Usuário que cadastrou o pedido
    # usuários de loja só pode ver e editar seus proprios pedidos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('User', lazy=True))

    # Nutrição, Loja, Insumos, etc.
    segmento_id = db.Column(
        db.Integer, db.ForeignKey(Segmento.id), nullable=False)
    segmento = db.relationship(
        Segmento, backref=db.backref('Segmento', lazy=True))

    vendedor_id = db.Column(
        db.Integer, db.ForeignKey('vendedores.id'), nullable=False)
    vendedor = db.relationship(
        Vendedor, backref=db.backref('Vendedor', lazy=True))

    coop_id = db.Column(db.Integer, db.ForeignKey('coops.id'), nullable=False)
    coop = db.relationship(Coop, backref=db.backref('Coop', lazy=True))

    filial_id = db.Column(
        db.Integer, db.ForeignKey('filiais.id'), nullable=False)
    filial = db.relationship(Filial, backref=db.backref('Filial', lazy=True))

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return "<Pedido(id='{}', valor='{}', datahora='{}', importado='{}', "\
               "user_id='{}' vendedor_id='{}', coop_id'{},"\
               " filial_id='{}')>".format(
                   self.id, self.valor, self.datahora, self.importado,
                   self.user_id, self.vendedor_id, self.coop_id,
                   self.filial_id)


# Cupons gerados conforme os pedidos
# um pedido pode ter um ou mais cupons
class Cupon(db.Model):
    __tablename__ = 'cupons'

    id = db.Column(db.Integer, primary_key=True)
    # se o status for 1 participa do sorteio
    ativo = db.Column(db.Integer, default=1)
    sorteado = db.Column(db.Integer)  # quando o cupon é sorteado recebe 1

    pedido_id = db.Column(
        db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    pedido = db.relationship(Pedido, backref=db.backref('Pedido', lazy=True))

    def __repr__(self):
        return "<Cupon(id='{}', ativo='{}', sorteado='{}')>".format(
            self.id, self.ativo, self.sorteado)


# Tabela com os sorteios de prêmios
class Sorteio(db.Model):
    __tablename__ = 'sorteios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255))
    premio = db.Column(db.String(255))  # descrição do premio que será sorteado
    # hora que rodou o sorteio
    # se a hora for NULL então ainda não foi sorteado
    datahora = db.Column(db.DateTime)

    # define se todos os checkins irão participar do sorteio, ou se quem já
    # ganhou algum premio não participa mais
    # -  'TODOS' = todos os checkins participam
    # -  'NAO_SORTEADOS' = somente aqueles que ainda não foram sorteados
    quem_participa = db.Column(db.String(255), default='nao_sorteados')

    # relacionamento com os cupons
    cupon_id = db.Column(db.Integer, db.ForeignKey('cupons.id'), nullable=True)
    cupon = db.relationship(Cupon, backref=db.backref('Cupon', lazy=True))

    def __repr__(self):
        return "<Sorteio(id='{}', nome='{}', premio='{}', datahora='{}')> \
        ".format(self.id, self.nome, self.premio, self.datahora)


# Para controle de pedido_save
# Usuários são vinculados a uma ou mais filiais, e só podem incluir pedidos
# para essas filiais
class FilialUser(db.Model):
    __tablename__ = 'filiais_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('users.id'))
    filial_id = db.Column(
        'filial_id', db.Integer(), db.ForeignKey('filiais.id'))


class RoleUser(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('users.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255), unique=True)

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    login_count = db.Column(db.Integer)
    current_login_at = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)
    roles = db.relationship(
        'Role',
        secondary='roles_users',
        backref=db.backref('users', lazy='dynamic'))
    filiais = db.relationship(
        'Filial',
        secondary='filiais_users',
        backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.name
