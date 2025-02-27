#MY ECOM API FOCUSES ON A BEAT STORE WHERE YOU CAN BUY EITHER A BEAT OR A ALBUM (A COLLECTION OF BEATS) THE BEAT CRUD IS A WORK IN PROGRESS SO THE ALBUM IS THE 'PRODUCT' FOR PROJECT COMPLETION SAKE
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, String, Integer, INT, TIMESTAMP, DateTime, select
from marshmallow import ValidationError
from typing import List, Optional
import datetime
#MARK: imports 
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:duncan66@localhost/ecommerceapi'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)
#RELATIONSHIP TABLES FOR USER TO BEAT LINK AND ORDER TO USER/ALBUM LINKS
user_beat = Table(
    'user_beat',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('beat_id', ForeignKey('beat.id'), primary_key=True)
)

order_link = Table(
    'order_link',
    Base.metadata,
    Column('orderbox_id', ForeignKey('orderbox.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('album_id', ForeignKey('album.id'), primary_key=True)
)
#CLASSES FOR TABLES
class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), unique=True)
    # order_link: Mapped[int] = mapped_column(ForeignKey("orderbox.id"), nullable=True)

    user: Mapped[List["Beat"]] = relationship("Beat", secondary=user_beat)

class Beat(Base):
    __tablename__ = 'beat'
    id: Mapped[int] = mapped_column(primary_key=True)
    beat_name: Mapped[str] = mapped_column(String(60), nullable=False)
    album_id: Mapped[str] = mapped_column(ForeignKey('album.id'), nullable=True)
    beat_price: Mapped[str] = mapped_column(String(30), nullable=False)

    album: Mapped["Album"] = relationship(back_populates="beats") 

class Album(Base):
    __tablename__ = 'album'
    id: Mapped[int] = mapped_column(primary_key=True) 
    artist_name: Mapped[str] = mapped_column(String(60), nullable=False)
    album_price: Mapped[str] = mapped_column(String(10), nullable=False)
    album_name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)  
    # order_link: Mapped[int] = mapped_column(ForeignKey("orderbox.id"), nullable=True)

    beats: Mapped[List['Beat']] = relationship(back_populates='album')

class OrderBox(Base):
    __tablename__ = 'orderbox'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[DateTime] = Column(TIMESTAMP, default=datetime.datetime.utcnow)                                                                                                                                                                                            
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=True)
    album_id: Mapped[int] = mapped_column(ForeignKey('album.id'), nullable=True)
    
    # user: Mapped["User"] = relationship('User', secondary='order_link')
    # album: Mapped[List["Album"]] = relationship('Album', secondary='order_link') 
#SCHEMAS
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk=True
class BeatSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Beat 
        include_fk=True
class OrderBoxSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderBox
        include_fk=True
class AlbumSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Album
user_schema = UserSchema()
users_schema = UserSchema(many=True)
beat_schema = BeatSchema()
beats_schema = BeatSchema(many=True)
orderbox_schema = OrderBoxSchema()
ordersbox_schema = OrderBoxSchema(many=True)
album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)



#MARK: USER CRUD
@app.route('/user', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    new_user = User(name=user_data['name'], email=user_data['email'])
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
       
    if not user:
        return jsonify({'message': 'invalid user id'}), 400
    else:
        return user_schema.jsonify(user), 200 


@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({'message': 'invalid user id'}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user.name = user_data['name']
    user.email = user_data['email']

    db.session.commit()
    return user_schema.jsonify(user), 200

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"succefully deleted user {id}"}), 200
#MARK: BEATS CRUD
@app.route('/beat', methods=['POST'])
def create_beat():
    try:
        beat_data = beat_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 500
    new_beat = Beat(beat_name=beat_data['beat_name'], 
                    album_id=beat_data['album_id'],  
                    beat_price=beat_data['beat_price']
                    )
    db.session.add(new_beat)
    db.session.commit()
    return beat_schema.jsonify(new_beat), 201

@app.route('/beat', methods=['GET'])
def get_beat():
    query = select(Beat)
    beat = db.session.execute(query).scalars().all()

    return beat_schema.jsonify(beat), 200
#MARK: ALBUM CRUD 
@app.route('/album', methods=['POST'])
def create_album():
    try:
        album_data = album_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    new_album = Album(album_name=album_data['album_name'],
                      artist_name=album_data['artist_name'], 
                      album_price=album_data['album_price']
                      )
    db.session.add(new_album)
    db.session.commit()
    return album_schema.jsonify(new_album), 201

@app.route('/album/<int:id>', methods=['GET'])
def get_album(id):
    album = db.session.get(Album, id)
        
    if not album:
        return jsonify({'message': 'invalid user id'}), 400
    else:
        return album_schema.jsonify(album), 200

@app.route('/albums', methods=['GET'])
def get_albums():
    query = select(Album)
    albums = db.session.execute(query).scalars().all()

    return albums_schema.jsonify(albums), 200
#MARK: ORDER CRUD
@app.route('/orderbox', methods=['POST'])
def create_order():
    try:
        order_data = orderbox_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 500
    new_order = OrderBox(
                    user_id=order_data['user_id'],  
                    album_id=order_data['album_id']
                    )
    db.session.add(new_order)
    db.session.commit()
    return orderbox_schema.jsonify(new_order), 201

@app.route('/ordersbox', methods=['GET'])
def get_orders():
    query = select(OrderBox)
    ordersbox = db.session.execute(query).scalars().all()

    return ordersbox_schema.jsonify(ordersbox), 200

@app.route('/orderbox/<int:id>', methods=['GET'])
def get_order(id):
    orderbox = db.session.get(OrderBox, id)

    return orderbox_schema.jsonify(orderbox), 200

@app.route('/orderbox/<int:id>', methods=['PUT'])
def update_orderbox(id):
    orderbox = db.session.get(OrderBox, id)

    if not orderbox:
        return jsonify({'message': 'invalid order id'}), 400
    
    try:
        orderbox_data = orderbox_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    orderbox.order_date = orderbox_data['order_date']
    orderbox.user_id = orderbox_data['user_id']
    orderbox.album_id = orderbox_data['album_id']

    db.session.commit()
    return orderbox_schema.jsonify(orderbox), 200

@app.route('/orderbox/<int:id>', methods=['DELETE'])
def delete_orderbox(id):
    orderbox = db.session.get(OrderBox, id)

    if not orderbox:
        return jsonify({"message": "Invalid order id"}), 400
    
    db.session.delete(orderbox)
    db.session.commit()
    return jsonify({"message": f"succefully deleted order {id}"}), 200
#MARK: run app
if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)

