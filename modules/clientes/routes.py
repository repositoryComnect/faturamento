from flask import Blueprint, jsonify, request


cliente_bp = Blueprint('cliente_bp', __name__)

cliente_bp.route('/criar_cliente', methods=['POST'])
def criar_cliente():
    

    return