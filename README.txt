(1) Deploy

Development
Proxy.py(web:80) --- django(backend:8000)
                  |
                  +- vue + node(frontend:8080)

Production
Nginx(web:80) --- django(backend:8000) --- MariaDB
               |
               +- vue(frontend:8080)


(2) Setup of Django backend
python3 -m venv venv
source ./venv/bin/activate
pip install django
pip install djangorestframework
pip install django-cors-headers
python manage.py createsuperuser
python manage.py makemigrations
python manage.py migrate

(3) Setup of Vue frontend
brew install node
npm install -g vue-cli
vue init webpack my-project

