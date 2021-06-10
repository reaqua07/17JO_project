from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)
from pymongo import MongoClient

client = MongoClient('mongodb://3.37.86.16', 27017, username="test", password="test")
db = client.dbsparta
SECRET_KEY = 'SPARTA'

import jwt
import datetime
import hashlib

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('main.html', name=user_info["name"])
    except jwt.ExpiredSignatureError:
        return render_template('signup.html', msg="로그인 시간이 만료되었습니다.")
    except jwt.exceptions.DecodeError:
        return render_template('signup.html')


@app.route('/signup')
def register():
    return render_template('signup.html')


@app.route('/main')
def main():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({"id": payload['id']})
    date = datetime.datetime.today()
    month = date.month
    return render_template('main.html', name=user_info['name'][1:], currentMonth=month)


@app.route('/write')
def write():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({"id": payload['id']})
    return render_template('write.html', name=user_info['name'][1:])


@app.route('/api/signup/ok', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name': name_receive})

    return jsonify({'result': 'success'})

@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:

        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/api/signup/check_dup', methods=['POST'])
def check_dup():
    # id 중복확인
    id_receive = request.form['id_give']
    exists = bool(db.user.find_one({"id": id_receive}))
    print(id_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/api/main', methods=['GET'])
def editlisting():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({'id': payload['id']})
    diaries = list(db.diaries.find({'id': user_info['id']}))
    for diary in diaries:
        diary["_id"] = str(diary["_id"])

    return jsonify({'user_diaries': diaries})


@app.route('/api/main', methods=['GET'])
def monthlisting():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({'id': payload['id']})
    diaries = list(db.diaries.find({'id': user_info['id']}))
    for diary in diaries:
        diary["_id"] = str(diary["_id"])

    return jsonify({'user_diaries': diaries})


@app.route('/api/main', methods=['GET'])
def listing():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({'id': payload['id']})
    diaries = list(db.diaries.find({'id': user_info['id']}))

    for diary in diaries:
        diary["_id"] = str(diary["_id"])

    return jsonify({'user_diaries': diaries})

@app.route('/api/edit', methods=['POST'])
def editSave():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({"id": payload['id']})
    weather_receive = request.form.get('weather_give')
    mood_receive = request.form.get('mood_give')
    content_receive = request.form.get('content_give')
    date_receive = request.form.get('date_give')

    db.diaries.update_one({'id': user_info['id'], 'date': date_receive}, {'$set': {'mood': mood_receive}})
    db.diaries.update_one({'id': user_info['id'], 'date': date_receive}, {'$set': {'weather': weather_receive}})
    db.diaries.update_one({'id': user_info['id'], 'date': date_receive}, {'$set': {'content': content_receive}})
    return jsonify({'result': 'success'})


@app.route('/api/delete', methods=['POST'])
def deletedia():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({"id": payload['id']})
    date_receive = request.form.get('date_give')
    db.diaries.delete_one({'id': user_info['id'], 'date': date_receive})
    return jsonify({'result': 'success'})


@app.route('/write', methods=['POST'])
def write_review():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.user.find_one({"id": payload['id']})
    weather_receive = request.form.get('weather_give')
    mood_receive = request.form.get('mood_give')
    content_receive = request.form.get('content_give')
    date_receive = request.form.get('date_give')
    doc = {
        'mood': mood_receive,
        'weather': weather_receive,
        'content': content_receive,
        'date': date_receive,
        'date_year': date_receive.split('-')[0],
        'date_month': date_receive.split('-')[1],
        'id': user_info['id']
    }
    db.diaries.insert_one(doc)
    null = None
    db.diaries.delete_many({'mood': null})

    return jsonify({'result': 'success'})


@app.route('/api/name', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'name': userinfo['name']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
