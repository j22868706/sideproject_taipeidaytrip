# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, render_template
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

import json
from collections import OrderedDict
import jwt
import datetime
from datetime import datetime as dt_datetime 
import requests
from dotenv import load_dotenv
import os
import pymysql

app.debug = True

load_dotenv()

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")


@app.route("/api/attractions")
def attractions():
    try:
        con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database"),
            connect_timeout=60 
        )

        cursor = con.cursor()

        attraction_list = []
        keyword = request.args.get('keyword')
        page = int(request.args.get('page', 0))
        
        if keyword:
            query = "SELECT * FROM attractions WHERE (name LIKE %s ) OR (mrt = %s )"
            attraction_list.append('%' + keyword + '%')
            attraction_list.append(keyword)
        else:
            query = "SELECT * FROM attractions"

        query += " ORDER BY id LIMIT %s, 12"
        attraction_list.append(page * 12)

        cursor.execute(query, attraction_list)

        data = cursor.fetchall()

        next_page_query = "SELECT COUNT(*) FROM attractions LIMIT %s, 12"
        attraction_list = [page * 12] 
        cursor.execute(next_page_query, attraction_list)
        next_page_data = cursor.fetchall()

        if next_page_data:
            total_results = next_page_data[0][0]
        else: 
             total_results = 0  

        response_data = OrderedDict()
        response_data["nextPage"] = page + 1 if len(data) >= 12 else None  
        response_data["data"] = None if len(data) == 0 else []

        for row in data:
            attraction = OrderedDict()
            attraction["id"] = row[0]
            attraction["name"] = row[2]
            attraction["category"] = row[3]
            attraction["description"] = row[4]
            attraction["address"] = row[5]
            attraction["transport"] = row[6]
            attraction["mrt"] = row[7]
            attraction["lat"] = row[8]
            attraction["lng"] = row[9]
            attraction["images"] = []

            img_query = "SELECT imageUrl FROM attractionImages WHERE attractionRownumber = %s"
            cursor.execute(img_query, (row[1],))
            img_data = cursor.fetchall()

            attraction["images"] = [img[0] for img in img_data]

            response_data["data"].append(attraction)
        con.close()
        return jsonify(response_data)

    except Exception as e:
        error_response = {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }
        return jsonify({error_response}), 500


@app.route("/api/attraction/<int:attractionId>")
def get_attraction(attractionId):
    try:
        con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )

        cursor = con.cursor()

        query = "SELECT * FROM attractions WHERE id = %s"
        cursor.execute(query, (attractionId,))
        data = cursor.fetchall()

        if len(data) == 0:
            error_response = {
                "error": True,
                "message": "請按照情境提供對應的錯誤訊息"
            }
            return json.dumps(error_response, ensure_ascii=False).encode('utf8'), 400  
        
        attraction_id_response = {"data": {}}

        attraction = {
            "id": data[0][0],
            "name": data[0][2],
            "category": data[0][3],
            "description": data[0][4],
            "address": data[0][5],
            "transport": data[0][6],
            "mrt": data[0][7],
            "lat": data[0][8],
            "lng": data[0][9],
            "images": []
        }

        img_query = "SELECT imageUrl FROM attractionImages WHERE attractionRownumber = %s"
        cursor.execute(img_query, (data[0][1],))
        img_data = cursor.fetchall()

        attraction["images"] = [img[0] for img in img_data]
        attraction_id_response["data"] = attraction

        con.close()

        return jsonify(attraction_id_response)

    except Exception as e:
        error_response = {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }
        return jsonify(error_response), 500  

@app.route("/api/mrts")
def mrts():
    try:    
        con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )

        cursor = con.cursor()
        mrts_list = []
        mrts_response_data = {"data": mrts_list}

        query = "SELECT DISTINCT mrt FROM attractions ORDER BY (SELECT COUNT(*) FROM attractions AS a WHERE a.mrt = attractions.mrt) DESC"
        cursor.execute(query)
        mrt_results = cursor.fetchall()

        for mrt_result in mrt_results:
            mrts_list.append(mrt_result[0])

        cursor.close()
        con.close() 

        return jsonify(mrts_response_data)
      
    except Exception as e:
        mrt_error_response = {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }
        print("Error:", e)
        return jsonify(mrt_error_response), 500 
    
