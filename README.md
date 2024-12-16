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
(venv) $ pip install -r requirements.txt
```
4. create the database
```bash
(venv) $ flask db upgrade
```
5. Compile language translations
```bash
(venv) $ flask translate compile
```
6. (Optional) Set environment variables to securely sign data, add email configuration, and add API keys
7. (Optional) Add Lord of the Rings themed sample Users and Posts.
```bash
(venv) $ python -m scripts.add_sample_data
```
- You can log in to the account of good-aligned characters with password '123', bad characters with password '321' and morally ambiguous characters with password '222'.

## Translations
1. Add a new language:
```bash
(venv) $ flask translate init <language-code>
```
2. Update languages after making changes to the _() and _l() language markers:
```bash
(venv) $ flask translate update
```
3. Compile all languages after updating the `msgstr` fields in the `.po` translation files (one `.po` file per supported language):
```bash
(venv) $ flask translate compile
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
```bash
(venv) $ flask run
```
Add `--debug`/`--no-debug` flag (or set `.flaskenv` variable `FLASK_DEBUG` to 0/1) to enable/disbale debug mode.

## Schema
Load schema.xml into a viewer like https://sql.toad.cz/ to see database schema.

App uses flask-sqlalchemy as ORM and flask-migrate to handle changes in db schema.

To implement a change in database models (add a new table, for example) you:
1. Modify models in app/models.py
2. Generate a new migration script
```bash
(venv) $ flask db migrate -m "short description"
```
3. Review the migration script (will appear at `migrations/versions/`)
4. Apply the changes to your development database
```bash
(venv) $ flask db upgrade
```
5. Add the migration script to source control and commit it.
6. Run `flask db upgrade` on production server.

When working with database servers such as MySQL and PostgreSQL, you have to create the database in the database server before running upgrade.

To downgrade the database (usually in development): run `flask db downgrade`, delete the migration script, and then generate a new one to replace it.