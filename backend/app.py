import os
from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY", "rr-track-logistics-development-secret"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

CORS(app)
JWTManager(app)

USERS = {
    "admin": {
        "password_hash": generate_password_hash("123456"),
        "rol": "admin",
    },
    "operador": {
        "password_hash": generate_password_hash("123456"),
        "rol": "operador",
    }
}

CAMIONES = [
    {
        "id": 1,
        "placa": "ABC-123",
        "modelo": "FH",
        "marca": "Volvo",
        "estado": "Disponible",
    },
    {
        "id": 2,
        "placa": "XYZ-789",
        "modelo": "Actros",
        "marca": "Mercedes-Benz",
        "estado": "En ruta",
    },
]
CONDUCTORES = []


def roles_requeridos(*roles):
    def decorator(view):
        @wraps(view)
        @jwt_required()
        def wrapped(*args, **kwargs):
            if get_jwt().get("rol") not in roles:
                return jsonify({"message": "No tienes permisos para esta operación."}), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator


def camion_por_id(camion_id):
    return next((camion for camion in CAMIONES if camion["id"] == camion_id), None)


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "servicio": "rr-track-logistics"})


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    usuario = str(data.get("usuario", "")).strip()
    password = str(data.get("password", ""))
    user = USERS.get(usuario)

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"message": "Usuario o contraseña incorrectos."}), 401

    token = create_access_token(identity=usuario, additional_claims={"rol": user["rol"]})
    return jsonify({"accessToken": token, "usuario": usuario}), 200


@app.get("/api/camiones")
@jwt_required()
def camiones():
    return jsonify(CAMIONES), 200


@app.post("/api/camiones")
@roles_requeridos("admin")
def registrar_camion():
    data = request.get_json(silent=True) or {}
    required = ("placa", "modelo", "marca")
    if any(not str(data.get(field, "")).strip() for field in required):
        return jsonify({"message": "placa, modelo y marca son obligatorios."}), 400

    camion = {
        "id": max((item["id"] for item in CAMIONES), default=0) + 1,
        "placa": str(data["placa"]).strip(),
        "modelo": str(data["modelo"]).strip(),
        "marca": str(data["marca"]).strip(),
        "estado": str(data.get("estado", "Disponible")).strip(),
    }
    CAMIONES.append(camion)
    return jsonify(camion), 201


@app.put("/api/camiones/<int:camion_id>")
@roles_requeridos("admin")
def actualizar_camion(camion_id):
    camion = camion_por_id(camion_id)
    if camion is None:
        return jsonify({"message": "Camión no encontrado."}), 404

    data = request.get_json(silent=True) or {}
    for field in ("placa", "modelo", "marca", "estado"):
        if field in data:
            camion[field] = str(data[field]).strip()
    return jsonify(camion), 200


@app.delete("/api/camiones/<int:camion_id>")
@roles_requeridos("admin")
def eliminar_camion(camion_id):
    camion = camion_por_id(camion_id)
    if camion is None:
        return jsonify({"message": "Camión no encontrado."}), 404
    CAMIONES.remove(camion)
    return jsonify({"message": "Camión eliminado."}), 200


@app.patch("/api/camiones/<int:camion_id>/estado")
@roles_requeridos("admin", "operador")
def actualizar_estado_camion(camion_id):
    camion = camion_por_id(camion_id)
    data = request.get_json(silent=True) or {}
    estado = str(data.get("estado", "")).strip()
    if camion is None:
        return jsonify({"message": "Camión no encontrado."}), 404
    if not estado:
        return jsonify({"message": "El estado es obligatorio."}), 400
    camion["estado"] = estado
    return jsonify(camion), 200


@app.post("/api/camiones/<int:camion_id>/ruta")
@roles_requeridos("admin")
def asignar_ruta(camion_id):
    camion = camion_por_id(camion_id)
    data = request.get_json(silent=True) or {}
    ruta = str(data.get("ruta", "")).strip()
    if camion is None:
        return jsonify({"message": "Camión no encontrado."}), 404
    if not ruta:
        return jsonify({"message": "La ruta es obligatoria."}), 400
    camion["ruta"] = ruta
    return jsonify(camion), 200


@app.get("/api/ubicaciones")
@roles_requeridos("admin", "operador")
def ubicaciones():
    return jsonify([]), 200


@app.route("/api/conductores", methods=["GET", "POST"])
@roles_requeridos("admin")
def gestionar_conductores():
    if request.method == "GET":
        return jsonify(CONDUCTORES), 200

    data = request.get_json(silent=True) or {}
    nombre = str(data.get("nombre", "")).strip()
    if not nombre:
        return jsonify({"message": "El nombre es obligatorio."}), 400
    conductor = {
        "id": max((item["id"] for item in CONDUCTORES), default=0) + 1,
        "nombre": nombre,
        "licencia": str(data.get("licencia", "")).strip(),
    }
    CONDUCTORES.append(conductor)
    return jsonify(conductor), 201


@app.get("/api/usuarios")
@roles_requeridos("admin")
def administrar_usuarios():
    return jsonify(
        [{"usuario": nombre, "rol": data["rol"]} for nombre, data in USERS.items()]
    ), 200


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"message": "Ruta no encontrada."}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify({"message": "Método HTTP no permitido."}), 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
