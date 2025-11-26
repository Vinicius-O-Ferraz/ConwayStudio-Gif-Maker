# 🧬 ConwayStudio – Visualizador e Gerador de GIFs do jogo da vida

Um visualizador interativo do Jogo da Vida de Conway e implementação de modelo epidemiológico espacial (SEIRD), com editor de matriz, simulação passo a passo e exportação para GIF.
Desenvolvido em Python + PyQt5 + Pillow.

# Demonstração

<div align="center">

![python-2025-11-26-15-59-45](https://github.com/user-attachments/assets/0686a11d-c0c6-44bb-b0cd-572ee4fd1e4c)

</div>

# ✨ Sobre o projeto 

Este projeto é uma interface gráfica completa para editar, visualizar e registrar simulações do Jogo da Vida, um autômato celular criado por John Conway. O objetivo é permitir experimentar padrões, observar comportamentos e gerar GIFs automaticamente das gerações da simulação.

Em seguida, foi implementado o modelo de simulação epidemiológica espacial. Cujo esquema pode ser visualizado abaixo:

<div align= "center">

<table>
  <tr>
    <td>
      <img width="450" src="https://github.com/user-attachments/assets/dc2c25a3-3eeb-4610-9a5d-0ea99c376b7d" />
    </td>
    <td>
      <table>
        <tr><th>Estado</th><th>Código</th><th>Cor (Nome)</th></tr>
        <tr><td>Suscetível</td><td>0</td><td>branco</td></tr>
        <tr><td>Exposto</td><td>1</td><td>laranja</td></tr>
        <tr><td>Infectado</td><td>2</td><td>vermelho</td></tr>
        <tr><td>Recuperado</td><td>3</td><td>verde</td></tr>
        <tr><td>Morto</td><td>4</td><td>cinza</td></tr>
      </table>
    </td>
  </tr>
</table>
      
</div>




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
    <td>Randomizar Infectados 🔥</td>
    <td>Gera infectados aleatóriamente</td>
  </tr>
  <tr>
    <td>Resetar Matriz 🧼</td>
    <td>Limpa tudo para branco</td>
  </tr>
</table>

</div>

# Exemplo de gif
<div align="center">
  <img src="https://github.com/user-attachments/assets/dd699054-e338-49db-b78e-1056d55c74af" width="500">
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
