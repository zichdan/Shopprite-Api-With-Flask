from flask.views import MethodView
from flask_smorest import abort, Blueprint
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required, get_jwt, get_jwt_identity 

from db import db 
from blocklist import BLOCKLIST
from schemas import UserSchema
from models import UserModel 


blp = Blueprint('Users', "users", description="Operation on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username==user_data["username"]).first():
            abort(409, message="A user with this username already exists.")
            
        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201
    
    
@blp.route("/login")  
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
             UserModel.username==user_data["username"]
        ).first()
        
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            return{"access_token": access_token, "refresh_token": refresh_token }
        
        abort(401, message="Invalid credentials.")  
        
    
@blp.route("/refresh")
class RefreshToken(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}  

        
    
       
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        
        return{"message": "Successfully logged out."}
    
    
    
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    
    @jwt_required()
    def delete(self, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message= "admin previllege required")
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return {"message": "User deleted successfully."}, 200
    
    





