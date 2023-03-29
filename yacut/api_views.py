import re
from http import HTTPStatus

from flask import jsonify, request, url_for

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id

short_pattern = re.compile(r'^[a-z,A-Z,0-9]{1,16}$')
url_pattern = re.compile(
    r'^http(s)?(:)?\/\/(www\.)?([a-zA-Z0-9@:%._\+~\/#=]){2,256}'
    r'\.([a-z]){2,6}[-a-zA-Z0-9@:%_\+.~#?&\/=]*$'
)


@app.route('/api/id/<string:id>/', methods=['GET'])
def delete_opinion(id):
    link = URLMap.query.filter_by(short=id).first()
    if link is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({"url": link.original}), HTTPStatus.OK


@app.route('/api/id/', methods=['POST'])
def generate_link():
    data = request.get_json()
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    url = data.get('url', None)
    if url is None:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')
    print(url)
    print(re.search(url_pattern, url))
    if re.search(url_pattern, url) is None:
        raise InvalidAPIUsage(
            'Не похоже на ссылку'
        )
    short = data.get('custom_id', None)
    if short:
        if URLMap.query.filter_by(short=short).first() is not None:
            raise InvalidAPIUsage(
                f'Имя "{short}" уже занято.'
            )
        if re.search(short_pattern, short) is None:
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
    else:
        short = get_unique_short_id()
    link = URLMap(
        original=url,
        short=short
    )
    db.session.add(link)
    db.session.commit()
    return (jsonify(
        {
            "url": url,
            "short_link": url_for("redirect_view", id=short, _external=True)
        }
    ), HTTPStatus.CREATED)
