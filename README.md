# praktikum_new_diplom
Автор - mehonator

Foodgram - убийца инстаграма, вобравший в себя самое лучшее и необходимое от конкурента — рецептики!
В Foodgram - сервис, в котором вы можете публиковать свои рецепты, подписываться на авторов, добавлять рецепты в список любимых или в корзину для покупок.
Так же вы можете распечатать список ингредиентов для покупок, который вам любезно посчитает наш сервис!

Проект разворачивается очень просто
1. Необходимо прописать server_name в nginx.conf
2. Запустить docker-compose: sudo docker-compose up --build
3. Подключиться к контейнеру web и провести миграции
    3.1 docker exec -it <container_id> bash
    3.2 manage.py migrate

Доступ к админке
login admin@admin.ru
password coagulant-cilantro-shoplift-untimed-sincere