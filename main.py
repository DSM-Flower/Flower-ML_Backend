import json
import datetime

from bson import ObjectId
from io import BytesIO

from pymongo import MongoClient
from flask import Flask, request, Response
from flask_restx import Api

# 비밀번호는 fl0wer!!

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://172.31.3.16', 27017)
db = client['kkot']

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 오브젝트 아이디로 검색할 때는 ObjectId(문자열)로
@app.route('/community_search', methods=['GET'])
def community_search():
    keyword = request.args.get('keyword')
    page = int(request.args.get('page'))

    objs = list(db['community'].find({"title": {"$regex": keyword}}))
    for obj in objs:
        obj['_id'] = str(obj['_id'])
        obj['image'] = str(obj['image'][0])
        
        obj.pop('comment')

    return Response(json.dumps(objs), status=200)

@app.route('/community/<id>', methods=['GET'])
def community(id):
    obj = db['community'].find_one({"_id": ObjectId(id)})
    if obj is None:
        return Response('Not Found', status=404)
    
    obj['_id'] = str(obj['_id'])
    obj['image'] = [str(id) for id in obj['image']]

    return Response(json.dumps(obj), status=200)

@app.route('/community_post', methods=['POST'])
def community_post():
    try:
        args = dict(request.form)
        files = []
        for i, file in enumerate(request.files.getlist('image')):
            byte_buffer = BytesIO()
            file.save(byte_buffer)

            result = db['images'].insert_one({
                'content': byte_buffer.getvalue(), 
                'ext': file.filename.split('.')[-1]}
            )
            files.append(result.inserted_id)

        post = {
            **args,
            'image': files,
            'comment': [],
            'uploadDate': now()
        }
        db['community'].insert_one(post)
    except:
        return Response(status=418)
    else:
        return Response(status=200)

@app.route('/community_delete/<id>', methods=['DELETE'])
def community_delete(id):
    nickname = request.args.get('nickname')
    password = request.args.get('password')

    obj = db['community'].find_one({"_id": ObjectId(id)})
    if obj is None:
        return Response('', status=404)

    if obj['nickname'] != nickname or obj['password'] != password:
        return Response('', status=418)

    for image in obj['image']:
        db['images'].delete_one({'_id': image})

    db['community'].delete_one({"_id": ObjectId(id)})
    return Response('', status=200)

@app.route('/image/<id>', methods=['GET'])
def image(id):
    obj = db['images'].find_one({"_id": ObjectId(id)})

    content = obj['content']
    ext = obj['ext']

    return Response(content, status=200, content_type=f'image/{ext}')

@app.route('/comment_post', methods=['POST'])
def comment_post():
    args = dict(request.form)

    id = args.pop('_id')
    obj = db['community'].find_one({'_id': ObjectId(id)})
    if obj is None:
        return Response('', status=404)

    comment = {
        '_id': ObjectId(),
        **args, 
        'uploadDate': now(),
    }

    db['community'].update_one(
        {'_id': ObjectId(id)}, 
        {'$push': {'comment': comment}}
    )

    return Response('', status=200)

@app.route('/comment_delete/<id>', methods=['DELETE'])
def comment_delete(id):
    nickname = request.args.get('nickname')
    password = request.args.get('password')

    obj = db['community'].find_one({'comment._id': ObjectId(id)}, {'comment.$': 1})
    if obj is None:
        return Response('', status=404)

    com = obj['comment'][0]
    if com['nickname'] != nickname or com['password'] != password:
        return Response('', status=418)

    db['community'].update_one({}, {'$pull': {'comment': {'_id': ObjectId(id)}}})
    return Response('', status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)