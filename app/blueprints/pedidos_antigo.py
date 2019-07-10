from flask import Blueprint, render_template, request, jsonify
from app import db
# from app import utils
from app.models import Pedido, Cupon
from sqlalchemy import text
# from app.utils import get_user_role


pedidos_bp = Blueprint('pedidos', __name__)


# Select o nome do cooperado para o autocomplete do campo nome do cooperado no
# de cadastro de pedidos
@pedidos_bp.route('/autocompletenome', methods=["GET"])
def autocompletenome():
    search = request.args.get('q')
    SQL = text('''SELECT DISTINCT nome FROM coops WHERE nome like "{}%"
ORDER BY nome'''.format(search))
    query = db.engine.execute(SQL)
    # print(query)
    results = [nome[0] for nome in query]
    return jsonify(matching_results=results)


# Select o nome do vendedor para o autocomplete do campo vendedor de cadastro
# de pedidos
@pedidos_bp.route('/autocompletevendedor', methods=["GET"])
def autocompletevendedor():
    search = request.args.get('q')
    SQL = text('''SELECT DISTINCT nome FROM vendedores
WHERE nome like "{}%" ORDER BY nome'''.format(search))
    query = db.engine.execute(SQL)
    results = [nome[0] for nome in query]
    return jsonify(matching_results=results)


