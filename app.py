# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

import mysql.connector

import datetime
import pytz

from flask_cors import CORS, cross_origin

con = mysql.connector.connect(
    host="82.197.82.90",  # Host de la base de datos
    database="u861594054_prac4_tania",  # Nombre de la base de datos
    user="u861594054_tania_pr4",  # Usuario
    password="b8O&lFD^"  # Contraseña
)

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return render_template("index.html")

@app.route("/app")
def app2():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return "<h5>Hola, soy la view app</h5>"

@app.route("/rentas")
def rentas():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT rentas.idRenta, 
           rentas.descripcion, 
           DATE_FORMAT(rentas.fechaHoraInicio, '%d/%m/%Y %H:%i:%s') AS fechaHoraInicio, 
           DATE_FORMAT(rentas.fechaHoraFin, '%d/%m/%Y %H:%i:%s') AS fechaHoraFin,
           trajes.nombreCorto
    FROM rentas
    INNER JOIN trajes ON rentas.idTraje = trajes.idTraje
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    return render_template("rentas.html", rentas=registros)

@app.route("/trajes")
def trajes():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT * FROM trajes
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    return render_template("trajes.html", trajes=registros)

@app.route("/rentas/buscar", methods=["GET"])
def buscarRentas():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT rentas.idRenta, 
           rentas.descripcion, 
           DATE_FORMAT(rentas.fechaHoraInicio, '%d/%m/%Y %H:%i:%s') AS fechaHoraInicio, 
           DATE_FORMAT(rentas.fechaHoraFin, '%d/%m/%Y %H:%i:%s') AS fechaHoraFin,
           trajes.*
    FROM rentas
    INNER JOIN trajes ON rentas.idTraje = trajes.idTraje
    WHERE rentas.descripcion LIKE %s
    OR    trajes.nombre LIKE %s
    ORDER BY rentas.idRenta DESC
    LIMIT 10 OFFSET 0
    """
    val    = (busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()
    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []

    finally:
        con.close()

    return make_response(jsonify(registros))

@app.route("/renta", methods=["POST"])
def guardarRenta():
    if not con.is_connected():
        con.reconnect()

    idRenta    = request.form["idRenta"]
    descripcion = request.form["descripcion"]
    fechaHoraInicio = request.form["fechaHoraInicio"]
    fechaHoraFin = request.form["fechaHoraFin"]
    idTraje    = request.form["idTraje"]

    cursor = con.cursor()

    if idRenta:
        sql = """
        UPDATE rentas
        SET descripcion = %s,
            fechaHoraInicio = %s,
            fechaHoraFin = %s,
            idTraje = %s
        WHERE idRenta = %s
        """
        val = (descripcion, fechaHoraInicio, fechaHoraFin, idTraje, idRenta)
    else:
        sql = """
        INSERT INTO rentas (descripcion, fechaHoraInicio, fechaHoraFin, idTraje)
        VALUES (%s, %s, %s, %s)
        """
        val = (descripcion, fechaHoraInicio, fechaHoraFin, idTraje)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({}))

@app.route("/renta/<int:idRenta>")
def editarRenta(idRenta):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idRenta, descripcion, fechaHoraInicio, fechaHoraFin, idTraje
    FROM rentas
    WHERE idRenta = %s
    """
    val    = (idRenta,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))
