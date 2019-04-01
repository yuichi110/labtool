(1) create venv
python3 -m venv venv

(2) enable venv
source venv/bin/activate

(3) install modules
pip install django
pip install djangorestframework
pip install django-cors-headers
pip install django-background-tasks
pip install requests

(4) migration
python manage.py makemigration
python manage.py migrate

(5) super user
python manage.py createsuperuser

