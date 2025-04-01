# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, render_template
import os
import pymysql
import logging
import json
from collections import OrderedDict
import jwt
import datetime
from datetime import datetime as dt_datetime
import requests
from dotenv import load_dotenv

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.debug = True

load_dotenv()

# 統一的資料庫連接函數
def get_db_connection():
    try:
        logger.info("嘗試連接到資料庫...")
        con = pymysql.connect(
            host=os.getenv("host"),
            port=int(os.getenv("port")),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database"),
            connect_timeout=60,  # 連接超時 60 秒
            read_timeout=60,     # 讀取超時 60 秒
            write_timeout=60     # 寫入超時 60 秒
        )
        logger.info("資料庫連接成功")
        return con
    except pymysql.MySQLError as e:
        logger.error(f"資料庫連接失敗: {e}")
        raise

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

# API Routes
@app.route("/api/attractions")
def attractions():
    try:
        con = get_db_connection()
        cursor = con.cursor()

        attraction_list = []
        keyword = request.args.get('keyword')
        page = int(request.args.get('page', 0))
        
        if keyword:
            query = "SELECT * FROM attractions WHERE (name LIKE %s) OR (mrt = %s)"
            attraction_list.extend(['%' + keyword + '%', keyword])
        else:
            query = "SELECT * FROM attractions"

        query += " ORDER BY id LIMIT %s, 12"
        attraction_list.append(page * 12)

        cursor.execute(query, attraction_list)
        data = cursor.fetchall()

        next_page_query = "SELECT COUNT(*) FROM attractions LIMIT %s, 12"
        cursor.execute(next_page_query, [page * 12])
        next_page_data = cursor.fetchall()
        total_results = next_page_data[0][0] if next_page_data else 0

        response_data = OrderedDict()
        response_data["nextPage"] = page + 1 if len(data) >= 12 else None
        response_data["data"] = [] if len(data) > 0 else None

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

    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

@app.route("/api/attraction/<int:attractionId>")
def get_attraction(attractionId):
    try:
        con = get_db_connection()
        cursor = con.cursor()

        query = "SELECT * FROM attractions WHERE id = %s"
        cursor.execute(query, (attractionId,))
        data = cursor.fetchall()

        if not data:
            return jsonify({"error": True, "message": "景點編號不存在"}), 400

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

        con.close()
        return jsonify({"data": attraction})

    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

@app.route("/api/mrts")
def mrts():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        mrts_list = []

        query = "SELECT DISTINCT mrt FROM attractions ORDER BY (SELECT COUNT(*) FROM attractions AS a WHERE a.mrt = attractions.mrt) DESC"
        cursor.execute(query)
        mrt_results = cursor.fetchall()

        mrts_list = [mrt[0] for mrt in mrt_results]
        con.close()
        return jsonify({"data": mrts_list})

    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

@app.route('/api/user', methods=["POST"])
def signup():
    try:
        con = get_db_connection()
        cursor = con.cursor()

        signupName = request.form["signupName"]
        signupEmail = request.form["signupEmail"]
        signupPassword = request.form["signupPassword"]

        cursor.execute("SELECT * FROM membership WHERE email = %s", (signupEmail,))
        if cursor.fetchone():
            con.close()
            return jsonify({"error": True, "message": "這個電子郵箱已經被使用!"}), 400

        cursor.execute("INSERT INTO membership (name, email, password) VALUES (%s, %s, %s)",
                       (signupName, signupEmail, signupPassword))
        con.commit()
        con.close()
        return jsonify({"ok": True, "message": "註冊成功"}), 200

    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

@app.route('/api/user/auth', methods=["PUT"])
def signin():
    try:
        con = get_db_connection()
        cursor = con.cursor()

        signinEmail = request.form["signinEmail"]
        signinPassword = request.form["signinPassword"]

        cursor.execute("SELECT * FROM membership WHERE email = %s AND password = %s", (signinEmail, signinPassword))
        signinMembership = cursor.fetchall()

        if not signinMembership:
            con.close()
            return jsonify({"error": True, "message": "電子郵件或密碼錯誤"}), 400

        user_info = {
            "id": signinMembership[0][0],
            "name": signinMembership[0][1],
            "email": signinMembership[0][2]
        }
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        secret_key = "My_secret_key"
        token = jwt.encode({"data": user_info}, secret_key, algorithm="HS256")

        con.close()
        return jsonify({"token": token})

    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

