from connection_sql import get_db_connection
from flask import Flask, jsonify, request

from flask_marshmallow import Marshmallow #create schema objects - determine the shape of the data we're sending and receiving
from marshmallow import ValidationError, fields
from mysql.connector import Error


app = Flask(__name__)
ma = Marshmallow(app)

app.json.sort_keys = False
# Schemas
class MemberSchema(ma.Schema):
    name = fields.String(required=True) 
    email = fields.String(required=True)
    phone = fields.String(required=True)
    membership_start = fields.Date(required=True)
    
    class Meta:
      fields = ('member_id', 'name', 'email', 'phone', 'membership_start')

member_schema = MemberSchema()      
members_schema = MemberSchema(many=True)
 

@app.route('/members', methods=['POST'])
def add_member():
    member_data = member_schema.load(request.json)
    print(member_data)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    name = member_data["name"]
    email = member_data["email"]
    phone = member_data["phone"]
    membership_start = member_data["membership_start"]
    
    new_member = (name, email, phone, membership_start)
    query = "INSERT INTO members(name, email, phone, membership_start) VALUES(%s, %s, %s, %s)"
    cursor.execute(query, new_member)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"Message": "Member was added successfully"}), 201
    


@app.route('/members', methods = ['GET'])
def get_members():  
   conn = get_db_connection()
   cursor = conn.cursor(dictionary=True)
   cursor.execute('SELECT * FROM members')
   
   members = cursor.fetchall()
   print(members)
   cursor.close()
   conn.close()
   
   return members_schema.jsonify(members)
    
  
@app.route("/members/<int:id>", methods=["PUT"]) 
def update_member(id):
    try: 
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        name = member_data['name']
        email = member_data["email"]
        phone = member_data["phone"]
        membership_start = member_data["membership_start"]

        query = "UPDATE Members SET name = %s, email = %s, phone = %s, membership_start= %s WHERE member_id = %s"
        updated_member = (name, email, phone, membership_start, id)
        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Members details updated successfully"}), 200 

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"message": "Internal Server Error"}), 500 
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500 
        cursor = conn.cursor()
        member_to_remove = (id,)

        query = "SELECT * FROM members WHERE member_id = %s"
        cursor.execute(query, member_to_remove)
        member = cursor.fetchone() 
        
        if not member:
            return jsonify({"message": "Member not found"}), 404 
          
        query = "DELETE FROM members WHERE member_id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()
        
        # Also delete associated sessions with this member
        query = "DELETE FROM sessions WHERE member_id = %s"
        cursor.execute(query, member_to_remove)

        return jsonify({"message": "Member Removed Successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# =====================================================================================
# ====================|| CRUD Operations for Sessions Table ||=========================
# =====================================================================================
class SessionSchema(ma.Schema):
    member_id = fields.Int(required=True) 
    date = fields.Date(required=True)
    duration = fields.Int(required=True)
    session_type = fields.String(required=True)
    
    class Meta:
      fields = ('member_id', 'date', 'duration', 'session_type')

session_schema = SessionSchema()      
sessions_schema = SessionSchema(many=True)



@app.route('/sessions', methods=['POST'])
def schedule_session():
    conn = get_db_connection()
    if conn is None:
      return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    
    session_data = session_schema.load(request.json)
    member_id = session_data["member_id"]
    date = session_data["date"]
    duration = session_data["duration"]
    session_type = session_data["session_type"]
    
    query = "INSERT INTO sessions(member_id, date, duration, session_type) VALUES(%s, %s, %s, %s)"
    cursor.execute(query, (member_id, date, duration, session_type))
    conn.commit()

    conn.close()
    cursor.close()    
    
    return jsonify({"Message": "New session was created"})
    
    
    
@app.route('/sessions', methods = ['GET'])
def get_sessions():  
   conn = get_db_connection()
   cursor = conn.cursor(dictionary=True)
   cursor.execute('SELECT * FROM sessions')
   
   sessions = cursor.fetchall()
   print(sessions)
   cursor.close()
   conn.close()
   
   return sessions_schema.jsonify(sessions)




@app.route("/sessions/<int:id>", methods=["PUT"]) 
# id refers to session id
def reschedule_session(id):
    try: 
        session_data = session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        member_id = session_data['member_id']
        date = session_data["date"]
        duration = session_data["duration"]
        session_type = session_data["session_type"]

        query = "UPDATE Sessions SET date = %s, duration = %s, session_type= %s WHERE member_id = %s AND session_id= %s"
        updated_session = (date, duration, session_type, member_id, id)
        cursor.execute(query, updated_session)
        conn.commit()

        return jsonify({"message": "Session details updated successfully"}), 200 

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"message": "Internal Server Error"}), 500 
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/sessions/<int:id>', methods=['GET'])
# id refers to member id
def get_member_all_sessions(id):
   conn = get_db_connection()
   cursor = conn.cursor(dictionary=True)
   query = 'SELECT * FROM sessions WHERE member_id = %s'
   cursor.execute(query, (id,))
   
   sessions = cursor.fetchall()
   print(sessions)
   cursor.close()
   conn.close()
   
   return sessions_schema.jsonify(sessions)


if __name__ == "__main__": #making sure only app.py can run the flask application
    app.run(debug=True)