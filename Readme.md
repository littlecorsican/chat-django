
# Redis command lines
Set up redis
wsl2
redis-server --version
redis-server
service --status-all  # show all services
sudo systemctl stop redis-server # stop service
default port: 127.0.0.1:6379


# WHAT NEEDS TO BE SETUP
1) Migration
2) Virtual Environment
3) Install Libararies
4) Redis
5) React front end (if you wish to test it)

# HOW TO SET UP
1) Create sql table "chat_db"
2) python manage.py makemigrations message
3) Run python manage.py migrate
4) cd into venv folder
5) create virtual environment by python -m venv venv
6) activate virtual env by cd Scripts and ./activate.ps1 for powershell and activate.bat for command prompt
7) install all the libraries by pip install -r requirements.txt
8) Open new CMD window, set up redis by entering wsl
9) redis-server to start server
10) cd ../../
11) start server by python manage.py runserver



# Useful links
file validation
https://pypi.org/project/django-upload-validator/
https://django-filer.readthedocs.io/en/latest/validation.html#:~:text=django%2Dfiler%20determines%20the%20mime,as%20an%20image%20file%2C%20say%20.
https://docs.djangoproject.com/en/3.2/_modules/django/core/validators/#FileExtensionValidator
https://www.geeksforgeeks.org/fileextensionvalidator-validate-file-extensions-in-django/
https://docs.djangoproject.com/en/5.0/ref/validators/

general tutorial
https://docs.djangoproject.com/en/5.0/intro/tutorial01/

enums
https://medium.com/@bencleary/using-enums-as-django-model-choices-96c4cbb78b2e
https://www.youtube.com/watch?v=GiAHicNFvBU