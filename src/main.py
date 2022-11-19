"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, session
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, People, FavoritesPeoples, FavoritesPlanets
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, insert, create_engine
from sqlalchemy.sql import text



#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

#sqlalchemy
engine = create_engine(os.environ.get('DB_CONNECTION_STRING'))


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    usuarios= User.query.all()
    list_user=list()
    for u in usuarios:
        list_user.append({"email":u.email,"is_active":u.is_active})
    response_body ={"msg": "Hello, this is your GET /user response "}

    return jsonify({"users":list_user}), 200

@app.route('/CreateUser',methods=['POST'])
def CreateUser():
    try:
        user=User()
        user.email=request.json.get("email")
        user.password=request.json.get("password")
        user.is_active=request.json.get("is_active")
        if user.password == None:
            return jsonify({"Error Password"})
        else:
            db.session.add(user)
            db.session.commit()
            return jsonify({"msg":"ok"})
    except Exception as e:
        return jsonify({"msg":"Error Server"}),500

@app.route('/SavePlanets',methods=['POST'])
def SavePlanets():
    url = 'https://www.swapi.tech/api/planets'
    data = requests.get(url)
    list_planets = list()
    if data.status_code == 200:
        data= data.json()
    for e in data["results"]:
        planet = Planets()
        print(e)
        planet.name =e["name"]
        planet.uid = e["uid"]
        planet.url=e["url"]
        list_planets.append(planet)
    print(list_planets)
    db.session.add_all(list_planets)
    db.session.commit()
    print("El commit")
    return jsonify({"ok":"ok"})

@app.route('/planets')
def GetPlanets():
    planets=Planets.query.all()
    print(len(planets))
    lista_planeta=list()
    for planeta in planets:
        lista_planeta.append({"name":planeta.name,"uid":planeta.uid})
    return jsonify({"Planetas":lista_planeta})

@app.route('/planets/<id>')
def get_planets_id(id):
    planets=Planets.query.filter_by(uid=id).first()
    if planets is  not None:
        return jsonify(planets.serialize())
    else:
        return jsonify("Bad request")
        

@app.route('/SavePeople',methods=['POST'])
def SavePeople():
    url = 'https://www.swapi.tech/api/people'
    data = requests.get(url)
    list_people = list()
    if data.status_code == 200:
        data= data.json()
    for e in data["results"]:
        people = People()
        people.name =e["name"]
        people.uid = e["uid"]
        people.url=e["url"]
        list_people.append(people)
    db.session.add_all(list_people)
    db.session.commit()
    return jsonify({"ok":"ok"})

@app.route('/people')
def GetPeople():
    peoples=People.query.all()
    lista_people=list()
    for people in peoples:
        lista_people.append({"name":people.name,"uid":people.uid})
    return jsonify({"peoples":lista_people})

@app.route('/people/<id>')
def get_people_id(id):
    people=People.query.filter_by(uid=id).first()
    if people is  not None:
        return jsonify(people.serialize())
    else:
        return jsonify("Bad request")

@app.route('/favorite/people/<id>',methods=['POST'])
def favorite_people_insert(id):
    try:
        people=People.query.filter_by(uid=id).first()
        with engine.connect() as con:
            encontrado=con.execute('SELECT user_id,people_id FROM FavoritesPeoples WHERE user_id=1 and people_id='+str(people.id))
            if len(list(encontrado))==0:
                raw=con.execute(FavoritesPeoples.insert(), {"user_id": 1, "people_id": people.id})
                return jsonify({"msg":"favorito agregado"})
            else:
                return jsonify({"msg":"ya se encuentra registrado"})
        return jsonify({"msg":"favorito agregado"})
    except Exception as e:
        return jsonify({"msg":"algo salio muy mal"})

@app.route('/users/favorites')
def user_favorites():
    with engine.connect() as con:
        favoritos=con.execute('SELECT user_id, people.name, people_id FROM FavoritesPeoples INNER JOIN people ON people_id=people.id WHERE user_id=1')
        lista_favoritos=list()
        for i in favoritos:
            lista_favoritos.append({"usuario":i[0],"personaje":i[1],"personaje_id":i[2]})
        favoritos_planetas=con.execute('SELECT user_id, planets.name, planets.id FROM FavoritesPlanets INNER JOIN planets ON planet_id=planets.id WHERE user_id=1')
        lista_favoritos_planetas=list()
        for i in favoritos_planetas:
            lista_favoritos_planetas.append({"usuario":i[0],"planeta":i[1],"planeta_id":i[2]})
        return jsonify({"favorites people":lista_favoritos,"favorites planets":lista_favoritos})

