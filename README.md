## requisitos

* python 3
  - confira a versão usando o comando: `py --version`

* django 5
  - confira a versão usando o comando: `django-admin --version`

* git
  - confira a versão usando o comando: `git -v`

## como executar

Obs: se for windows use **py**, se for linux use **python**

* crie o ambiente virtual

  - use o comando: `py -m venv venv`

* ative o ambiente virtual
  - use um dos seguintes comandos: `venv\Scripts\Activate.ps1` ou `venv\Scripts\activate.bat`
  - use o primeiro comando no power shell
  - use o segundo no prompt do CMDOS

* instale o django
  - use o comando: `py -m pip install django`

* crie a pasta /importar/programa na raiz do repositorio e salve os dados nela

* popule o banco de dados com os dados
  - use o comando: `py manage.py importar_programas`

* prepare as migrações
  - use o comando: `py manage.py makemigrations`

* faça a migração
  - use o comando: `py manage.py migrate`

* crie o administrador
  - use o comando: `py manage.py createsuperuser`

* inicie o servidor
  - use o comando: `py manage.py runserver
