# Flask app
For learning purposes. Based on the Flask guide at: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

## Setup
Developed with Python 3.12.4
1. Clone repository
2. Create virtual environment: on cloned directory, run
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. db
```bash
flask db upgrade
```
## Translations
To add support for a new language:
1. generate messages.pot
```bash
pybabel extract -F babel.cfg -k _l -o messages.pot .
```
2. add desired language (here the example is 'es' for Spanish) to Config.py and run the command below (substituting 'es' for the correct language code)
```bash
pybabel init -i messages.pot -d app/translations -l es
```
3. Edit the `msgstr` fields in the file at `app/translations/<lang>/LC_MESSAGES/messages.po` to translate text.
4. With translations ready, run `pybabel compile -d app/translations`
To update translation file:
```
(venv) $ pybabel extract -F babel.cfg -k _l -o messages.pot .
(venv) $ pybabel update -i messages.pot -d app/translations
```

## Config
If environment variables are not defined, app will use default value hardcoded in `config.py`.
- `SECRET_KEY` used by Flask
- `DATABASE_URL` used by sqlalchemy
Email Configuration (to recieve server errors by email)
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USE_TLS`: App instead uses SSL if this variable is undeclared or if its value is 0.
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `ADMINS`: comma-separated, like 'example1@example.com,example2@example.com'

To rename the project just change the name of `my_website.py` and the `FLASK_APP` variable at `.flaskenv`.

## Running the app
### Development mode
```bash
flask run
```
or 
```bash
flask run --debug
```

## Schema
Load schema.xml into a viewer like https://sql.toad.cz/ to see database schema.

App uses flask-sqlalchemy as ORM and flask-migrate to handle changes in db schema.

To implement a change in database models (add a new table, for example) you:
1. Modify models in app/models.py
2. Generate a new migration script
```bash
flask db migrate
```
3. Review the migration script (will appear at `migrations/versions/`)
4. Apply the changes to your development database
```bash
flask db upgrade
```
5. Add the migration script to source control and commit it.
6. Run `flask db upgrade` on production server.

When working with database servers such as MySQL and PostgreSQL, you have to create the database in the database server before running upgrade.

To downgrade the database (usually in development): run `flask db downgrade`, delete the migration script, and then generate a new one to replace it.