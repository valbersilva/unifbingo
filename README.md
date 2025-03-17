# Summary
- [Summary](#Summary)
- [Introduction](#Introduction)
- [Getting Started](#Getting-Started)
   - [Tool Installation](#Tool-Installation)
      - [Docker](#Docker)
      - [Python](#Python)
      - [Visual Studio Code](#Visual-Studio-Code)
- [Build and Test](#Build-and-Test)
- [Project Flow](#Project-Flow)
- [Contact Information](#contact-Information)


# Introduction 
Na UniFBV Wyden, na materia de Aplic. em nuvem iot e industria 4.0 foi proposto ser feito um projeto que fosse publicado na nuvem com o objetivo de despertar vontade e curiosidade para novas pessoas aprenderem a programar

# Getting Started
Para iniciar esse projeto, siga as etapas descritas abaixo e siga todo o [README](https://github.com/valbersilva/suape_apc?tab=readme-ov-file)
1. [Tool Installation](#Tool-Installation)
2. [Setting Up Environment](#Setting-Up-Environment)
3. [Setting Up Variables](#Setting-Up-Variables)
## Tool Installation
Existem algumas tecnologias que precisam ser adicionadas para que esse projeto aconteça, aqui estão as principais ferramentas.
### [Docker](https://www.docker.com/)
> Necessário apenas para fazer funcionar na máquina final/principal do projeto.

A outra ferramenta desse projeto é o [docker](https://www.docker.com/), uma plataforma de código aberto que facilita a criação, implantação e execução de aplicativos em contêineres. Os contêineres são pacotes leves e portáteis que incluem tudo o que é necessário para executar um aplicativo, como o código, as bibliotecas e as dependências.
Caso tenha dúvida, acessar o site do docker ou um exemplo que está nos documentos do projeto.
Acessar: [docs docker](docs/docker.md#docs-docker)
### [Python](https://www.python.org/downloads/)
> Necessário também para fazer testes ou executar em máquina local

Existem duas maneiras de instalar o [python](https://www.python.org/downloads/) numa máquina com a versão que você deseja, escolha uma e faça.
1. Você pode instalar o [python](https://www.python.org/downloads/) direto do site oficial, escolher a versão e instalar essa na sua máquina escolhendo o sistema operacional
2. Instalar através do [pyenv](https://github.com/pyenv/pyenv), caso esteja num linux, ou sua versão windows, o [pyenv-win](https://github.com/pyenv-win/pyenv-win).
Após escolher sua maneira de instalar o python e gerenciar a versão em sua máquina, pode seguir para as proximas etapas.
### [Visual Studio Code](https://code.visualstudio.com/Download)
> Necessário apenas para fazer alterações no projeto e para executar em máquina local

Etapa bem simples, apenas entrar no site e instalar o [vscode](https://code.visualstudio.com/Download).
## Setting Up Environment
Após instalar o vscode e instalar o python, precisa organizar o ambiente de desenvolvimento e testes local que você está fazendo.
- Copie o arquivo de [Environment Variables](docs/environment_variables.md#Environment-Variables) e cole no caminho modules/apcmixer. Altere o nome do arquivo de "environment_variables" para ".env".Adicione as variáveis que estão faltantes. Alguns exemplos: email, senha...
- Crie um [Virtual Environment](https://docs.python.org/3/library/venv.html) e ative-o.
- Instale os [requirements](/requirements.txt#requirements) com o comando: ```pip install -r requirements.txt``` - apenas se o venv estiver ativo.
## Setting Up Variables
Para configurar as variáveis e informações de tags e fábrica e sempre manter tudo atualizado, é importante acessar a pasta modules/apcmixer/aux_files e acessar o arquivo [apc_intelligent_mixer_template_suape](modules/apcmixer/aux_files/apc_intelligent_mixer_template_suape.xlsx#apc_intelligent_mixer_template_suape).
Após preencher e atualizar, carregar o arquivo [load_data](modules/apcmixer/load_data.py)

# Build and Test
TODO: Describe and show how to build your code and run the tests. 


# Project Flow
> Fluxo de processo e de predição de pH está no [FIGMA](https://www.figma.com/board/TM4tqkHjtjxsveabQo7ifu/Mixer-APC-Suape---Flow-Chart?node-id=0-1&t=b63Qs3AHErOrL56k-1)

Primeiro detalhe técnico a ser entendido é que esse projeto especificamente é que ele funciona com 2 serviços acontecendo ao mesmo tempo.
1. WebService com DJango
2. Serviço de predição

## WebService com DJango
> O WebService com DJango existe para gerenciar variáveis e parametros de ambiente do projeto.

## Serviço de Maquina
> O serviço de maquina irá iniciar o controlador que hoje pode ser o Predictor ou o Quat.

O serviço de predição inicia pelo [Machine Service](modules/apcmixer/src/services/MachineService.py#Machine-Service) (caso queira estudar o que esse arquivo faz, acesse a [documentation](docs/#documentation))

## load_data.py
> Este arquivo irá ler a base de dados em excel populada pra carregar no banco de dados apontado no arquivo, as informações e fazer com que o sistema funcione. Observe que no
arquivo, ele irá procurar em uma pasta o arquivo correspondente e ira fazer a inserção dos dados a partir de la.

Para uma explicação do template vá em:
TODO:


Espero que isso ajude a entender o que cada função faz! Se precisar de mais detalhes, sinta-se à vontade para perguntar.
# Contact Information

```
Desenvolvido para:
UniFBV Wyden <>
Desenvolvido por:
Contributor: Valber Silva <valber.l.p.silva@gmail.com>

README Author: Valber Silva <valber.l.p.silva@gmail.com>
README Contributor:
```
