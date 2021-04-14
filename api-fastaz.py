from flask import Flask , request , jsonify , make_response
import pymongo 
import jwt
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'quangblue16032401'

client = pymongo.MongoClient("mongodb+srv://quang_db:1h5o1ifGY5wrJsUT@cluster0.cv2te.mongodb.net/?ssl=true&ssl_cert_reqs=CERT_NONE")
try:
    db = client.get_database("fastaz_db")
    collection = db.get_collection("fastaz_db")
except pymongo.errors.ConnectionFailure as error:
    print(str(error))
    exit()
finally:
    print("Connecting to database sucessfully !!!")

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!' : 'Token is missing!'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
            print(payload)
        except:
            return jsonify({'Alert!' : 'Invalid Token!'})
        return func(*args, **kwargs)
    return decorated


@app.route('/login', methods=['POST'])
def login():
    _id = request.json['_id']
    username = request.json['username']
    password = request.json['password']

    if username and password and _id:
        token = jwt.encode({
            '_id' : _id,
            'username' : username,
            'password' : password,
            },
            app.config['SECRET_KEY']
            )
        if collection.count_documents({"_id":_id}) == 0:
            dataUser = {
                '_id' : _id,
                'username' : username,
                'password' : password
            }
            collection.insert_one(dataUser)


        return jsonify({
            'token' : token.decode('utf-8'),
            '_id' : _id,
            'username' : username
            })
    else:
        return make_response('Unable to verify', 403 , {'WWW-Authenticate': 'Basic realm:"Authentication Failed !"'})





def decode(token):
    # token = request.json['token']
    de = jwt.decode(token,app.config['SECRET_KEY']) 
    return jsonify(de)

@app.route('/users', methods=['POST'])
def create_user():
    # print(request.json)
    username = request.json['username']
    password = request.json['password']

    if username and password:
        id = collection.insert({
            'username' : username,
            'password' : password

        })

        response = {
            'username' : username,
            'password' : password
        }

        return response
    else:
        return not_found()

@app.errorhandler(404)
def not_found(error=None):
    message = jsonify({
        'message' : 'Resource Not Found',
        'status' : 404
    })
    response.status_code = 404
    return message



if __name__ == '__main__':
    app.run(debug=True)