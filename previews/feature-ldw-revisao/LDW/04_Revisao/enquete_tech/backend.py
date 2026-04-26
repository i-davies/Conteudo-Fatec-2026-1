# pyright: reportCallIssue=false
from flask import jsonify, request
from flask_cors import CORS
from pydantic import BaseModel, ValidationError

from database import app, db
from models import TecnologiaModel

# Permite o frontend acessar esta API localmente
CORS(app)


class VotoRequest(BaseModel):
    tecnologia: str


@app.route("/api/votos", methods=["GET"])
def buscar_placar():
    tecnologias = TecnologiaModel.query.order_by(TecnologiaModel.nome.asc()).all()
    banco_formatado = {tech.nome: tech.votos for tech in tecnologias}
    return jsonify(banco_formatado)


@app.route("/api/votar", methods=["POST"])
def registrar_voto():
    try:
        dados_validados = VotoRequest(**(request.json or {}))
    except ValidationError:
        return jsonify({"sucesso": False, "mensagem": "Formato invalido"}), 400

    tecnologia_votada = dados_validados.tecnologia
    tech_alvo = TecnologiaModel.query.filter_by(nome=tecnologia_votada).first()

    if tech_alvo:
        tech_alvo.votos += 1
        db.session.commit()
        return jsonify(
            {
                "sucesso": True,
                "mensagem": f"Voto para {tecnologia_votada} computado com sucesso!",
            }
        )

    return jsonify({"sucesso": False, "mensagem": "Tecnologia nao encontrada"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
