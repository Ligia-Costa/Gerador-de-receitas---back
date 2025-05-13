# Imports necessários
from flask import Flask, jsonify, request # Flask, jsonify para formatar resposta, request para acessar dados da requisição
from flask_cors import CORS # Para lidar com Cross-Origin Resource Sharing
from google import genai # Biblioteca para interagir com o modelo Gemini
import os # Módulo para interagir com o sistema operacional (usaremos para variáveis de ambiente)
from dotenv import load_dotenv # Importa a função para carregar .env (se python-dotenv foi instalado)
import json

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# Cria uma instância da aplicação Flask
app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

# Habilita o CORS para a aplicação inteira... Isso permitirá que qualquer origem (qualquer domínio/porta) faça requisições ao seu back-end.
CORS(app)

def criar_receita(ingredientes):

# Cria o prompt para a API Gemini, instruindo-a a gerar a receita com basenos ingredientes fornecidos e a formatar a resposta como JSON.
    prompt = f"""
        Crie uma receita que tenha como base os ingredientes: {ingredientes}.
        Em caso de ingredientes que não sejam culinários, por exemplo, orgãos sexuais, 
        objetos, ignore-os, não gere a receita e alerte o usuário sobre o uso responsável
        da ferramenta de geração de receitas mantendo a mesma estrutura do JSON 
        da receita.
        A receita pode ser doce ou salgada, entrada, prato principal ou sobremesa.
        Dê preferência para receitas de fácil execução.
        Retorne apenas as seguintes informações: o título da receita, o porcionamento, tempo de preparo, ingredientes em tópicos e modo de fazer em ordem.
        Devolva no formato JSON se acordo com o modelo:
        receita = {{
            "titulo": "titulo da receita",
            "porcionamento": "porcionamento da receita"
            "tempo_de_preparo": "45 minutos",
            "ingredientes": [
                "ingrediente 1",
                "ingrediente 2",
                "ingrediente 3"
            ],
            "modo_de_fazer": [
                "modo",
                "de",
                "fazer"
            ]
        }}   
        """
		# Envia a requisição para a API Gemini para gerar o conteúdo da receita.
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt, 
        config={
        "response_mime_type": "application/json",
        }
    )
    
    # Tenta decodificar a resposta da API Gemini como JSON.
    response = json.loads(response.text)
    return response

@app.route('/receita', methods=['POST'])
def make_receita():
    try:
        # Tenta obter os dados da requisição como JSON.
        dados = request.get_json()

        # Valida se a requisição contém um JSON válido.
        if not dados or not isinstance(dados, dict):
            return jsonify({'error': 'Requisição JSON inválida. Esperava um dicionário.'}), 400

        # Obtém a lista de ingredientes do JSON. Se a chave "ingredientes" não existir, usa uma lista vazia como valor padrão.
        ingredientes = dados.get('ingredientes', [])

        # Valida se o campo "ingredientes" é uma lista.
        if not isinstance(ingredientes, list):
            return jsonify({'error': 'O campo "ingredientes" deve ser uma lista.'}), 400

        # Valida se a lista de ingredientes contém pelo menos 3 ingredientes.
        if len(ingredientes) < 3:
            return jsonify({'error': 'São necessários pelo menos 3 ingredientes.'}), 400

        # Chama a função criar_receita para gerar a receita com base nos ingredientes.
        response = criar_receita(ingredientes)

        # Retorna a receita como JSON com o código de status 200 (OK).
        return jsonify(response), 200

    except Exception as e:
        # Se ocorrer algum erro durante o processo, imprime o erro no console e retorna um JSON com a mensagem de erro e o código de status 500.
        print(f"Um erro interno ocorreu na API: {e}")
        return jsonify({'error': str(e)}), 500  # Retorna código 500 para erros internos

if __name__ == '__main__':
    app.run(debug=True)