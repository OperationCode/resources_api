from src.app import db


def health_database_status():
    try:
        db.session.query("1").from_statement("SELECT 1").all()
        return '<h1>It works.</h1>'
    except Exception:
        return '<h1>Something is broken.</h1>'
