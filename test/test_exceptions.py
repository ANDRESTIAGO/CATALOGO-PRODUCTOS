import pandas as pd
from operations.operations import create_user


def test_modify_motherboard_forbidden(client):
    # crear usuario y orden
    client.post("/registro", data={
        "nombre_usuario": "user_m",
        "correo": "user_m@example.com",
        "contraseña": "p",
        "contraseña2": "p"
    })
    # crear orden con motherboard id=1
    client.post("/add", data={
        "nombre_orden": "Orden-MB",
        "motherboard_id": 1,
        "cpu_id": 2,
        "ram_id": 3,
        "gpu_id": 4,
        "disco_id": 5
    })

    # intentar modificar la motherboard (original tipo Motherboard)
    resp = client.post("/modificar", data={
        "orden": "Orden-MB",
        "componente_id_original": 1,  # motherboard id
        "nuevo_id": 2  # trying to replace with CPU...
    })
    # endpoint should return 400 due to HTTPException(status_code=400, detail="No puedes modificar la placa madre...")
    assert resp.status_code == 400

def test_delete_order_no_permission(client):
    # crear usuario A y una orden
    client.post("/registro", data={
        "nombre_usuario": "userA",
        "correo": "userA@example.com",
        "contraseña": "a",
        "contraseña2": "a"
    })
    client.post("/add", data={
        "nombre_orden": "Orden-A",
        "motherboard_id": 1,
        "cpu_id": 2,
        "ram_id": 3,
        "gpu_id": 4,
        "disco_id": 5
    })

    # logout A
    client.get("/logout")

    # login B
    client.post("/registro", data={
        "nombre_usuario": "userB",
        "correo": "userB@example.com",
        "contraseña": "b",
        "contraseña2": "b"
    })

    # intentar eliminar "Orden-A" (que pertenece a userA) -> should raise 403
    resp = client.post("/eliminar", data={"orden": "Orden-A"})
    assert resp.status_code == 403
