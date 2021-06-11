from flask import Flask , request , jsonify , make_response
import pymongo , json
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
    _id = int(request.values['_id'])
    usernameAz = request.values['usernameAz']
    tokenWeb = request.values['tokenWeb']
    email = request.values['email']

    if usernameAz and _id:
        token = jwt.encode({
            '_id' : _id,
            'usernameAz' : usernameAz
            },
            app.config['SECRET_KEY']
            )
        if collection.count_documents({"_id":_id}) == 0:
            dataUser = {
                '_id' : _id,
                'usernameAz' : usernameAz,
                'tokenWeb' : tokenWeb,
                'email' : email,
                'shopee' : {}
            }
            collection.insert_one(dataUser)


        return jsonify({
            'token' : token.decode('utf-8'),
            '_id' : _id,
            'username' : usernameAz,
            'email' : email
            })
    else:
        return make_response('Unable to verify', 403 , {'WWW-Authenticate': 'Basic realm:"Authentication Failed !"'})

@app.route('/check_user_shopee', methods=['POST'])
def check_shopee_username():
    usernameAz = request.json['usernameAz']
    shopid = request.json['shopid']
    usernameShop = request.json['usernameShop']
    cookie = request.json['cookie']

    if usernameAz and shopid and usernameShop:
        try:
            if collection.count_documents({"usernameAz":usernameAz , f"shopee.{usernameShop}" : { "$exists" : True }}) == 0:
                data = { 
                    "cookie": cookie,
                    "shop_name": usernameShop,
                    "shopid": shopid,
                    "status_cookie": "True",
                    "active_functions": [],
                    "reply_rating": {
                            "1": [],
                            "2": [],
                            "3": [],
                            "4": [],
                            "5": []
                                    },
                    "list_push_product" : []   
                                        
                                        }
                collection.update({"usernameAz" : usernameAz}, {"$set" : 
                { f'shopee.{usernameShop}' : data}}, upsert=True)
                return jsonify({'create_user' : True})
            else:
                return jsonify({'create_user' : False})
        except:
            return jsonify({'error' : 'Can not update database'})

@app.route('/get_data_user_shopee' , methods = ['POST'])
def get_data_user_shopee():
    usernameAz = request.values['usernameAz']

    if usernameAz:
        listShop =[]
        r = collection.find({
            'usernameAz' : usernameAz,
            })
        for x in r:
            for shop in x['shopee']:
                listShop.append(shop)

        if len(listShop) != 0 :
            re = {'data' : listShop,
                'success' : True
            }
        else:
            re = {'success' : False}
        
        return jsonify(re)
    else:
        return jsonify({'error' : 'Can not update database'})

@app.route('/get_data_shopee' , methods = ['POST'])
def get_data_shopee():
    usernameAz = request.values['usernameAz']

    if usernameAz:
        data = None
        r = collection.find({
            'usernameAz' : usernameAz,
            })
        for x in r:
            data = x

        if len(data) > 0 :
            re = {'data' : data,
                'success' : True
            }
        else:
            re = {'success' : False}
        
        return jsonify(re)
    else:
        return jsonify({'error' : 'Can not update database'})

@app.route('/del_user_shopee' , methods = ['POST'])
def del_user_shopee():
    usernameShop = request.values['usernameShop']
    usernameAz = request.values['usernameAz']

    if usernameAz and usernameShop:
        if collection.count_documents({"usernameAz":usernameAz , f"shopee.{usernameShop}" : { "$exists" : True }}) != 0:
            
            r = collection.update({"usernameAz": usernameAz}, {"$unset": {f"shopee.{usernameShop}": 1}})
            if r['updatedExisting'] == True:
                return jsonify({'updated' : True})
            else:
                return jsonify({'updated' : False})

        else:
            return jsonify({'error' : 'Can not update empty database'})
    else:
        return jsonify({'error' : 'Can not update database'})

@app.route('/save_reply_rating' , methods=['POST'])
def save_reply_rating():
    usernameShop = request.values['usernameShop']
    usernameAz = request.values['usernameAz']
    data = request.values['dataUpadte']
    data = data.replace("\'", "\"")
    data = json.loads(data)

    print (data)
    if usernameShop and usernameAz and data: 
        if collection.count_documents({"usernameAz":usernameAz , f"shopee.{usernameShop}" : { "$exists" : True }}) != 0:

            r = collection.update_many(
            { 'usernameAz': usernameAz },
            { '$set': { 
                f'shopee.{usernameShop}.reply_rating.1': data['textOneStar'], 
                f'shopee.{usernameShop}.reply_rating.2': data['textTwoStar'],
                f'shopee.{usernameShop}.reply_rating.3': data['textThreeStar'],
                f'shopee.{usernameShop}.reply_rating.4': data['textFourStar'],
                f'shopee.{usernameShop}.reply_rating.5': data['textFiveStar'], 
                }},
            upsert=True  
            )
            print ('đây là r ', r.matched_count) 
            if r.matched_count > 0:
                return jsonify({'updated' : True})
            else:
                return jsonify({'updated' : False})
        else:
            return jsonify({'error' : 'Can not update empty database'})
    else:
        return jsonify({'error' : 'Can not update database'})
    

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