#проект Foodgram
### Автор
Vasiluk Konsantin / kavasiluk

### Использованные технологии
Python
Django
Nginx
Docker
Postgres
GitHub
GitHub Actions
JavaScript
Rest

### Описание проекта
Проект "Foodgram" - это сайт на котором пользователи могут добавлять рецепты, находить рецепты других пользователей, подписываться на их новые публикации.
Добавив рецепты других пользователей в список покупок пользователи могут скачать его, чтобы получить файл со списоком ингредиентов необходимых для приготовления выбранных блюд.

Сайт на котором размещен проект - https://vaska.tech
Для просмотра админки можно воспользоваться следующими данными:
Email: vasiluk23@yandex.ru
Password: yandexpracticum

### Как запустить проект на своем сервере:
Установить на сервере docker.
Создать папку Foodgram и перейти в неё.
Создать файл docker-compose.yml и .env (содержимое которого необходимо заполнить на основании примера в файле .env.template).
Создать папку infra в которой нужно будет создать файл nginx.conf

Необходимо будет заполнить Secrets на Github, добавив туда следующие данные:
DOCKER_USERNAME - Имя аккаунта dockerhub
DOCKER_PASSWORD - Пароль от аккаунта dockerhub
HOST - IP сервера
USER - Имя пользователя на сервере
SSH_KEY - SSH ключ для доступа на сервер
SSH_PASSPHRASE - Фраза для использования SSH ключа
TELEGRAM_TO - ID телеграм аккаунта для получения уведомления об успешном деплое
TELEGRAM_TOKEN - API token бота который будет использоваться для получения уведомления

Выполнить команды:
* git add .
* git commit -m "Some Commit"
* git push

После этого код будет автоматически обработан с помощью GitHub Actions где будут собраны докер-образы для контейнеров на Docker Hub и автоматический деплой проекта на сервер.
При успешном деплое будет получено уведомление в Telegram

После выполнения деплоя, для загрузки ингредиентов и создания администратора следует выполнить следующие команды на сервере:
```
docker compose exec backend python manage.py load_ingredients
docker compose exec backend python manage.py createsuperuser