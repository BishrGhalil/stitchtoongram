# Stitchtoongram
Telegram bot for [stitchtoon](https://github.com/BishrGhalil/stitchtoon).

### Getting started
**Requirements:**
- Python >=3.8
- pipenv

1. Installing required python packages and starting virtual environment.
```console
pipenv install
pipenv shell
```

2. Edit `secrets.json` to add required data.
```json
{
  "bot_token": "",
  "requests_channel_id": "",
  "logs_channel_id": "",
  "reports_channel_id": "",
  "author_id": ""
}
```

3. Edit `initial_db_data.json` to add your initial database data such as admins and other options.
```json
{
  "options": [{
      "name": "DEFAULT_POINTS",
      "value": 5,
      "data_type": "int"
    },
    "options": [{
      "name": "AUTHOR_TE_ID",
      "value": 00000000,
      "data_type": "int"
    }],
    "users": [{
        "username": "beshralghalil",
        "is_admin": true,
        "is_registered": true,
        "telegram_id": 0000000,
        "full_name": "Beshr Alghalil",
        "points": 10000
      },
      {
        "username": "someuser",
        "is_blocked": true,
        "telegram_id": 00000000,
        "full_name": "Some User",
      }
    ]
  }
```

4. Start the development server
```console
python server.py
```

Or start the shell for fast DB CRUD operations:
```console
python server.py --shell
```
