from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Configuração para garantir JSON válido
app.config['JSON_AS_ASCII'] = False  # Permite caracteres acentuados
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

try:
    # Tenta ler o CSV com diferentes separadores
    try:
        df = pd.read_csv('backend/Relatorio_cadop.csv', sep=';', encoding='utf-8')
    except:
        df = pd.read_csv('backend/Relatorio_cadop.csv', sep='\t', encoding='utf-8')
    
    # Remove espaços extras nos nomes das colunas
    df.columns = df.columns.str.strip()
    print("CSV carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar CSV: {str(e)}")
    df = pd.DataFrame()

@app.route('/buscar', methods=['GET'])
def buscar_operadoras():
    termo = request.args.get('termo', '').strip().lower()
    
    if not termo:
        return jsonify({"total": 0, "resultados": []})
    
    try:
        if df.empty:
            return jsonify({"error": "Dados não carregados"}), 500
        
        # Busca segura em todas as colunas
        mask = df.apply(
            lambda row: row.astype(str).str.lower().str.contains(termo, na=False)
        ).any(axis=1)
        
        resultados = df[mask]
        
        # Converter para dicionário tratando valores nulos
        resultados_dict = resultados.replace({pd.NA: None, float('nan'): None}).to_dict('records')
        
        # Criar resposta JSON manualmente para garantir formato válido
        response = {
            "total": len(resultados),
            "resultados": resultados_dict
        }
        
        # Converter para JSON e depois de volta para objeto para garantir validação
        json_str = json.dumps(response, ensure_ascii=False)
        valid_json = json.loads(json_str)
        
        return jsonify(valid_json)
        
    except Exception as e:
        print(f"Erro na busca: {str(e)}")
        return jsonify({
            "error": "Erro ao processar busca",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)