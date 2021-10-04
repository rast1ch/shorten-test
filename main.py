import hashlib
import redis
import random
import string
from flask import Flask
from flask import (
    request,
    render_template
)
import flask
from werkzeug.exceptions import abort
from wtforms import validators, Form, StringField


app = Flask(__name__)
r = redis.Redis()


class CreationForm(Form):
    url_to = StringField('URL', [validators.Length(min=5, max=200)])


def form_slug(link : str) :
    # """Формирования случайного url"""
    # random_slug = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    # # Оооочень много вариантов +-1,340,095,640,625
    # if r.get(random_slug): # Это для избежания колизий
    #     rand_slug()
    # else:
    #     return random_slug
    encoded_link = link.encode()
    hash_object = hashlib.sha256(encoded_link)
    return hash_object.hexdigest()[:3] + hash_object.hexdigest()[:-4:-1]



@app.route('/', methods=['GET', 'POST'])
def index():
    form = CreationForm(request.form)
    if request.method == 'POST' and form.validate():
        slug = form_slug(form.url_to.data)
        if r.get(slug):
            r.expire(slug, 3600) # Просто обновить счётчик
        else:
            r.set(slug, form.url_to.data)
            r.expire(slug, 3600)
        return flask.redirect(f'http://127.0.0.1:5000/info/{slug}')
    return render_template('index.html', form=form)


@app.route('/info/<slug>/')
def info(slug):
    link_to = r.get(slug)
    url = f'http://127.0.0.1:5000/{slug}'
    if link_to:
        return render_template('info.html', data={'link_to':link_to.decode('utf-8'),'url':url})
    else:
        abort(404)


@app.route('/<slug>/')
def redirect(slug):
    link_to = r.get(slug)
    if link_to:
        return flask.redirect(link_to.decode('utf-8'))
    else:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)