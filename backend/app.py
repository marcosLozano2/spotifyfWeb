from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import yaml

app = Flask(__name__)

config = yaml.load(open('database.yaml'),Loader=yaml.FullLoader)
client = MongoClient(config['uri'])
# db = client.lin_flask
db = client['knf-dev']
CORS(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/songs', methods=['POST', 'GET'])
def data():
    
    # POST a data to database
    if request.method == 'POST':
        
        body = request.json
        songName = body['songName']
        artistName = body['artistName']
        duration = body['duration'] 
        # db.users.insert_one({
        db['songs'].insert_one({
            "songName": songName,
            "artistName": artistName,
            "duration":duration
        })
        return jsonify({
            'status': 'Data is posted to MongoDB!',
            "songName": songName,
            "artistName": artistName,
            "duration":duration
        })
    
    # GET all data from database
    if request.method == 'GET':
        allData = db['songs'].find()
        dataJson = []
        for data in allData:
            id = data['_id']
            songName = data['songName']
            artistName = data['artistName']
            duration = data['duration'] 
            dataDict = {
                'id': str(id),
                'songName': songName,
                'artistName': artistName,
                'duration':duration
            }
            dataJson.append(dataDict)
        print(dataJson)
        return jsonify(dataJson)

@app.route('/songs/<string:id>', methods=['GET', 'DELETE', 'PUT'])

def onedata(id):

    # GET a specific data by id
    if request.method == 'GET':
        data = db['songs'].find_one({'_id': ObjectId(id)})
        id = data['_id']
        songName = data['songName']
        artistName = data['artistName']
        duration = data['duration']
        dataDict = {
            'id': str(id),
            'songName': songName,
            'artistName': artistName,
            'duration':duration
        }
        print(dataDict)
        return jsonify(dataDict)
        
    # DELETE a data
    if request.method == 'DELETE':
        db['songs'].delete_many({'_id': ObjectId(id)})
        print('\n # Deletion successful # \n')
        return jsonify({'status': 'Data id: ' + id + ' is deleted!'})

    # UPDATE a data by id
    if request.method == 'PUT':
        data = request.json
        songName = data['songName']
        artistName = data['artistName']
        duration = data['duration']

        db['songs'].update_one(
            {'_id': ObjectId(id)},
            {
                "$set": {
                    'songName': songName,
                    'artistName': artistName,
                    'duration':duration
                }
            }
        )

        print('\n # Update successful # \n')
        return jsonify({'status': 'Data id: ' + id + ' is updated!'})

# Configure Swagger UI
SWAGGER_URL = '/api'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Spotify"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# @app.route('/swagger.json')
# def swagger():
#     with open('swagger.json', 'r') as f:
#         return jsonify(json.load(f))

if __name__ == '__main__':
    app.debug = True
    app.run()