@app.route('/api/user', methods=["POST"])
def signup():
    con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
    )
    signupName = request.form["signupName"]
    signupEmail = request.form["signupEmail"]
    signupPassword = request.form["signupPassword"]

    cursor = con.cursor()

    cursor.execute("SELECT * FROM membership WHERE email = %s", (signupEmail,))
    existing_user = cursor.fetchone()

    if existing_user:
        con.close()
        signup_error_response = {"error": True, "message": "這個電子郵箱已經被使用!"}
        return jsonify(signup_error_response), 400
    try:
        cursor.execute("INSERT INTO membership (name, email, password) VALUES (%s, %s, %s)",
                       (signupName, signupEmail, signupPassword))
        con.commit()
        con.close()
        signup_success_response = {"ok": True, "message": "註冊成功"}
        return jsonify(signup_success_response), 200
    except Exception as e:
        con.close()
        print("Error:", e)
        signup_error_response = {"error": True, "message": "註冊失敗"}
        return jsonify(signup_error_response), 500

@app.route('/api/user/auth', methods=["PUT"])
def signin():
    try:
        con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        signinEmail = request.form["signinEmail"]
        signinPassword = request.form["signinPassword"]
        cursor = con.cursor()

        cursor.execute("SELECT * FROM membership WHERE email = %s AND password =%s" , (signinEmail, signinPassword))
        signinMembership = cursor.fetchall()
        for signinRow in signinMembership:
            if signinRow[2] == signinEmail and signinRow[3] == signinPassword:
                user_info = {
                   "id": signinRow[0],
                   "name": signinRow[1],
                   "email": signinRow[2]
                }
                expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
                secret_key = "My_secret_key"
                token = jwt.encode({"data": user_info}, secret_key, algorithm="HS256")
                return jsonify({"token": token})
        return jsonify({"error":True, "message":"電子郵件或密碼錯誤"}), 400 
    except Exception as e:
        signin_error_response = {
        "error": True,
        "message": "請按照情境提供對應的錯誤訊息"
        }
        return jsonify(signin_error_response), 500 

def authenticate_token(f):
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        secret_key = "My_secret_key"
        if token is None:
            return jsonify(data=None)
        
        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            return jsonify(data=None)
        
        jwt_token = token_parts[1]
        
        try:
            decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
            print(decode_token)
            token_user_info = decode_token.get("data", None)
            if token_user_info is None:
                return jsonify(data=None)
            return jsonify(data=token_user_info)
        except jwt.ExpiredSignatureError:
            print("JWTToken過期")
            return jsonify(data=None), 400
        except jwt.InvalidTokenError as e:
            print("JWTToken無效:", str(e))
            return jsonify(data=None), 400
    return decorated


@app.route("/api/user/auth", methods=["GET"])
@authenticate_token
def user_auth(current_user):
    print(current_user)
    return jsonify(data=current_user)

@app.route("/api/booking", methods=["GET"])
def get_trip():
    con = pymysql.connect(
        host=os.getenv("host"),
            port=int(os.getenv("port")),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )
    cursor = con.cursor()
    token = request.headers.get("Authorization")
    secret_key = "My_secret_key"

    if token:
        token_parts = token.split()
        if len(token_parts) == 2 and token_parts[0].lower() == "bearer":
            jwt_token = token_parts[1]
            try:
                decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
                user_id = decoded["data"]["id"]
                cursor.execute('SELECT id FROM membership WHERE id = %s', (user_id,))
                member_id = cursor.fetchone()[0]
                cursor.execute('SELECT memberID FROM booking WHERE memberID = %s', (member_id,))
                existing_booking = cursor.fetchone()

                if existing_booking:
                    searched_booking_query = "SELECT memberID, attractionID, date, time, price FROM booking WHERE memberID = %s"
                    cursor.execute(searched_booking_query, (member_id,))
                    booking_info = cursor.fetchone()

                    if booking_info:
                        member_id, attraction_id, booking_info_date, booking_info_time, booking_info_price = booking_info

                        search_attraction_info_query = "SELECT id, rownumber, name, address FROM attractions WHERE id = %s"
                        cursor.execute(search_attraction_info_query, (attraction_id,))
                        attraction_info = cursor.fetchone()

                        if attraction_info:
                            attraction_id, attraction_rownumber, attraction_name, attraction_address = attraction_info



                            img_query = "SELECT imageUrl FROM attractionImages WHERE attractionRownumber = %s"
                            cursor.execute(img_query, (attraction_rownumber,))
                            img_data = cursor.fetchall()
                            image_url = img_data[0][0]  
                        
                        attraction = {
                            "id": attraction_id,
                            "name": attraction_name,
                            "address": attraction_address,
                            "images": image_url
                        }
                        
                        booking_response_data = {
                            "attraction": attraction,
                            "date": booking_info_date,
                            "time": booking_info_time,
                            "price": booking_info_price,
                        }
                        return jsonify({"data": booking_response_data})
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"})
            except jwt.DecodeError:
                return jsonify({"error": "Token decoding failed"})
            except Exception as e:
                return jsonify({"error": str(e)})
    
    return jsonify({"data": None})

