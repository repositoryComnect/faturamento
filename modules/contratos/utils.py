from datetime import datetime

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