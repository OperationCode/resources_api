from app import utils as utils
from app.models import Category, Language


def _unauthorized_response():
    message = "The email or password you submitted is incorrect " \
              "or your account is not allowed api access"
    payload = {'errors': {"invalid-credentials": {"message": message}}}
    return utils.standardize_response(payload=payload, status_code=401)


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
    return (langs, categ)