@app.route("/api/booking", methods=["POST"])
def update_trip():
    con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
    )
    cursor = con.cursor()
    token = request.headers.get("Authorization")
    secret_key = "My_secret_key"

    trip_reservation = request.get_json()
    attractionId = trip_reservation["attractionId"]
    date = trip_reservation["date"]
    time = trip_reservation["time"]
    price = trip_reservation["price"]

    if token:
        token_parts = token.split()
        if len(token_parts) == 2 and token_parts[0].lower() == "bearer":
            jwt_token = token_parts[1]
            try:
                decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
                user_id = decoded["data"]["id"]
                cursor.execute('SELECT id FROM membership WHERE id = %s', (user_id,))
                member_id = cursor.fetchone()[0]
                cursor.execute('SELECT memberID FROM booking WHERE memberID = %s', (member_id,))
                existing_booking = cursor.fetchone()


                if existing_booking:
                    update_booking = "UPDATE booking SET attractionID = %s, date = %s, time = %s, price = %s WHERE memberID = %s"
                    cursor.execute(update_booking, (attractionId, date, time, price, member_id))
                else:
                    insert_booking = "INSERT INTO booking (memberID, attractionID, date, time, price) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(insert_booking, (member_id, attractionId, date, time, price))

                con.commit()
                return jsonify({"ok": True})

            except jwt.ExpiredSignatureError:
                return jsonify({
                    "error": True,
                    "message": "Token已過期"
                }), 400
            except jwt.InvalidTokenError as e:
                return jsonify({
                    "error": True,
                    "message": f"Token無效: {str(e)}"
                }), 400
            except Exception as e:
                return jsonify({
                    "error": True,
                    "message": f"伺服器內部錯誤: {str(e)}"
                }), 500

    return jsonify({
        "error": True,
        "message": "未登入系統，拒絕存取"
    }), 403

@app.route("/api/booking", methods=["DELETE"])
def delete_trip():
    con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
    )
    cursor = con.cursor()
    token = request.headers.get("Authorization")
    secret_key = "My_secret_key"

    if token:
        token_parts = token.split()
        if len(token_parts) == 2 and token_parts[0].lower() == "bearer":
            jwt_token = token_parts[1]
            try:
                decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
                user_id = decoded["data"]["id"]
                cursor.execute('SELECT id FROM membership WHERE id = %s', (user_id,))
                member_id = cursor.fetchone()[0]
                cursor.execute('SELECT memberID FROM booking WHERE memberID = %s', (member_id,))
                existing_booking = cursor.fetchone()

                if existing_booking:
                    delete_booking_query = "DELETE FROM booking WHERE memberId = %s"
                    cursor.execute(delete_booking_query, (member_id,))

                    con.commit()
                    con.close()

                    return jsonify({"ok": True})
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"})
            except jwt.DecodeError:
                return jsonify({"error": "Token decoding failed"})
            except Exception as e:
                return jsonify({"error": str(e)})
    return jsonify({"error": True, "message": "請按照情境提供對應的錯誤訊息"})


