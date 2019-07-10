#!/usr/bin/env python3

from flask import abort, redirect, request, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.form import InlineFormAdmin
from flask_admin.menu import MenuLink
from flask_security import current_user
from flask_security.utils import encrypt_password
from .models import (
    User, Role, Filial, Sorteio, Coop, Vendedor, Pedido, Segmento, Cupon)
from .db import db

# admin = Admin(
#     name='TimeTracker',
#     template_mode='bootstrap3',
#     base_template='admin_base.html')
admin = Admin(name='Camda Expo', template_mode='bootstrap3')
admin.add_link(MenuLink(name='Pedidos', category='', url="/pedidos"))


class ModelView_Filial(ModelView):
    form_columns = ['nome', 'numero']

    def is_accessible(self):
        return current_user.has_role('admin')


class ModelView_Vendedor(ModelView):
    form_columns = ['nome', 'codigo', 'filial']

    column_labels = dict(codigo='Código')

    def is_accessible(self):
        return current_user.has_role('admin')


class ModelView_Coop(ModelView):
    form_columns = ['nome', 'cidade', 'matricula', 'cpf', 'filial']

    def is_accessible(self):
        return current_user.has_role('admin')


class ModelView_Segmento(ModelView):
    form_columns = ['nome', 'valor_cupon']
    column_descriptions = dict(valor_cupon='''
    Gera cupons a cada X reais do pedido, ex: se valor_cupon = 1.000 reais, um
    pedido de 10.000 reais irá gerar 10 cupons <br />
    - 0 para não gerar cupon <br />
    - 1 para gerar apenas um cupon por pedido''')

    def is_accessible(self):
        return current_user.has_role('admin')


class ModelView_Pedido(ModelView):
    form_columns = ['valor', 'importado', 'segmento', 'vendedor', 'coop',
                    'filial', 'user']

    column_descriptions = dict(importado="0=Não e 1=Sim")
    # form_choices = {
    #     'importado': [(0, 'Não'), (1, 'Sim')]
    # }

    def is_accessible(self):
        return current_user.has_role('admin')


class ModelView_Sorteio(ModelView):
    can_delete = False

    form_columns = ['nome', 'premio', 'quem_participa']

    form_choices = {
        'quem_participa': [
            ('todos', 'Todos'),
            ('nao_sorteados', 'Não sorteados')]
    }

    def is_accessible(self):
        return current_user.has_role('admin')


class ModelView_Conta(ModelView):
    form_columns = ['descricao', 'tipo']

    # Opções para formulário
    form_choices = {
        'tipo': [
            ('carteira', 'carteira'),
            ('investimento', 'investimento'),
            ('c_corrente', 'conta corrente'),
            ('c_poupanca', 'conta poupança'),
            ('cartao_credito', 'cartão de crédito')]}

    def is_accessible(self):
        return current_user.has_role('admin')


class ModelView_Lancamento(ModelView):
    form_columns = ['descricao', 'valor', 'operacao', 'data', 'conta']

    # Opções para formulário
    form_choices = {
        'tipo': [
            ('deposito', 'depósito'),
            ('saque', 'saque'),
            ('transferencia', 'transferência'),
            ('rendimento', 'rendimento')
        ],
        'operacao': [
            ('debito', 'débito'),
            ('credito', 'crédito')
        ]}

    def is_accessible(self):
        return current_user.has_role('admin')


class ModelView_Generico(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')


# # Customized inline form handler para SubTarefas
# class InlineModelForm(InlineFormAdmin):
#     form_excluded_columns = ('tarefa',)
#     form_label = 'Sub Tarefas'
#
#     form_widget_args = {
#         'descricao': {
#             'rows': 5
#         }
#     }
#
#     def __init__(self):
#         return super(InlineModelForm, self).__init__(SubTarefa)
#
#
# class TarefaMV(ModelView):
#     form_columns = ['titulo', 'tarefa', 'tipo', 'local', 'data_inicio',
#                     'data_fim']
#     column_default_sort = ('id', True)
#     column_exclude_list = ('data_inicio', 'data_fim',)
#     column_searchable_list = ['titulo']
#     form_widget_args = {
#         'tarefa': {
#             'rows': 5
#         }
#     }
#     inline_models = (InlineModelForm(),)


# Create customized model view class
class SafeModelView(ModelView):

    def is_accessible(self):
        if current_user.is_anonymous:
            return False

        if not current_user.is_active or not current_user.is_authenticated:
            return False
        # if not current_user.has_role('admin'):
        #     return False
        return True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated and not current_user.is_anonymous:
                abort(403)  # denied
            else:
                return redirect(url_for('security.login', next=request.url))


class RoleModelView(SafeModelView):
    def is_accessible(self):
        return current_user.has_role('admin')


class UserModelView(SafeModelView):
    column_display_pk = True
    form_columns = ("name", "email", "active", "password", 'filiais')
    # Don't display the password on the list of Users
    column_exclude_list = ('password', 'confirmed_at')
    form_excluded_columns = ('password',)
    column_auto_select_related = True

    def on_model_change(self, form, model, is_created):
        model.password = encrypt_password(model.password)

    def is_accessible(self):
        return current_user.has_role('admin')


def configure_admin(app):
    admin.init_app(app)
    admin.add_view(ModelView_Filial(Filial, db.session))
    admin.add_view(ModelView_Vendedor(Vendedor, db.session))
    admin.add_view(ModelView_Coop(Coop, db.session))
    admin.add_view(ModelView_Segmento(Segmento, db.session))
    admin.add_view(ModelView_Pedido(Pedido, db.session))
    admin.add_view(ModelView_Sorteio(Sorteio, db.session))
    admin.add_view(ModelView(Cupon, db.session))
    admin.add_view(UserModelView(User, db.session, category='Accounts'))
    admin.add_view(RoleModelView(Role, db.session, category='Accounts'))
