from flask import Blueprint, render_template, request, jsonify
from flask_security import login_required, current_user
from app import db
# from app import utils
from app.models import (Pedido, Cupon, Filial, Segmento, Coop, Vendedor,
                        RoleUser, Role)
from sqlalchemy import text, distinct
from app.utils import Log


pedidos_bp = Blueprint('pedidos', __name__)


# Select o nome do cooperado para o autocomplete do campo nome do cooperado no
# de cadastro de pedidos
@pedidos_bp.route('/autocompletenome', methods=["GET"])
def autocompletenome():
    search = request.args.get('q')
    nome = '{}%'.format(search)

    # ilike para desativar o case sensitive da consulta.
    query = Coop.query.filter(Coop.nome.ilike(nome)).all()
    results = [coop.nome for coop in query]
    return jsonify(matching_results=results)


# Select o nome do vendedor para o autocomplete do campo vendedor de cadastro
# de pedidos
@pedidos_bp.route('/autocompletevendedor', methods=["GET"])
def autocompletevendedor():
    search = request.args.get('q')
    nome = '{}%'.format(search)

    # ilike para desativar o case sensitive da consulta.
    query = Vendedor.query.filter(Vendedor.nome.ilike(nome)).all()
    results = [vendedor.nome for vendedor in query]
    print(results)
    return jsonify(matching_results=results)


@pedidos_bp.route('/pedidos/new')
@login_required
def new():
    user = current_user.get_id()
    user_name = current_user.name

    # Caso o usuário for do grupo 'filial_user', só pode lançar pedido para
    # as filiais a qual pertence na tabela 'filiais_users' (FilialUser)
    if current_user.roles[0].name == 'filial_user':
        print('\n\n elaia')
        filial_id = current_user.filiais[0].id
        filiais = Filial.query.filter_by(id=filial_id).all()
    else:
        filiais = Filial.query.order_by(Filial.nome.asc()).all()

    segmentos = Segmento.query.all()
    return render_template('pedidos_form_add.html', filiais=filiais,
                           segmentos=segmentos, user_name=user_name)


@pedidos_bp.route('/pedidos/edit')
@login_required
def edit():
    user = current_user.get_id()
    user_name = current_user.name
    if user == 'admin':
        return render_template('pedido_edit.html', user_name=user_name)
    else:
        return render_template('acesso_negado.html')


def gera_cupom(valor, segmento_id, pedido):
    " Gera os cupons para concorrer a sorteios"
    valor = float(valor.replace(',', '.'))

    segmento = Segmento.query.get(segmento_id)
    if segmento.valor_cupon == 0:
        # não gera cupons
        return 0
    elif segmento.valor_cupon == 1:
        # gera apenas 1(Um) cupon
        db.session.add(Cupon(pedido=pedido))
        db.session.commit()
        return 1
    else:
        # gera cupons de acordo com o valor do pedido e o valor_cupon
        quantidade = round(valor / segmento.valor_cupon)
        for i in range(quantidade):
            db.session.add(Cupon(pedido=pedido))
        db.session.commit()
        return quantidade


@pedidos_bp.route("/pedidos/new/save", methods=["GET", "POST"])
def new_save():
    if request.method == "POST":
        dados = request.form.to_dict()
        print(dados)
        nomeCooperado = dados['nomeCooperado']  # Nome do cooperado
        nomeVendedor = dados['nomeVendedor']  # Nome do vendedor
        filial_id = dados['filial']  # Códido da filial
        segmento_id = dados['segmento']  # Segmento ex: loja, insumos, nutriçao
        valor = dados['valor']  # Valor do pedido

        Log('func new_save: nomeCooperado: {}'.format(nomeCooperado))
        Log('func new_save: nomeVendedor: {}'.format(nomeVendedor))
        Log('func new_save: filial_id: {}'.format(filial_id))
        Log('func new_save: segmento_id: {}'.format(segmento_id))
        Log('func new_save: valor: {}'.format(valor))

        cooperado = Coop.query.filter_by(nome=nomeCooperado).first()
        Log('func new_save: Coop.query: {}'.format(cooperado))
        vendedor = Vendedor.query.filter_by(nome=nomeVendedor).first()
        Log('func new_save: Vendedor.query: {}'.format(vendedor))
        filial = Filial.query.filter_by(id=filial_id).first()
        Log('func new_save: Filial.query: {}'.format(filial))

        # Caso o usuário pertença ao Role 'filial_user' então é pedido tirado
        # nas lojas, e recebe importado=1
        # Caso não, é pedido tirado na feira e recebe importado=0
        if current_user.roles[0].name == 'filial_user':
            importado = '1'
        else:
            importado = '0'
        Log('func new_save: importado: {}'.format(importado))

        # Verificando se já existe um pedido igual no banco de dados
        checa = Pedido.query.filter_by(
            coop=cooperado,
            vendedor=vendedor,
            valor=valor,
            filial=filial).first()
        Log('func new_save: checa pedido: {}'.format(checa))
        if checa is not None:
            return 'o pedido já existe'
            # return render_template('erro_pedido_duplicado.html',pedido=checa)

        # Incluindo o pedido no banco de dados usando SqlAlchemy
        pedido = Pedido(
            valor=valor,
            importado=importado,
            user=current_user,
            segmento_id=segmento_id,
            vendedor=vendedor,
            coop=cooperado,
            filial=filial)
        Log('func new_save: pedido: {}'.format(pedido))
        db.session.add(pedido)
        Log('func new_save: pedido add: {}'.format(pedido))
        db.session.commit()
        Log('func new_save: pedido add commit: {}'.format(pedido))

        # Gerando cupons
        cupons = gera_cupom(
            valor=valor, segmento_id=segmento_id, pedido=pedido)
        Log('func new_save: gera cupons: {}\n'.format(cupons))

        # Formata o numero do pedido para ficar com 4 digitos
        if pedido.id < 1000:
            idpedido = '{:0>4}'.format(pedido.id)
        else:
            idpedido = pedido.id

        return "Pedido: {}<br> Cupons: {}".format(pedido, cupons)
