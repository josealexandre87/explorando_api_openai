import json  # Biblioteca usada para manipulação de dados no formato JSON.

import openai  # Biblioteca da OpenAI para interagir com os modelos GPT.
import yfinance as yf  # Biblioteca para acessar dados financeiros, como ações e cotações.
from dotenv import (  # Funções para carregar variáveis de ambiente de um arquivo .env.
    find_dotenv, load_dotenv)

_ = load_dotenv(find_dotenv())  # Carrega as variáveis de ambiente do arquivo .env.

client = openai.Client()  # Instancia a conexão com a API da OpenAI usando a chave carregada da variável de ambiente.


### Função que retorna a cotação histórica de uma ação específica da Bovespa
def retorna_cotacao_acao_historica(ticker, periodo='1mo'): # Define um período padrão de 1 mês
    ticker = ticker.replace('.SA', '') # Remove o sufixo '.SA' se ele estiver presente no ticker
    ticker_obj = yf.Ticker(f'{ticker}.SA') # Cria um objeto do tipo Ticker usando o símbolo fornecido pelo usuário
    hist = ticker_obj.history(period=periodo)['Close'] # Obtém o histórico de preços de fechamento para o período especificado
    hist.index = hist.index.strftime('%Y-%m-%d') # Formata as datas para o formato 'YYYY-MM-DD'
    hist = round(hist, 2) # Arredonda os preços de fechamento para 2 casas decimais
    # Se o número de entradas no histórico for maior que 30, ajusta para intervalos regulares
    if len(hist) > 30:
        slice_size = int(len(hist) / 30)
        hist = hist.iloc[::-slice_size][::-1]
    return hist.to_json() # Retorna o histórico no formato JSON


### Lista de ferramentas que descreve a função disponível para ser chamada pelo GPT
tools = [
    {
        'type': 'function',  # Define que estamos trabalhando com uma função
        'function': {
            'name': 'retorna_cotacao_acao_historica',  # Nome da função que o GPT pode invocar
            'description': 'Retorna a cotação diária histórica para uma ação da Bovespa',  # Descrição da função
            'parameters': {
                'type': 'object',  # Define que os parâmetros serão recebidos em formato de objeto
                'properties': {
                    'ticker': {
                        'type': 'string',  # O tipo de dado do parâmetro ticker
                        'description': 'O ticker da ação. Exemplo: "ABEV3" para Ambev, "PETR4" para Petrobras, etc.'
                    },
                    'periodo': {
                        'type': 'string',  # Tipo do parâmetro periodo
                        'description': 'O período dos dados históricos: "1mo" para 1 mês, "1y" para 1 ano, etc.',
                        'enum': ["1d", "5d", "1mo", "6mo", "1y", "5y", "10y", "ytd", "max"]  # Valores permitidos
                    }
                }
            }
        }
    }
]

### Dicionário que mapeia o nome da função para a própria função
funcoes_disponiveis = {'retorna_cotacao_acao_historica': retorna_cotacao_acao_historica}


### Função que gera texto com a interação do modelo GPT, incluindo chamadas de ferramentas
def gera_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens,  # Mensagens que foram trocadas na conversa
        model='gpt-3.5-turbo-0125',  # Modelo utilizado para gerar respostas
        tools=tools,  # Lista de ferramentas disponíveis para o modelo
        tool_choice='auto'  # Define que a escolha de qual ferramenta usar será automática
    )

    tool_calls = resposta.choices[0].message.tool_calls  # Verifica se houve chamadas de ferramentas na resposta

    ### Se houver chamadas de ferramentas, processa cada uma
    if tool_calls:
        mensagens.append(resposta.choices[0].message)  # Adiciona a resposta do modelo à lista de mensagens
        for tool_call in tool_calls:
            func_name = tool_call.function.name  # Nome da função chamada pelo GPT
            function_to_call = funcoes_disponiveis[func_name]  # Mapeia o nome da função à função real
            func_args = json.loads(tool_call.function.arguments)  # Converte os argumentos da função de JSON para Python
            func_return = function_to_call(**func_args)  # Executa a função com os argumentos fornecidos
            mensagens.append({
                'tool_call_id': tool_call.id,  # Adiciona o ID da chamada da ferramenta
                'role': 'tool',  # Define o papel como 'tool' para a resposta da ferramenta
                'name': func_name,  # Nome da função chamada
                'content': func_return  # Resultado da execução da função
            })
        segunda_resposta = client.chat.completions.create(
            messages=mensagens,  # Envia todas as mensagens para o modelo, incluindo a resposta da ferramenta
            model='gpt-3.5-turbo-0125',  # Mesmo modelo utilizado anteriormente
        )
        mensagens.append(segunda_resposta.choices[0].message)  # Adiciona a segunda resposta do modelo às mensagens
    print(f'Assistant: {mensagens[-1].content}') # Exibe a última resposta do assistente (ou GPT) no terminal
    return mensagens  # Retorna as mensagens atualizadas com todas as respostas


### Bloco principal de execução, simulando um chatbot financeiro
if __name__ == '__main__':
    print('Bem-vindo ao ChatBot Financeiro.')  # Mensagem de boas-vindas
    
    while True:  # Loop para continuar recebendo entradas do usuário
        input_usuario = input('User: ')  # Recebe a entrada do usuário
        mensagens = [{'role': 'user', 'content': input_usuario}]  # Cria uma lista de mensagens com a entrada do usuário
        mensagens = gera_texto(mensagens)  # Gera a resposta baseada no GPT e funções disponíveis

