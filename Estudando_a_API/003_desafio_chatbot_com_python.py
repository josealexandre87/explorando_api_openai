import openai
from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())

client = openai.Client()

def geracao_de_texto(mensagens, model='gpt-3.5-turbo.0125', max_tokens=1000, temperature=0):
    resposta = client.chat.completions.create(
        messages=mensagens,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True, # Ativa o modo de streaming para obter a resposta em partes (chunks).
    )  
    
    print('Assintant', end='')
    texto_completo = ''
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            print(texto, end='')
            texto_completo += texto
    print()
    
    mensagens.append({'role': 'assistent', 'content': texto_completo})
    return mensagens

if __name__ == '__main__':
    
    print('Bem-vindo ao chatBot com Python!')
    mensagens = []
    while True:
        input_usuario = input('User: ')
        mensagens.append({'role': 'user', 'content': input_usuario})
        mensagens = geracao_de_texto(mensagens)