To use this website locally:

1. Run ```cd bot && docker compose build && docker compose up -d```
2. Run ```cd email && docker compose build && docker compose up -d```
3. Run ```cd website && docker compose build && docker compose up -d```
4. Run ```cd dev-env && docker compose build && docker compose up -d```
5. Set up mail server for the mails (I used [mail trap](https://mailtrap.io))
6. Run ```docker exec -it photo-site-1 python -c 'import init; init.init_db()'``` to init the DB
7. Access it at ```http://localhost```
8. Format of the api request: ```http://localhost/screenshot?url=http://google.com&format=png&timeout=0&uuid=API_KEY```

Allowed formats: png, webp, jpg.
Parameter timeout is optional and can be a integer value between 0 and 20, default is 5.