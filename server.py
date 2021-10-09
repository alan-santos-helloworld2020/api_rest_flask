from flask import Flask,jsonify,Response,request
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from pymongo import message
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/onload"
mongo = PyMongo(app)

@app.route('/', methods=['POST'])
def salvar():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if username and email and password:
        hashed_password = generate_password_hash(password)
        id = mongo.db.usuarios.insert(
            {'username': username, 'email': email, 'password': hashed_password})
        response = jsonify({
            '_id': str(id),
            'username': username,
            'password': password,
            'email': email
        })
        response.status_code = 201
        return response
    else:
        return not_found()

#############################################################################
@app.route("/",methods=['GET'])
def listar():
    dados = json_util.dumps(mongo.db.usuarios.find())
    return Response(dados,mimetype='application/json')

#############################################################################

@app.route("/<id>",methods=['GET'])
def pesquisar(id):
    dados = json_util.dumps(mongo.db.usuarios.find_one({'_id':ObjectId(id)}))
    return Response(dados,mimetype='application/json')

#############################################################################

@app.route('/<id>', methods=['PUT'])
def alterar(id):
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    if username and email and password and id:
        hashed_password = generate_password_hash(password)
        result = mongo.db.usuarios.update_one(
            {'_id': ObjectId(id['$oid']) if '$oid' in id else ObjectId(id)}, {'$set': {'username': username, 'email': email, 'password': hashed_password}})
        response = jsonify({'message': True,'rows':result.matched_count})
        response.status_code = 200
        return response
    else:
      return not_found()

#############################################################################

@app.route('/<id>',methods=['DELETE'])
def deletar(id):
    result = mongo.db.usuarios.delete_one({'_id':ObjectId(id)})
    if result.deleted_count > 0:
        response = jsonify({'message':True,'rows':result.deleted_count})
        return response
    else:
        response = jsonify({'message':False,'rows':result.deleted_count})
        return response


#############################################################################

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        message:'Resouce not found '+request.url,
        status:404
    })
    response.status_code = 404
    return response

app.run(debug=True)