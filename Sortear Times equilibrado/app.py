# app.py
from flask import Flask, render_template, request, redirect, url_for
import os
import json
import random

app = Flask(__name__)



def carregar_jogadores(caminho_arquivo='jogadores.json'):
    # Obtenha o caminho absoluto para o diretório do script
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Construa o caminho completo para o arquivo de jogadores
    caminho_arquivo_completo = os.path.join(diretorio_atual, caminho_arquivo)

    try:
        with open(caminho_arquivo_completo, 'r') as file:
            jogadores = json.load(file)
    except FileNotFoundError:
        jogadores = []

    return jogadores

jogadores = carregar_jogadores()  # usa o caminho padrão 'jogadores.json'
# ou
# jogadores = carregar_jogadores(caminho_arquivo='dadosjogadores/jogadores.json')



def salvar_jogadores(jogadores):
  with open('jogadores.json', 'w') as file:
    json.dump(jogadores, file, indent=2)


def criar_tabela_jogadores():
  jogadores = carregar_jogadores()
  salvar_jogadores(jogadores)


def adicionar_jogador(nome, nivel, posicao):
  jogadores = carregar_jogadores()
  jogadores.append({
      "nome": nome.upper(),
      "nivel": nivel,
      "posicao": posicao,
      "status": 'pendente'
  })
  salvar_jogadores(jogadores)


def sortear_times(jogadores):
  # Dividir jogadores por posição
  goleiros = [
      jogador for jogador in jogadores if jogador['posicao'] == 'goleiro'
  ]
  outros_jogadores = [
      jogador for jogador in jogadores if jogador['posicao'] != 'goleiro'
  ]

  # Garantir que os goleiros não caiam no mesmo time
  random.shuffle(goleiros)
  meio_goleiros = len(goleiros) // 2
  goleiros_time1 = goleiros[:meio_goleiros]
  goleiros_time2 = goleiros[meio_goleiros:]

  # Sortear os outros jogadores de forma equilibrada
  random.shuffle(outros_jogadores)
  meio_outros = len(outros_jogadores) // 2
  outros_time1 = outros_jogadores[:meio_outros]
  outros_time2 = outros_jogadores[meio_outros:]

  time1 = goleiros_time1 + outros_time1
  time2 = goleiros_time2 + outros_time2

  # Calcular somatório dos níveis para cada time
  somatorio_niveis_time1 = sum(jogador['nivel'] for jogador in time1)
  somatorio_niveis_time2 = sum(jogador['nivel'] for jogador in time2)

  return {
      "time1": time1,
      "time2": time2,
      "somatorio_niveis_time1": somatorio_niveis_time1,
      "somatorio_niveis_time2": somatorio_niveis_time2
  }


# ...
def realizar_sorteio():
  jogadores = carregar_jogadores()

  # Verificar se há jogadores pendentes
  if any(jogador['status'] == 'pendente' for jogador in jogadores):
    mensagem = "Aguarde até que todos os jogadores confirmem o status."
    return None, mensagem
  else:
    # Filtrar jogadores que estão dentro
    jogadores_dentro = [
        jogador for jogador in jogadores if jogador['status'] == 'dentro'
    ]

    # Ordenar jogadores por posição desejada
    posicoes_desejadas = ['Goleiro', 'Zagueiro', 'Meia', 'Atacante']
    jogadores_dentro.sort(
        key=lambda x: (posicoes_desejadas.index(x['posicao']), x['nivel']))

    # Adicione prints para depuração
    # print("Jogadores dentro:", jogadores_dentro)

    # Dividir jogadores por nota e posição
    jogadores_dentro.sort(key=lambda x: (x['nivel'], x['posicao']))

    # Adicione prints para depuração
    # print("Jogadores ordenados:", jogadores_dentro)

    # Dividir jogadores em dois times, garantindo equilíbrio nas notas e posições
    time1 = jogadores_dentro[::2]
    time2 = jogadores_dentro[1::2]

    # Adicione prints para depuração
    # print("Time 1:", time1)
    # print("Time 2:", time2)

    # Calcular somatório dos níveis para cada time
    somatorio_niveis_time1 = sum(jogador['nivel'] for jogador in time1)
    somatorio_niveis_time2 = sum(jogador['nivel'] for jogador in time2)

    # Adicione prints para depuração
    # print("Somatório Níveis Time 1:", somatorio_niveis_time1)
    # print("Somatório Níveis Time 2:", somatorio_niveis_time2)

    return {
        "time1": time1,
        "time2": time2,
        "somatorio_niveis_time1": somatorio_niveis_time1,
        "somatorio_niveis_time2": somatorio_niveis_time2
    }, None

  #####################


@app.route('/sortear', methods=['POST'])
def sortear():
  times_sorteados, mensagem_erro = realizar_sorteio()

  # Adicione os prints para depuração
  if times_sorteados:
    # print("Time 1:", times_sorteados["time1"])
    # print("Time 2:", times_sorteados["time2"])
    # print("Somatório Níveis Time 1:",
    #       times_sorteados["somatorio_niveis_time1"])
    # print("Somatório Níveis Time 2:",
    #       times_sorteados["somatorio_niveis_time2"])
    return render_template('resultado.html', resultado_sorteio=times_sorteados)
  else:
    # print("Erro no sorteio:", mensagem_erro)
    return render_template('erro_sorteio.html', mensagem_erro=mensagem_erro)


@app.route('/', methods=['GET', 'POST'])
def index():
  criar_tabela_jogadores()

  if request.method == 'POST':
    nome = request.form['nome']
    try:
      nivel = int(request.form['nivel'])
      if not 0 <= nivel <= 10:
        raise ValueError("O nível deve estar entre 0 e 10.")
    except ValueError:
      return "Valor inválido para o nível. Insira um valor entre 0 e 10."

    posicao = request.form['posicao']
    adicionar_jogador(nome, nivel, posicao)

  jogadores = carregar_jogadores()
  return render_template('index.html', jogadores=jogadores)


@app.route('/resetar', methods=['POST'])
def resetar_status():
  jogadores = carregar_jogadores()
  for jogador in jogadores:
    jogador['status'] = 'pendente'
  salvar_jogadores(jogadores)
  return redirect(url_for('index'))


@app.route('/mudar_status/<nome>', methods=['POST'])
def mudar_status(nome):
  jogadores = carregar_jogadores()
  for jogador in jogadores:
    if jogador['nome'] == nome:
      novo_status = request.form.get('novo_status')
      jogador['status'] = novo_status
  salvar_jogadores(jogadores)
  return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=9090)
