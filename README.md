# Flask app skeleton
A basic skeleton with a simple login form. No database implementation yet.

Based on https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
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

## Config
- Set `SECRET_KEY` environment variable. If not set, app will use default value hardcoded in `config.py`.

## Running the app
### Development mode
```bash
flask run
```
or 
```bash
flask run --debug
```