@app.route('/favorite/planet/<id>',methods=['POST'])
def favorite_planet_insert(id):
    try:
        planet=Planets.query.filter_by(id=id).first()
        with engine.connect() as con:
            encontrado=con.execute('SELECT user_id,planet_id FROM FavoritesPlanets WHERE user_id=1 and planet_id='+str(planet.id))
            if len(list(encontrado))==0:
                raw=con.execute(FavoritesPlanets.insert(), {"user_id": 1, "planet_id": planet.id})
                return jsonify({"msg":"planeta favorito agregado"})
            else:
                return jsonify({"msg":"planeta ya se encuentra registrado"})
    except Exception as e:
        return jsonify({"msg":"algo salio muy mal"})

@app.route('/favorite/planet/<int:id>', methods=['DELETE'])
def delete_planets_favorite(id):
    try:
        with engine.connect() as con:
            encontrado=con.execute('SELECT user_id,planet_id FROM FavoritesPlanets WHERE user_id=1 and planet_id='+str(id))
            if len(list(encontrado))==0:
                return jsonify({"msg":"planeta favorito no encontrado"})
            else:
                raw=con.execute(FavoritesPlanets.delete().where(FavoritesPlanets.c.planet_id==id))
                return jsonify({"msg":"planeta favorito borrado"})
    except Exception as e:
        return jsonify({"msg":"algo salio muy mal"})

@app.route('/favorite/people/<int:id>', methods=['DELETE'])
def delete_people_favorite(id):
    try:
        with engine.connect() as con:
            encontrado=con.execute('SELECT user_id,people_id FROM FavoritesPeoples WHERE user_id=1 and people_id='+str(id))
            if len(list(encontrado))==0:
                return jsonify({"msg":"personaje favorito no encontrado"})
            else:
                raw=con.execute(FavoritesPeoples.delete().where(FavoritesPeoples.c.people_id==id and FavoritesPeoples.c.user_id==1))
                return jsonify({"msg":"personaje favorito borrado"})
    except Exception as e:
        return jsonify({"msg":"algo salio muy mal"})

@app.route('/create_planet', methods=['POST'])
def create_planet():
    try:
        planet=Planets()
        planet.name =request.json.get("name")
        planet.uid = request.json.get("id")
        planet.url=request.json.get("url")
        db.session.add(planet)
        db.session.commit()
        return jsonify({"msg":"planeta creado"})
    except Exception as e:
        return jsonify({"msg":"paso algo malo"})

@app.route('/update_planet/<int:id>', methods=['PUT'])
def update_planet(id):
    try:
        planet=Planets.query.get(id)
        planet.name =request.json.get("name")
        planet.uid = request.json.get("id")
        planet.url=request.json.get("url")
        db.session.commit()
        return jsonify({"msg":"planeta actualizado"})
    except Exception as e:
        return jsonify({"msg":"paso algo malo"})

@app.route('/delete_planet/<int:id>', methods=['DELETE'])
def delete_planet(id):
    try:
        planet=Planets.query.get(id)
        db.session.delete(planet)
        db.session.commit()
        return jsonify({"msg":"planeta borrado"})
    except Exception as e:
        return jsonify({"msg":"paso algo malo"})

@app.route('/create_people',methods=['POST'])
def create_people():
    try:
        people=People()
        people.name =request.json.get("name")
        people.uid = request.json.get("id")
        people.url=request.json.get("url")
        db.session.add(people)
        db.session.commit()
        return jsonify({"msg":"personaje creado"})
    except Exception as e:
        return jsonify({"msg":"paso algo malo"})

@app.route('/update_people/<int:id>', methods=['PUT'])
def update_people(id):
    try:
        people=People.query.get(id)
        people.name =request.json.get("name")
        people.uid = request.json.get("id")
        people.url=request.json.get("url")
        db.session.commit()
        return jsonify({"msg":"personaje actualizado"})
    except Exception as e:
        return jsonify({"msg":"paso algo malo"})

@app.route('/delete_people/<int:id>', methods=['DELETE'])
def delete_people(id):
    try:
        people=People.query.get(id)
        db.session.delete(people)
        db.session.commit()
        return jsonify({"msg":"personaje borrado"})
    except Exception as e:
        return jsonify({"msg":"paso algo malo"})

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
