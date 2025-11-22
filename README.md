# 🧬 Game of Life – Visualizador e Gerador de GIFs

Um visualizador interativo do Jogo da Vida de Conway, com editor de matriz, simulação passo a passo e exportação para GIF.
Desenvolvido em Python + PyQt5 + Pillow.

# Demonstração

<div align="center">

![Timeline-1](https://github.com/user-attachments/assets/3c9250cd-0a6c-42c0-ae79-4d2fd080f532)

</div>

# ✨ Sobre o projeto 

Este projeto é uma interface gráfica completa para editar, visualizar e registrar simulações do Jogo da Vida, um autômato celular criado por John Conway.
O objetivo é permitir experimentar padrões, observar comportamentos e gerar GIFs automaticamente das gerações da simulação.

A interface foi construída com PyQt5, e as imagens/frames dos GIFs com Pillow (PIL).

Ele funciona em tela cheia, possui pintura interativa na matriz, botões simples de simulação e uma filmoteca com miniaturas clicáveis dos GIFs gerados.

Uma exploração mais aprofundada pode ser encontrada no paper anexado na pasta docs deste repositório.

# 🖥️ Controles
<div align="center">

<table>
  <tr>
    <th>Ação</th>
    <th>Descrição</th>
  </tr>
  <tr>
    <td>Clique + arrastar</td>
    <td>Pinta células vivas (preto) ou mortas (branco)</td>
  </tr>
  <tr>
    <td>Próxima Geração ⏭️</td>
    <td>Calcula a próxima geração</td>
  </tr>
  <tr>
    <td>Voltar Geração ⏮️</td>
    <td>Reverte uma geração</td>
  </tr>
  <tr>
    <td>GIF 25 Gerações 📷</td>
    <td>Exporta 25 gerações em GIF</td>
  </tr>
  <tr>
    <td>GIF 100 Gerações 🎥</td>
    <td>Exporta 100 gerações</td>
  </tr>
  <tr>
    <td>Filmoteca 💾</td>
    <td>Abre a pasta de GIFs</td>
  </tr>
  <tr>
    <td>Resetar Matriz 🧼</td>
    <td>Limpa tudo para branco</td>
  </tr>
</table>

</div>

# 📁 Organização da pasta gifs

A pasta gifs/ é criada automaticamente.
Ela pode ser aberta pelo botão Filmoteca.

Sempre ficam disponíveis as 4 miniaturas mais recentes no painel lateral.
# 🚀 Instalação (Windows)
## 1. Clone o repositório
```
git clone https://github.com/Vinicius-O-Ferraz/Conway-Simulation-Jogo-da-Vida.git
cd .\Conway-Simulation-Jogo-da-Vida\
```

## 2. Instale as dependências
```
pip install -r requirements.tx
```

## 3. Execute o projeto
```
cd .\src\   
python app.py
```

# 🐧 Instalação (Linux)
## 1. Clone o repositório
```
git clone https://github.com/Vinicius-O-Ferraz/Conway-Simulation-Jogo-da-Vida.git```
cd .\Conway-Simulation-Jogo-da-Vida\
```

## 2. Instale as dependências
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.tx
```

## 3. Execute o projeto
```
cd src
python3 app.py

```
