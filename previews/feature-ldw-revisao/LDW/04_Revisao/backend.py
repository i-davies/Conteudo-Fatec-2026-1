from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Precisamos permitir que o frontend converse com o backend
CORS(app)

# Memória Volátil: se reiniciar o servidor, zera a votação.
PLACAR = {
    "Flask": 0,
    "FastAPI": 0,
    "Flet": 0
}

@app.route('/api/votos', methods=['GET'])
def buscar_placar():
    """Retorna a situação atual das votações"""
    return jsonify(PLACAR)

@app.route('/api/votar', methods=['POST'])
def registrar_voto():
    """Recebe um voto do frontend e computa na memória"""
    dados = request.json
    tecnologia = dados.get('tecnologia')
    
    if tecnologia in PLACAR:
        PLACAR[tecnologia] += 1
        return jsonify({"sucesso": True, "mensagem": f"Voto para {tecnologia} computado!"})
    
    return jsonify({"sucesso": False, "mensagem": "Tecnologia não encontrada"}), 404

if __name__ == '__main__':
    # Rodando na porta 5000 para acesso do Frontend
    app.run(debug=True, port=5000)
