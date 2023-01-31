from flask.views import MethodView
from flask_smorest import  Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from db import db
from models import StoreModel, ItemModel, UserModel
from schemas import StoreSchema
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


blp = Blueprint("Stores", "stores", description="Operations on Stores")



@blp.route("/stores/<int:store_id>")
class Store(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store
        
    @jwt_required()
    def delete(self, store_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort (500, "Admin previllege required")
        store_items = ItemModel.query.filter_by(store_id=store_id).all()
        for item in store_items:
            db.session.delete(item)

        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit() 
    
        return {'message': "Store deleted"}
        

@blp.route("/stores")
class StoreList(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A store with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while trying to create the store.")
    
        return store 
            


    # @blp.arguments(StoreSchema)
    # @blp.response(200, StoreSchema)
    # def post(self, store_data):
    #     store = StoreModel(**store_data)
        
    #     try:
    #         db.session.add(store)
    #         db.session.commit()
    #     except SQLAlchemyError:
    #         abort(500, message='An error occured while creating a store')
        
    #     return store
    
        