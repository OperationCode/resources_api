from prometheus_client import Counter, Summary

from app import utils as utils
from app.models import Category, Language

failures_counter = Counter('my_failures', 'Number of exceptions raised')
latency_summary = Summary('request_latency_seconds', 'Length of request')
logger = utils.setup_logger('routes_logger')


def get_attributes(json):
    languages_list = Language.query.all()
    categories_list = Category.query.all()

    language_dict = {l.key(): l for l in languages_list}
    category_dict = {c.key(): c for c in categories_list}

    langs = []
    for lang in json.get('languages') or []:
        language = language_dict.get(lang)
        if not language:
            language = Language(name=lang)
        langs.append(language)
    categ = category_dict.get(json.get('category'), Category(name=json.get('category')))

    return langs, categ
