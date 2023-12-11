from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import FileResponse
from database import (get_connection, create_table, get_users,
                      get_db_table, check_exist, insert_row)

from typing import Optional
from pydantic import BaseModel
import base64

app = FastAPI()

class User(BaseModel):
    fullname: str
    email: str
    password : str
    phone: int
    profilepic: UploadFile = File(...)


@app.get('/user')
def get_user(*, user_id: Optional[int] = None, profile_pic: Optional[bool] = None):
    _, cur = get_connection()
    data = get_users(cur, 'Users',user_id)
    if profile_pic and user_id and data[0]:
        images = get_db_table()
        image_data = images.find_one({'user_id':user_id})
        ext = image_data['extension']
        with open(f"current.{ext}", "wb") as img:
            img.write(base64.b64decode(image_data['b_format']))

        return FileResponse(img.name)
    return {"data" : data}

@app.post("/register")
def register(user: User = Depends()):
    table_name = 'Users'
    profilepic = user.profilepic
    pic_ext = profilepic.filename.split('.')[-1]
    user_dict = user.dict()
    del user_dict['profilepic']

    conn, _ = get_connection()
    cur = create_table(conn,table_name)

    if not check_exist(cur, table_name, user_dict['email'], user_dict['phone']):

        user_id = insert_row(conn ,cur, table_name, user_dict)

        b_format = base64.b64encode(profilepic.file.read())
        image = {
                    'b_format': b_format,
                    'extension' : pic_ext,
                    'user_id' : user_id
                }

        images = get_db_table()
        image_id = images.insert_one(image).inserted_id
        
        return {'Response' : 'Registered Successfully'}
    else:
        return {'Exists' : 'Email or phone already exists'}