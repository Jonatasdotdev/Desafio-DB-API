from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Isso permitirá chamadas do frontend Vue

# Carrega os dados do CSV
df = pd.read_csv('operadoras.csv', encoding='utf-8', sep=';')

@app.route('/buscar', methods=['GET'])
def buscar_operadoras():
    termo = request.args.get('termo', '')

    if not termo:
        return jsonify([])

    # Filtra as operadoras que contêm o termo em qualquer campo
    resultado = df[df.apply(lambda row: row.astype(str).str.contains(termo, case=False).any(axis=1)]

    return jsonify(resultado.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)