def authenticate_token(f):
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        secret_key = "My_secret_key"
        if not token:
            return jsonify({"data": None})

        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            return jsonify({"data": None})

        jwt_token = token_parts[1]
        try:
            decode_token = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
            token_user_info = decode_token.get("data", None)
            if not token_user_info:
                return jsonify({"data": None})
            return f(token_user_info, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            logger.error("JWT Token 已過期")
            return jsonify({"data": None}), 400
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT Token 無效: {str(e)}")
            return jsonify({"data": None}), 400
    return decorated

@app.route("/api/user/auth", methods=["GET"])
@authenticate_token
def user_auth(current_user):
    return jsonify({"data": current_user})

@app.route("/api/booking", methods=["GET"])
def get_trip():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        token = request.headers.get("Authorization")
        secret_key = "My_secret_key"

        if not token:
            con.close()
            return jsonify({"data": None})

        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            con.close()
            return jsonify({"data": None})

        jwt_token = token_parts[1]
        decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        user_id = decoded["data"]["id"]

        cursor.execute('SELECT id FROM membership WHERE id = %s', (user_id,))
        member_id = cursor.fetchone()
        if not member_id:
            con.close()
            return jsonify({"data": None})
        member_id = member_id[0]

        cursor.execute('SELECT memberID, attractionID, date, time, price FROM booking WHERE memberID = %s', (member_id,))
        booking_info = cursor.fetchone()

        if not booking_info:
            con.close()
            return jsonify({"data": None})

        member_id, attraction_id, booking_info_date, booking_info_time, booking_info_price = booking_info

        cursor.execute('SELECT id, rownumber, name, address FROM attractions WHERE id = %s', (attraction_id,))
        attraction_info = cursor.fetchone()
        if not attraction_info:
            con.close()
            return jsonify({"data": None})

        attraction_id, attraction_rownumber, attraction_name, attraction_address = attraction_info

        img_query = "SELECT imageUrl FROM attractionImages WHERE attractionRownumber = %s"
        cursor.execute(img_query, (attraction_rownumber,))
        img_data = cursor.fetchall()
        image_url = img_data[0][0] if img_data else ""

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

        con.close()
        return jsonify({"data": booking_response_data})

    except jwt.ExpiredSignatureError:
        logger.error("Token 已過期")
        return jsonify({"error": "Token expired"}), 400
    except jwt.DecodeError:
        logger.error("Token 解碼失敗")
        return jsonify({"error": "Token decoding failed"}), 400
    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

@app.route("/api/booking", methods=["POST"])
def update_trip():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        token = request.headers.get("Authorization")
        secret_key = "My_secret_key"

        if not token:
            con.close()
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            con.close()
            return jsonify({"error": True, "message": "無效的 Token"}), 403

        jwt_token = token_parts[1]
        decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        user_id = decoded["data"]["id"]

        trip_reservation = request.get_json()
        attractionId = trip_reservation["attractionId"]
        date = trip_reservation["date"]
        time = trip_reservation["time"]
        price = trip_reservation["price"]

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
        con.close()
        return jsonify({"ok": True})

    except jwt.ExpiredSignatureError:
        logger.error("Token 已過期")
        return jsonify({"error": True, "message": "Token已過期"}), 400
    except jwt.InvalidTokenError as e:
        logger.error(f"Token 無效: {str(e)}")
        return jsonify({"error": True, "message": f"Token無效: {str(e)}"}), 400
    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

@app.route("/api/booking", methods=["DELETE"])
def delete_trip():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        token = request.headers.get("Authorization")
        secret_key = "My_secret_key"

        if not token:
            con.close()
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            con.close()
            return jsonify({"error": True, "message": "無效的 Token"}), 403

        jwt_token = token_parts[1]
        decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        user_id = decoded["data"]["id"]

        cursor.execute('SELECT id FROM membership WHERE id = %s', (user_id,))
        member_id = cursor.fetchone()[0]

        cursor.execute('SELECT memberID FROM booking WHERE memberID = %s', (member_id,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM booking WHERE memberID = %s", (member_id,))
            con.commit()

        con.close()
        return jsonify({"ok": True})

    except jwt.ExpiredSignatureError:
        logger.error("Token 已過期")
        return jsonify({"error": True, "message": "Token expired"}), 400
    except jwt.DecodeError:
        logger.error("Token 解碼失敗")
        return jsonify({"error": True, "message": "Token decoding failed"}), 400
    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

@app.route("/api/order", methods=["POST"])
def order_trip():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        token = request.headers.get("Authorization")
        secret_key = "My_secret_key"

        if not token:
            con.close()
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403

        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            con.close()
            return jsonify({"error": True, "message": "無效的 Token"}), 403

        jwt_token = token_parts[1]
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

        cursor.execute('SELECT * FROM ordersystem WHERE name = %s AND date = %s AND time = %s AND attractionId = %s',
                       (contact_name, trip_date, trip_time, trip_attraction_id))
        if cursor.fetchone():
            con.close()
            return jsonify({"error": True, "message": "訂單建立失敗，已存在相同訂單"}), 400

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
            return jsonify({
                "data": {
                    "number": order_num,
                    "payment": {"status": status_code, "message": "付款成功"},
                }
            }), 200
        else:
            con.close()
            return jsonify({"error": True, "message": req.json().get("msg")}), 400

    except jwt.ExpiredSignatureError:
        logger.error("Token 已過期")
        return jsonify({"error": True, "message": "Token expired"}), 400
    except jwt.DecodeError:
        logger.error("Token 解碼失敗")
        return jsonify({"error": True, "message": "Token decoding failed"}), 400
    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500

@app.route("/api/order/<int:orderNumber>", methods=["GET"])
def show_trip(orderNumber):
    try:
        con = get_db_connection()
        cursor = con.cursor()
        token = request.headers.get("Authorization")
        secret_key = "My_secret_key"

        if not token:
            con.close()
            return jsonify({"error": True, "message": "未提供有效的 Token"}), 403

        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            con.close()
            return jsonify({"error": True, "message": "無效的 Token"}), 403

        jwt_token = token_parts[1]
        decoded = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])

        query = "SELECT * FROM ordersystem WHERE orderNum = %s"
        cursor.execute(query, (orderNumber,))
        order_data = cursor.fetchone()

        if not order_data:
            con.close()
            return jsonify({"error": True, "message": "訂單不存在"}), 404

        attraction_id = order_data[3]
        query_attraction = "SELECT name, address, rownumber FROM attractions WHERE id = %s"
        cursor.execute(query_attraction, (attraction_id,))
        attraction_data = cursor.fetchone()

        if not attraction_data:
            con.close()
            return jsonify({"error": True, "message": "景點資料不存在"}), 500

        attraction_rownumber = attraction_data[2]
        img_query = "SELECT imageUrl FROM attractionImages WHERE attractionRownumber = %s"
        cursor.execute(img_query, (attraction_rownumber,))
        img_data = cursor.fetchall()
        image_url = img_data[0][0] if img_data else ""

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

        con.close()
        return jsonify({"data": order_info})

    except jwt.ExpiredSignatureError:
        logger.error("Token 已過期")
        return jsonify({"error": True, "message": "Token已過期"}), 400
    except jwt.InvalidTokenError:
        logger.error("Token 無效")
        return jsonify({"error": True, "message": "無效的Token"}), 400
    except pymysql.MySQLError as e:
        logger.error(f"資料庫錯誤: {e}")
        return jsonify({"error": True, "message": f"資料庫錯誤: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"伺服器錯誤: {e}")
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
