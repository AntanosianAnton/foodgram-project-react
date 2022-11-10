# Проект «Продуктовый помощник» - Foodgram
Foodgram - Продуктовый помощник. Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
## стек:
- Python
- Django
- Docker
- Nginx
- Подробнее (см. `foodgram/requirements.txt` )
## Workflow
- `build_and_push_to_docker_hub` - Сборка и доставка докер-образов на Docker Hub
- `deploy` - Автоматический деплой проекта на боевой сервер. Выполняется копирование файлов из репозитория на сервер:
- `send_message` - Отправка уведомления в Telegram В репозитории на Гитхабе добавьте данные в `Settings - Secrets - Actions secrets`:
- `DOCKER_USERNAME` - имя пользователя в DockerHub
- `DOCKER_PASSWORD` - пароль пользователя в DockerHub
- `HOST` - адрес сервера
- `USER` - пользователь
- `SSH_KEY` - приватный ssh ключ
- `PASSPHRASE` - кодовая фраза для ssh-ключа
- `DB_ENGINE` - django.db.backends.postgresql
- `DB_NAME` - postgres (по умолчанию)
- `POSTGRES_USER` - postgres (по умолчанию)
- `POSTGRES_PASSWORD` - postgres (по умолчанию)
- `DB_HOST` - db
- `DB_PORT` - 5432
- `SECRET_KEY` - секретный ключ приложения django (необходимо чтобы были экранированы или отсутствовали скобки)
- `ALLOWED_HOSTS` - список разрешенных адресов
- `TELEGRAM_TO` - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
- `TELEGRAM_TOKEN` - токен бота (получить токен можно у @BotFather, /token, имя бота)
При внесении любых изменений в проект, после коммита и пуша
```
git add .
git commit -m "..."
git push
```
запускается набор блоков команд jobs (см. файл backend.yml, т.к. команда `git push` является триггером workflow проекта.
Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone https://github.com/AntanosianAnton/foodgram-project-react
cd backend
```
Создайте и активируйте виртуальное окружение, обновите pip:
```
python3 -m venv venv
. venv/bin/activate
python3 -m pip install --upgrade pip
```
## Как развернуть проект на сервере:
Установите соединение с сервером:
```
ssh username@server_address
```
Обновите индекс пакетов APT:
```
sudo apt update
```
и обновите установленные в системе пакеты и установите обновления безопасности:
```
sudo apt upgrade -y
```
Создайте папку `nginx`:
```
mkdir nginx
```
Отредактируйте файл `nginx/default.conf` и в строке `server_name` впишите IP виртуальной машины (сервера).
Скопируйте подготовленные файлы `docker-compose.yml` и `nginx/default.conf` из вашего проекта на сервер:
```
scp docker-compose.yaml <username>@<host>/home/<username>/docker-compose.yaml
sudo mkdir nginx
scp default.conf <username>@<host>/home/<username>/nginx/default.conf
```
Установите Docker и Docker-compose:
```
sudo apt install docker.io
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```
Проверьте корректность установки Docker-compose:
```
sudo  docker-compose --version
```
На сервере создайте файл .env
```
touch .env
```
и заполните переменные окружения
```
nano .env
```
или создайте этот файл локально и скопируйте файл по аналогии с предыдущим шагом:
```
SECRET_KEY=<SECRET_KEY>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
## После успешного деплоя:
На сервере соберите docker-compose:
```
sudo docker-compose up -d --build
```
Соберите статические файлы (статику):
```
docker-compose exec backend python manage.py collectstatic --no-input
```
Примените миграции:
```
(опционально) docker-compose exec backend python manage.py makemigrations
```
```
docker-compose exec backend python manage.py migrate --noinput
```
Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
## Пользовательские роли в проекте
1. Анонимный пользователь
2. Аутентифицированный пользователь
3. Администратор
## Анонимные пользователи могут:
1. Просматривать список рецептов;
2. Просматривать отдельные рецепты;
3. Фильтровать рецепты по тегам;
4. Создавать аккаунт.
## Аутентифицированные пользователи могут:
1. Получать данные о своей учетной записи;
2. Изменять свой пароль;
3. Просматривать, публиковать, удалять и редактировать свои рецепты;
4. Добавлять понравившиеся рецепты в избранное и удалять из избранного;
5. Добавлять рецепты в список покупок и удалять из списка;
6. Подписываться и отписываться на авторов;
7. Скачать список покупок
### Статус workflow:
![example workflow](https://github.com/AntanosianAnton/foodgram-project-react/blob/master/.github/workflows/main.yml/badge.svg)
### Foodgram: 

[Foodgram](http://51.250.93.154/)
### Админка:

[Админка](http://51.250.93.154/admin/)
Использовать данные для входа:
```
login: admin
password: admin
```
### Разработчик:

[Антон Антаносян:](https://github.com/AntanosianAnton) 
