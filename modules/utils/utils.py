from datetime import datetime
import re

def formatar_telefone(numero):
        if not numero:
            return ''
        numero = ''.join(filter(str.isdigit, numero))
        if len(numero) == 11:
            return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"
        elif len(numero) == 10:
            return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"
        return numero

def safe_float(value, default=None):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

def safe_date(value):
        try:
            return value.strftime('%d/%m/%Y') if value else None
        except Exception:
            return None
        

def parse_date(date_str):
            if not date_str:
                return None
            try:
                for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y'):
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                return None
            except Exception:
                return None
            

def formatar_cep(cep):
    """
    Formata um CEP brasileiro no padrão XXXXX-XXX.
    Retorna string vazia se o CEP for inválido ou None.
    """
    if not cep:
        return ''
    
    # Garante que é string
    cep = str(cep)

    # Remove tudo que não for número
    cep_numeros = re.sub(r'\D', '', cep)

    # Verifica se tem 8 dígitos
    if len(cep_numeros) == 8:
        return f"{cep_numeros[:5]}-{cep_numeros[5:]}"
    
    # Se não tiver 8 dígitos, retorna sem alterar
    return cep


def formatar_cpf_cnpj(valor):
    """
    Formata um CPF ou CNPJ automaticamente.

    - CPF (11 dígitos): 000.000.000-00
    - CNPJ (14 dígitos): 00.000.000/0000-00

    Retorna string vazia se o valor for None ou inválido.
    """
    if not valor:
        return ''

    # Garante que é string
    valor = str(valor)

    # Remove tudo que não for número
    numeros = re.sub(r'\D', '', valor)

    if len(numeros) == 11:  # CPF
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    elif len(numeros) == 14:  # CNPJ
        return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
    else:
        # Se não for 11 nem 14 dígitos, retorna o valor original
        return valor