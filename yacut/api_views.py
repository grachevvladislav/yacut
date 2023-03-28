from flask import jsonify, request, url_for
from . import app, db
from .models import URLMap

from .views import get_unique_short_id
from .error_handlers import InvalidAPIUsage
import re

pattern = re.compile(r'^[a-z,A-Z,0-9]{1,16}$')


@app.route('/api/id/<string:id>/', methods=['GET'])
def delete_opinion(id):
    link = URLMap.query.filter_by(short=id).first()
    if link is None:
        raise InvalidAPIUsage('Указанный id не найден')
    return jsonify({"url": link.original}), 200


@app.route('/api/id/', methods=['POST'])
def generate_link():
    data = request.get_json()
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('\"url\" является обязательным полем!')
    url = data['url']
    if 'custom_id' in data and data['custom_id'] != '':
        short = data['custom_id']
        if URLMap.query.filter_by(short=short).first() is not None:
            raise InvalidAPIUsage(
                f'Имя "{short}" уже занято.'
            )
        if re.search(pattern, short) is None:
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
    ), 201)
