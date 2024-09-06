import openai
from dotenv import find_dotenv, load_dotenv

# Carrega variáveis de ambiente a partir do arquivo .env, como a chave da API
_ = load_dotenv(find_dotenv())

# Cria uma instância do cliente OpenAI para realizar chamadas à API
client = openai.Client()

# Função para gerar respostas do modelo com base nas mensagens fornecidas
def geracao_de_texto(mensagens, model='gpt-3.5-turbo.0125', max_tokens=1000, temperature=0):
    # Envia as mensagens para a API da OpenAI e recebe a resposta em formato de stream (em pedaços)
    resposta = client.chat.completions.create(
        messages=mensagens,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True, # Ativa o modo de streaming para obter a resposta em partes (chunks).
    )  
    
    print('Assintant', end='') # Imprime a indicação de que o assistente está respondendo
    texto_completo = '' # Variável para armazenar a resposta completa
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content # Extrai o conteúdo do pedaço atual
        if texto:
            print(texto, end='')
            texto_completo += texto
    print()
    # Adiciona a resposta completa do assistente na lista de mensagens
    mensagens.append({'role': 'assistent', 'content': texto_completo})
    return mensagens

# Execução principal do chatbot
if __name__ == '__main__':
    
    print('Bem-vindo ao chatBot com Python!')
    mensagens = []
    while True:
        input_usuario = input('User: ')
        mensagens.append({'role': 'user', 'content': input_usuario}) # no caso seria o PROMPT!
        mensagens = geracao_de_texto(mensagens)