@app.route("/api/order", methods=["POST"])
def order_trip():
    con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
    )
    cursor = con.cursor()
    token = request.headers.get("Authorization")
    secret_key = "My_secret_key"

    if token:
        token_parts = token.split()
        if len(token_parts) == 2 and token_parts[0].lower() == "bearer":
            jwt_token = token_parts[1]
            try:
                decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
                data = request.get_json()
                user_id = decoded["data"]["id"]
                prime = data['prime']
                price = data['order']['price'][0]  
                trip_attraction_id = data['order']['trip']['attraction']['id'][0]                  
                trip_date = data['order']['trip']['date'][0]  
                trip_time = data['order']['trip']['time'][0]  
                contact_name = data['order']['contact']['name']
                contact_email = data['order']['contact']['email']
                contact_phone = data['order']['contact']['phone']
                current_time = dt_datetime.now().strftime('%Y%m%d%H%M%S')
                order_num = current_time
                
                cursor.execute('SELECT * FROM ordersystem WHERE name = %s AND date = %s AND time = %s AND attractionId = %s', (contact_name, trip_date, trip_time, trip_attraction_id))
                existing_order = cursor.fetchone()

                if existing_order:
                    return jsonify({"error": True, "message" :"訂單建立失敗，已存在相同訂單"})
                else:
                    cursor.execute('INSERT INTO ordersystem (orderNum, memberId, attractionId, date, time, price, email, name, phone, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                   (order_num, user_id, trip_attraction_id, trip_date, trip_time, price, contact_email, contact_name, contact_phone, 'Pending'))

                    order_data = {
                        "prime": prime,
                        "partner_key": 'partner_b0OKh6UYc94AT4ThSiORUeEoiBJBNIsMofJjaVZlzN2N9nmP7vwLvQ8q',
                        "merchant_id": 'j22868706_TAISHIN',	
                        "details": "TaiPei Day Trip Booking",
                        "amount": price,
                        "cardholder": {
                            "phone_number": contact_phone,
                            "name": contact_name,
                            "email": contact_email,
                        },
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "x-api-key": 'partner_b0OKh6UYc94AT4ThSiORUeEoiBJBNIsMofJjaVZlzN2N9nmP7vwLvQ8q',
                    }
                    url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
                    req = requests.post(url, headers=headers, json=order_data, timeout=30)
                    status_code = req.json().get("status")                    
                    if status_code == 0:
                        cursor.execute('UPDATE ordersystem SET status = %s WHERE orderNum = %s', ('confirm', order_num))
                        con.commit()
                        con.close()

                        success = {
                            "data": {
                                "number": order_num,
                                "payment": {"status": status_code, "message": "付款成功"},
                            }
                        }
                        return jsonify(success), 200
                    else:
                        return jsonify({"error": True, "message": req.json().get("msg")})
                    
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"})
            except jwt.DecodeError:
                return jsonify({"error": "Token decoding failed"})
            except Exception as e:
                return jsonify({"error": str(e)})
    return jsonify({"error": True, "message": "請按照情境提供對應的錯誤訊息"})

@app.route("/api/order/<int:orderNumber>", methods=["GET"])
def show_trip(orderNumber):
    con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
    )
    cursor = con.cursor()
    token = request.headers.get("Authorization")
    secret_key = "My_secret_key"

    if token:
        token_parts = token.split()
        if len(token_parts) == 2 and token_parts[0].lower() == "bearer":
            jwt_token = token_parts[1]
            try:
                decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
                if decoded:
                    query = "SELECT * FROM ordersystem WHERE orderNum = %s"
                    cursor.execute(query, (orderNumber,))
                    order_data = cursor.fetchone()
                    if order_data:
                        attraction_id = order_data[3]
                        query_attraction = "SELECT name, address, rownumber FROM attractions WHERE id = %s"
                        cursor.execute(query_attraction, (attraction_id,))
                        attraction_data = cursor.fetchone()
                        if attraction_data:
                            attractionRownumber = attraction_data[2]
                            img_query = "SELECT imageUrl FROM attractionImages WHERE attractionRownumber = %s"
                            cursor.execute(img_query, (attractionRownumber,))
                            img_data = cursor.fetchall()
                            image_url = img_data[0][0]                             
                        order_info = {
                            "number": order_data[1],
                            "price": order_data[6],
                            "trip": {
                                "attraction": {
                                    "id": order_data[3],
                                    "name": attraction_data[0],
                                    "address": attraction_data[1],
                                    "image": image_url
                            },
                                "date": order_data[4],
                                "time": order_data[5]
                            },
                            "contact": {
                                "name": order_data[8],
                                "email": order_data[7],
                                "phone": order_data[9],
                            },
                            "status": order_data[10]
                        }
                        return jsonify({"data": order_info})
                    else:
                        return jsonify({"error": "訂單不存在"})
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token已過期"})
            except jwt.InvalidTokenError:
                return jsonify({"error": "無效的Token"})
    
    return jsonify({"error": "未提供有效的Token"})


