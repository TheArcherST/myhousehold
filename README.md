This application is designed to be a layer for processing household data.  There are
abilities to integrate with specific tool


Deployment

```bash
cp .env.example .env
cp ./python/.env.example .env

# *edit env files here* using nano, vim, etc.

# up compose
docker compose up --build -d

# run migrations
make migrations-run

```

Generate new migrations

```bash
make migrations-generate m="Revision message"
```
