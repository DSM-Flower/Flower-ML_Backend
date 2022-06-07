import json
import datetime

from bson import ObjectId
from io import BytesIO

from pymongo import MongoClient
from flask import Flask, request, Response
from flask_restx import Api

# https://www.tensorflow.org/hub/tutorials/image_feature_vector
# https://www.tensorflow.org/datasets/catalog/oxford_flowers102

# 비밀번호는 fl0wer!!

app = Flask(__name__)
api = Api(app)

# client = MongoClient('mongodb://kkot:kkot@172.31.9.101:27017/kkot')
# client = MongoClient('mongodb://localhost', 27017)
client = MongoClient('mongodb://kkot:kkot@54.153.89.152:27017/kkot')
db = client['kkot']

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.route('/flower_search', methods=['GET'])
def flower_search():
    image = request.files.get('image')
    buffer = BytesIO()
    image.save(buffer)

    return Response('{"name":"장미"}', status=200, content_type='text/json')

@app.route('/image', methods=['GET'])
def image():
    id = request.args.get('id')
    obj = db['images'].find_one({"_id": ObjectId(id)})

    content = obj['content']
    ext = obj['ext']

    return Response(content, status=200, content_type=f'image/{ext}')

# 오브젝트 아이디로 검색할 때는 ObjectId(문자열)로
@app.route('/community_search', methods=['GET'])
def community_search():
    keyword = request.args.get('keyword')

    objs = list(db['community'].find({"title": {"$regex": keyword}}))
    for obj in objs:
        obj['_id'] = str(obj['_id'])
        obj['image'] = str(obj['image'][0]) if len(obj['image']) > 0 else None
        
        obj.pop('comment')

    return Response(json.dumps(objs), status=200, content_type='text/json')

@app.route('/community', methods=['GET'])
def community_get():
    id = request.args.get('id')
    obj = db['community'].find_one({"_id": ObjectId(id)})
    if obj is None:
        return Response('Not Found', status=404, content_type='text/json')
    
    obj['_id'] = str(obj['_id'])
    obj['image'] = [str(id) for id in obj['image']]
    for comment in obj['comment']:
        comment['_id'] = str(comment['_id'])

    return Response(json.dumps(obj), status=200, content_type='text/json')

@app.route('/community', methods=['POST'])
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
        return Response(status=418, content_type='text/json')
    else:
        return Response(status=200, content_type='text/json')

@app.route('/community', methods=['PUT'])
def community_put():
    args = dict(request.form)

    id = args.pop('_id')
    nickname = args.pop('nickname')
    password = args.pop('password')

    obj = db['community'].find_one({'_id': ObjectId(id)})

    if obj is None:
        return Response(status=404, content_type='text/json')

    if obj['nickname'] != nickname or obj['password'] != password:
        return Response(status=418, content_type='text/json')

    for image in obj['image']:
        db['images'].delete_one({'_id': ObjectId(image)})
    
    post = {
        **args, 
        'uploadDate': now()
    }

    if args.get('images', None) is None:
        files = []
        for file in request.files.getlist('image'):
            byte_buffer = BytesIO()
            file.save(byte_buffer)

            result = db['images'].insert_one({
                'content': byte_buffer.getvalue(),
                'ext': file.filename.split('.')[-1]
            })
            files.append(result.inserted_id)

        post['images'] = files
    
    db['community'].update_one({'_id': ObjectId(id)}, {'$set': post})

    return Response(status=200, content_type='text/json')

@app.route('/community', methods=['DELETE'])
def community_delete():
    id = request.args.get('id')
    nickname = request.args.get('nickname')
    password = request.args.get('password')

    obj = db['community'].find_one({"_id": ObjectId(id)})
    if obj is None:
        return Response('', status=404, content_type='text/json')

    if obj['nickname'] != nickname or obj['password'] != password:
        return Response('', status=418, content_type='text/json')

    for image in obj['image']:
        db['images'].delete_one({'_id': ObjectId(image)})

    db['community'].delete_one({"_id": ObjectId(id)})
    return Response('', status=200, content_type='text/json')

@app.route('/comment', methods=['POST'])
def comment_post():
    args = dict(request.form)

    id = args.pop('_id')
    obj = db['community'].find_one({'_id': ObjectId(id)})
    if obj is None:
        return Response('', status=404, content_type='text/json')

    comment = {
        '_id': ObjectId(),
        **args, 
        'uploadDate': now(),
    }

    db['community'].update_one(
        {'_id': ObjectId(id)}, 
        {'$push': {'comment': comment}}
    )

    return Response('', status=200, content_type='text/json')
    
@app.route('/comment', methods=['PUT'])
def comment_put():
    args = dict(request.form)

    id = args.pop('_id')
    nickname = args['nickname']
    password = args['password']
    
    obj = db['community'].find_one({'comment._id': ObjectId(id)}, {'comment.$': 1})
    obj = obj['comment'][0]
    
    if obj is None:
        return Response(status=404, content_type='text/json')
       
    if obj['nickname'] != nickname or obj['password'] != password:
        return Response(status=418, content_type='text/json')
        
    comment = {
        **args,
        'uploadDate': now()
    }
    
    db['community'].update_one(
        {'comment._id': ObjectId(id)}, {'$set': comment}
    )
    
    return Response(status=200, content_type='text/json')

@app.route('/comment', methods=['DELETE'])
def comment_delete():
    id = request.args.get('id')
    nickname = request.args.get('nickname')
    password = request.args.get('password')

    obj = db['community'].find_one({'comment._id': ObjectId(id)}, {'comment.$': 1})
    if obj is None:
        return Response('', status=404, content_type='text/json')

    com = obj['comment'][0]
    if com['nickname'] != nickname or com['password'] != password:
        return Response('', status=418, content_type='text/json')

    db['community'].update_one({}, {'$pull': {'comment': {'_id': ObjectId(id)}}})
    return Response('', status=200, content_type='text/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)