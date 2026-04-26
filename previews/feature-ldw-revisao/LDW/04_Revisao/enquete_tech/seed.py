# pyright: reportCallIssue=false
from database import app, db
from models import TecnologiaModel


with app.app_context():
    tecnologias_iniciais = [
        TecnologiaModel(nome="Flask", votos=0),
        TecnologiaModel(nome="FastAPI", votos=0),
        TecnologiaModel(nome="Flet", votos=0),
    ]

    for tech in tecnologias_iniciais:
        existente = TecnologiaModel.query.filter_by(nome=tech.nome).first()
        if not existente:
            db.session.add(tech)

    db.session.commit()
    print("Seeds inseridos com sucesso!")
