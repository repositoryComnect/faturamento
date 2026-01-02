from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from application.models.models import User, db
from sqlalchemy import func

operadores_bp = Blueprint('operadores_bp', __name__, url_prefix='/operadores')


@operadores_bp.route('/operadores', methods=['GET'])
def listar_operadores():
    """Página HTML de operadores"""
    try:
        operadores = User.query.order_by(User.nome).all()

        print(f'Total operadores: {len(operadores)}')
        return render_template(
            'operadores.html',
            operadores=operadores
        )

    except Exception as e:
        print(f'Erro: {e}')
        return render_template(
            'operadores.html',
            operadores=[],
            error=str(e)
        )

@operadores_bp.route('/insert/operadores', methods=['POST'])
def insert_operadores():
    try:
        form_data = request.form.to_dict()

        nome = form_data.get('nome_operador')
        sobrenome = form_data.get('sobrenome_operador')
        email = form_data.get('email_operador')
        username = form_data.get('username_operador')
        password = form_data.get('password_operador')
        confirm_password = form_data.get('confirm_password_operador')
        perfil = form_data.get('perfil_operador')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username e senha são obrigatórios'
            }), 400

        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'As senhas não conferem'
            }), 400

        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': 'Username já cadastrado'
            }), 400

        novo_operador = User(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            username=username,
            password=password,
            is_admin=True if perfil == '1' else False,
            is_active=True
        )

        db.session.add(novo_operador)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Operador cadastrado com sucesso'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@operadores_bp.route('/operadores/proximo_id', methods=['GET'])
def proximo_id_operador():
    try:
        # Busca o maior ID atual
        ultimo_id = db.session.query(func.max(User.id)).scalar()

        proximo_id = (ultimo_id or 0) + 1

        return jsonify({
            'success': True,
            'proximo_id': proximo_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@operadores_bp.route('/api/operadores', methods=['GET'])
def get_operadores_api():
    try:
        operadores = (
            User.query
            .order_by(User.id.asc())
            .all()
        )

        return jsonify({
            'success': True,
            'operadores': [
                {
                    'id': u.id,
                    'nome': u.nome or '',
                    'sobrenome': u.sobrenome or '',
                    'email': u.email or '',
                    'username': u.username,
                    'is_admin': u.is_admin,
                    'is_active': u.is_active,
                    'created_at': u.created_at.strftime('%d/%m/%Y') if u.created_at else ''
                }
                for u in operadores
            ]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@operadores_bp.route('/procurar/operador', methods=['GET'])
def procurar_operador():
    operador_id = request.args.get('id')

    if not operador_id:
        return jsonify({'success': False, 'message': 'ID não informado'}), 400

    operador = User.query.filter_by(id=operador_id).first()

    if not operador:
        return jsonify({'success': False, 'message': 'Operador não encontrado'}), 404

    return jsonify({
        'success': True,
        'data': {
            'id': operador.id,
            'nome': operador.nome,
            'sobrenome': operador.sobrenome,
            'email': operador.email,
            'username': operador.username,
            'perfil': 1 if operador.is_admin else 2
        }
    })

@operadores_bp.route('/operadores/delete/<int:id_operador>', methods=['POST'])
def delete_operadores(id_operador):
    operador = User.query.get(id_operador)

    if not operador:
        return jsonify({
            'success': False,
            'message': 'Operador não encontrado'
        }), 404

    try:
        operador.is_active = False  # soft delete
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Operador desativado com sucesso'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erro ao excluir operador',
            'error_details': str(e)
        }), 500

@operadores_bp.route('/editar/operadores', methods=['POST'])
def editar_operadores():

    operador_id = request.form.get('id_operador')

    if not operador_id:
        return jsonify({'success': False, 'message': 'ID do operador não informado'}), 400

    operador = User.query.filter_by(id=operador_id).first()

    if not operador:
        return jsonify({'success': False, 'message': 'Operador não encontrado'}), 404

    operador.nome = request.form.get('nome_operador')
    operador.sobrenome = request.form.get('sobrenome_operador')
    operador.email = request.form.get('email_operador')
    operador.username = request.form.get('username_operador')

    perfil = request.form.get('perfil_operador')
    operador.is_admin = True if perfil == '1' else False

    password = request.form.get('password_operador')
    confirm_password = request.form.get('confirm_password_operador')

    if password:
        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'As senhas não coincidem'
            }), 400

        operador.password = password

    try:
        db.session.commit()
        return redirect(url_for('home_bp.render_operadores'))
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
