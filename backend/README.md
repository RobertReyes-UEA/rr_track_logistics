# Backend Flask

API de desarrollo para RR Track Logistics.

## Instalar

Desde la carpeta `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar

```powershell
python app.py
```

El servidor escucha en `http://0.0.0.0:5000`, por lo que Flutter puede acceder mediante la IP local de la computadora.

## Credenciales de prueba

```text
Usuario: admin
Contraseña: 123456

Usuario: operador
Contraseña: 123456
```

## Rutas

- `GET /api/health`: verifica que el servidor esté activo.
- `POST /api/auth/login`: recibe `usuario` y `password`, y devuelve `accessToken`.
- `GET /api/camiones`: administrador u operador.
- `POST /api/camiones`: administrador, registra un camión.
- `PUT /api/camiones/<id>`: administrador, actualiza un camión.
- `DELETE /api/camiones/<id>`: administrador, elimina un camión.
- `POST /api/camiones/<id>/ruta`: administrador, asigna una ruta.
- `PATCH /api/camiones/<id>/estado`: administrador u operador, actualiza el estado.
- `GET /api/ubicaciones`: administrador u operador.
- `GET /api/conductores` y `POST /api/conductores`: administrador.
- `GET /api/usuarios`: administrador.

Todas las rutas protegidas requieren el encabezado:

```text
Authorization: Bearer <accessToken>
```

Un operador recibe HTTP `403` al intentar registrar, actualizar o eliminar camiones,
asignar rutas, gestionar conductores o consultar usuarios.

Para cambiar la clave JWT en producción, define la variable `JWT_SECRET_KEY` antes de iniciar el servidor.
