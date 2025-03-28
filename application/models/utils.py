from settings.extensions import db, bcrypt
from application.models.models import User

user = User.query.filter_by(username="lolegario").first()
if user:
    user.password = bcrypt.generate_password_hash("soladochao").decode('utf-8')
    db.session.commit()
    print("Senha atualizada com sucesso!")