@pedidos_bp.route("/pedidos")
@pedidos_bp.route('/pedidos/<int:pagina_num>')
def pedidos(pagina_num=None):
    ppp = 10  # Numero de pedidos por página
    ordem = 'id'  # ordenação do Select

    # Gerar a pagina com os pedidos de acordo com o numero da pagina
    if pagina_num:
        # Paginação de N em N pedidos (N é a variavel ppp)
        if pagina_num > 0:
            pagina_left = pagina_num - 1

        reloadPage = False
        SQL = text("""SELECT    pedidos.id AS id,
                    coops.nome AS nome,
                    pedidos.valor AS valor,
                    filiais.nome AS filial,
                    vendedores.nome AS vendedor
                FROM (((pedidos
                INNER JOIN vendedores ON vendedores.id=pedidos.vendedor_id)
                INNER JOIN coops ON pedidos.coop_id=coops.id)
                INNER JOIN filiais ON filiais.id=pedidos.filial_id)
                ORDER BY {0}
                DESC
                LIMIT {1}, {2}""".format(ordem, pagina_num * ppp, ppp))
        resultado = db.engine.execute(SQL)
    else:
        pagina_num = 0
        pagina_left = 0
        reloadPage = True
        SQL = text("""SELECT	pedidos.id AS id,
                    coops.nome AS nome,
                    pedidos.valor AS valor,
                    filiais.nome AS filial,
                    vendedores.nome AS vendedor
                FROM (((pedidos
                INNER JOIN vendedores ON vendedores.id=pedidos.vendedor_id)
                INNER JOIN coops ON pedidos.coop_id=coops.id)
                INNER JOIN filiais ON filiais.id=pedidos.filial_id)
                ORDER BY {1}
                DESC
                LIMIT 0, {0}""".format(ppp, ordem))
        resultado = db.engine.execute(SQL)
    # else:
        # sql = "SELECT * FROM pedidos ORDER BY idpedidos DESC LIMIT 0, 50"
        # resultado = db.getSelect(sql)

    dados = []
    for i in resultado:
        valor = utils.formata_valor(i[2])
        dados.append((i[0], i[1], valor, i[3], i[4]))

    sql = text("SELECT COUNT(id) FROM pedidos")
    numPedidos = db.engine.execute(sql).first()
    paginas = range(numPedidos[0] // ppp + 1)
    pagina_right = pagina_num + 1
    pages_left = pagina_num - 3
    pages_right = pagina_num + 3

    return render_template(
        'pedidos.html',
        dados=dados,
        numPaginas=paginas,
        reloadPage=reloadPage,
        pagina_left=pagina_left,
        pagina_right=pagina_right,
        pages_left=pages_left,
        pages_right=pages_right,
        pagina_num=pagina_num
    )


@pedidos_bp.route('/pedidos/include')
@pedidos_bp.route('/include')
@pedidos_bp.route('/')
@login_required
def include():
    user = current_user.get_id()
    # print('\ncurrent user: {}'.format(user))
    user_name = current_user.name
    # user_id = current_user.id
    #
    # role_user = get_user_role(user_id)
    # if user_id in role_user:
    #     sorteio = 1
    # else:
    #     sorteio = 0
    # Pega informações das filiais da qual o usuário faz parte.
    filiais = utils.get_filiais(user=user)
    return render_template('include.html', filiais=filiais, user_name=user_name)


@pedidos_bp.route('/pedidos/edit')
@login_required
def edit():
    user = current_user.get_id()
    user_name = current_user.name
    if user == 'admin':
        return render_template('pedido_edit.html', user_name=user_name)
    else:
        return render_template('acesso_negado.html')


@pedidos_bp.route('/pedidos/edit_form', methods=["GET", "POST"])
@login_required
def edit_form():
    user = current_user.get_id()
    user_name = current_user.name

    filiais = utils.get_filiais()

    if request.method == "POST":
        dados = request.form.to_dict()
        n_pedido = dados['n_pedido']
        sql = """
SELECT
    pedidos.idpedidos,
    pedidos.segmento,
    pedidos.valor,
    coop.nome,
    filiais.idfiliais,
    vendedor.nome
FROM (((pedidos
    INNER JOIN coop ON coop.idcoop=pedidos.coop_idcoop)
    INNER JOIN filiais ON filiais.idfiliais=pedidos.filiais_idfiliais)
    INNER JOIN vendedor ON vendedor.idvendedor=pedidos.vendedor_idvendedor)
WHERE idpedidos = {}""".format(n_pedido)
    dados_pedido = db.getOneLine(sql)
    # print(dados_pedido)

    if user == 'admin':
        return render_template('pedido_edit_form.html', user_name=user_name, dados_pedido=dados_pedido, filiais=filiais)
    else:
        return render_template('acesso_negado.html')


@pedidos_bp.route('/pedidos/edit/save', methods=["GET", "POST"])
@login_required
def pedido_update():
    print(request.form.to_dict())


@pedidos_bp.route('/pedidos/visualizar')
@login_required
def visualizar():
    return 'hola'


def gera_cupom(valor, segmento):
    valor = float(valor.replace(',', '.'))

    # Caso não seja separado por segmento utilizar todos
    if segmento == "TODOS":
        teste = valor / 1000
        if teste < 1:
            return 0
        else:
            return round(teste)

    # Caso de loja gera um cupon para cada 500 reais
    if segmento == 'loja':
        teste = valor / 500
        if teste < 1:
            return 0
        else:
            return round(teste)

    # Caso de insumos gera um cupon para cada 10000 reais
    if segmento == 'insumos':
        teste = valor / 10000
        if teste < 1:
            return 0
        else:
            return round(teste)

    # Caso de loja gera um cupon para cada 1000 reais
    if segmento == 'nutricao':
        teste = valor / 1000
        if teste < 1:
            return 0
        else:
            return round(teste)


@pedidos_bp.route("/include/save", methods=["GET", "POST"])
def pedido_save():
    if request.method == "POST":
        dados = request.form.to_dict()
        nome = dados['nome']  # Nome do cooperado
        valor = dados['valor']  # Valor do pedido
        filial = dados['filial']  # Códido da filial
        vendedor = dados['vendedor']  # Nome do vendedor
        # segmento = dados['segmento']  # Segmento ex: loja, insumos, nutriçao
        segmento = "TODOS"  # Estou usando como TODOS, pois não sei se vai separar esse ano

        # verifica se tem "," no valor e subistitui por "."
        if ',' in valor:
            valor = valor.replace(',', '.')
        # formata com 2 casas decimais depois da virgula
        if '.' in valor:
            r, c = valor.split('.')
            valor = '{}.{:0<2}'.format(r, c)
        else:
            valor = '{}.00'.format(valor)

        # Pegando o ID do coopedado
        SQL = text("SELECT id FROM coops WHERE nome = '{}'".format(nome))
        id_coop = db.engine.execute(SQL).first()
        if id_coop is None:
            return render_template('erro.html', coop=nome)

        # Pegando o ID do vendedor
        SQL = text("SELECT id FROM vendedores WHERE nome = '{}'".format(vendedor))
        id_vendedor = db.engine.execute(SQL).first()
        if id_vendedor is None:
            return render_template('erro.html', vendedor=vendedor)

        # Caso o usuário começe com user, então é pedido tirado na reproducamda
        # Caso não, é pedido tirado nas filiais
        user = current_user.get_id()
        if 'user' in user:
            importado = '0'
        else:
            importado = '1'

        # Verificando se já existe um pedido igual no banco de dados
        checa = Pedido.query.filter_by(
            valor=valor,
            importado=importado,
            vendedor_id=id_vendedor[0],
            coop_id=id_coop[0],
            filial_id=filial).first()
        if checa is not None:
            return render_template('erro_pedido_duplicado.html', pedido=checa)
            # print('\n\n\n')
            # print('checa: ', checa)
            # print('valor: ', checa.valor, ' ', valor)
            # print('importado: ', checa.importado, ' ', importado)
            # print('vendedor_id: ', checa.vendedor_id, ' ', id_vendedor[0])
            # print('coop_id: ', checa.coop_id, ' ', id_coop[0])
            # print('coop_id: ', checa.filial_id, ' ', filial)

        # str(checa.valor), str(checa.importado), str(checa.vendedor_id), str(checa.coop_id), str(checa.filial_id)
        # if (str(checa.valor) == str(valor) and
        #     str(checa.importado) == str(importado) and
        #     str(checa.vendedor_id) == str(id_vendedor[0]) and
        #     str(checa.coop_id) == str(id_coop[0]) and
        #     str(checa.filial_id) == str(filial)):
        #     # Começa o IF
        #     print('valor igual')

        # Incluindo o pedido no banco de dados usando SqlAlchemy
        pedido = Pedido(
            valor=valor,
            importado=importado,
            segmento=segmento,
            vendedor_id=id_vendedor[0],
            coop_id=id_coop[0],
            filial_id=filial)
        db.session.add(pedido)
        db.session.commit()
        # print(pedido.id)

        # Gerando cupons
        cupons = gera_cupom(valor, segmento)
        if cupons > 0:
            for c in range(int(cupons)):
                # db.execute("INSERT INTO cupons (ativo, pedidos_idpedidos) VALUES (1, '{}')".format(result))
                db.session.add(Cupon(ativo=1, pedido=pedido))
                db.session.commit()

        # Formata o numero do pedido para ficar com 4 digitos
        if pedido.id < 1000:
            idpedido = '{:0>4}'.format(pedido.id)
        else:
            idpedido = pedido.id

        return render_template('include_save.html', idpedidos=idpedido, cupons=cupons)


@pedidos_bp.route("/pedidos/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        n_pedido = request.form.to_dict()['n_pedido']
        SQL = text("""
SELECT
    pedidos.id,
    pedidos.segmento,
    pedidos.valor,
    coops.nome,
    filiais.nome,
    vendedores.nome
FROM (((pedidos
    INNER JOIN coops ON coops.id=pedidos.coop_id)
    INNER JOIN filiais ON filiais.id=pedidos.filial_id)
    INNER JOIN vendedores ON vendedores.id=pedidos.vendedor_id)
WHERE pedidos.id = {}""".format(n_pedido))
        result = db.engine.execute(SQL).first()
        # print(result)
        return render_template('pedido_delete_confirm.html', dados_pedido=result)
    else:
        return render_template('pedido_delete.html')


@pedidos_bp.route("/pedidos/delete/confirm", methods=["GET", "POST"])
@login_required
def delete_confirm():
    if request.method == "POST":
        idpedido = request.form.to_dict()['idpedido']
        # db.engine.execute(text("DELETE FROM cupons WHERE pedidos_idpedidos = '{}'".format(idpedido)))
        db.engine.execute(text("DELETE FROM pedidos WHERE id = '{}'".format(idpedido)))
        return render_template("pedido_deletado.html", idpedido=idpedido)
