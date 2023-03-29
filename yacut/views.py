from flask import flash, redirect, render_template, url_for

from . import app, db
from .forms import URLForm
from .models import URLMap
from .utils import get_unique_short_id


@app.route('/<string:id>', methods=['GET'])
def redirect_view(id):
    link = URLMap.query.filter_by(short=id).first_or_404()
    return redirect(link.original)


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()
    if form.validate_on_submit():
        short = form.custom_id.data
        if short:
            if URLMap.query.filter_by(short=short).first() is not None:
                flash(f'Имя {short} уже занято!')
                return render_template('index.html', form=form)
        else:
            short = get_unique_short_id()
        link = URLMap(
            original=form.original_link.data,
            short=short
        )
        db.session.add(link)
        db.session.commit()
        flash('Ваша новая ссылка готова!')
        flash(url_for("redirect_view", id=short, _external=True), 'url')
    return render_template('index.html', form=form)
