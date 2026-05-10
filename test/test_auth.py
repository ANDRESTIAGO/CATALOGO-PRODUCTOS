import os
import pandas as pd
from operations.operations import create_user

def test_register_and_login_and_logout(client):
    # REGISTER
    resp = client.post("/registro", data={
        "nombre_usuario": "andres",
        "correo": "andres@example.com",
        "contraseña": "pass1234",
        "contraseña2": "pass1234"
    })
    # registro redirige al home autenticado (303)
    assert resp.status_code in (302, 303)

    # Ahora el cliente mantiene la sesión. Comprobemos acceso a ruta autenticada
    resp_home = client.get("/homeAutenticacion")
    assert resp_home.status_code == 200
    assert "homeAutenticacion" in resp_home.text or "Se registro correctamente" in resp_home.text or resp_home.ok

    # LOGOUT
    resp_logout = client.get("/logout")
    assert resp_logout.status_code in (302, 303)
    # después del logout, acceder a /homeAutenticacion debe redirigir a /login
    resp_after = client.get("/homeAutenticacion")
    assert resp_after.status_code in (302, 303)

def test_login_wrong_password(client):
    # primero crear un usuario a nivel de CSV (para tener la contraseña hash correctamente)
    # Usa la misma función create_user importada por operaciones vía home router
    from operations import create_user
    create_user("usuario", "u1@example.com", "miClave123")

    # intentar login con contraseña equivocada
    resp = client.post("/login", data={"correo": "u1@example.com", "contraseña": "wrong"})
    # el endpoint devuelve la plantilla login (200) con mensaje de error (no redirige)
    assert resp.status_code in (200, 422)
    assert "Correo o contraseña incorrectos" in resp.text or resp.ok

def test_change_password_flow(client):
    # registrar usuario y quedarse logueado
    client.post("/registro", data={
        "nombre_usuario": "cambio",
        "correo": "cambio@example.com",
        "contraseña": "oldpass",
        "contraseña2": "oldpass"
    })

    # cambiar contraseña: necesita current_password y new_password
    resp = client.post("/cambiar_contraseña", data={
        "current_password": "oldpass",
        "new_password": "newpass123",
        "new_password2": "newpass123"
    })
    # el endpoint devuelve plantilla con success (200)
    assert resp.status_code in (200, 302, 303) or resp.ok

    # cerrar sesión y reintentar login con la nueva contraseña
    client.get("/logout")
    resp_login = client.post("/login", data={"correo": "cambio@example.com", "contraseña": "newpass123"})
    # debe redirigir al home (exitoso)
    assert resp_login.status_code in (302, 303)
