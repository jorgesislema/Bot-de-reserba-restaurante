"""Tests funcionales de reservas: disponibilidad, validaciones y doble reserva."""

import threading
from datetime import date, timedelta

import pytest
from database.db_manager import (
    RestaurantDB,
    ReservaDuplicadaError,
    ReservaFueraDeHorarioError,
    ReservaInvalidaError,
    ReservaNoDisponibleError,
)

FUTURA = (date.today() + timedelta(days=30)).isoformat()


def _datos(**kwargs):
    datos = {
        "fecha": FUTURA,
        "hora": "20:00",
        "personas": 2,
        "nombre_contacto": "Cliente Test",
        "telefono": "+593900000001",
    }
    datos.update(kwargs)
    return datos


def _agotar_slot(db, prefijo_tel: str):
    """Crea reservas que agotan la capacidad total del slot 20:00."""
    por_reserva = min(db.max_personas_por_reserva, db.capacidad_total)
    faltan = db.capacidad_total
    i = 0
    while faltan > 0:
        n = min(por_reserva, faltan)
        db.crear_reserva(_datos(personas=n, telefono=f"{prefijo_tel}{i}"))
        faltan -= n
        i += 1


def test_disponibilidad_lista_slots(db):
    slots = db.verificar_disponibilidad(FUTURA, None, 2)
    assert len(slots) > 0
    assert all("hora" in s and "disponible" in s for s in slots)
    assert any(s["disponible"] for s in slots)


def test_disponibilidad_hora_especifica(db):
    slots = db.verificar_disponibilidad(FUTURA, "20:00", 2)
    slot = next(s for s in slots if s["hora"] == "20:00")
    assert slot["disponible"] is True


def test_disponibilidad_fuera_de_horario(db):
    slots = db.verificar_disponibilidad(FUTURA, "03:00", 2)
    slot = next(s for s in slots if s["hora"] == "03:00")
    assert slot["disponible"] is False
    assert slot["motivo"] == "fuera_de_horario"


def test_crear_reserva_valida(db):
    reserva_id = db.crear_reserva(_datos())
    assert reserva_id > 0
    reservas = db.obtener_reservas_por_fecha(FUTURA)
    assert any(r["id"] == reserva_id for r in reservas)


def test_rechazar_reserva_fuera_de_horario(db):
    with pytest.raises(ReservaFueraDeHorarioError):
        db.crear_reserva(_datos(hora="03:00", telefono="+593900000002"))


def test_rechazar_reserva_fecha_pasada(db):
    with pytest.raises(ReservaInvalidaError):
        db.crear_reserva(
            _datos(fecha=(date.today() - timedelta(days=1)).isoformat(),
                   telefono="+593900000003")
        )


def test_rechazar_reserva_capacidad_excedida(db):
    with pytest.raises(ReservaInvalidaError):
        db.crear_reserva(_datos(personas=999, telefono="+593900000004"))


def test_rechazar_reserva_sin_capacidad_en_slot(db):
    # Agotar la capacidad total del slot con varias reservas
    _agotar_slot(db, "+59390000005")
    with pytest.raises(ReservaNoDisponibleError):
        db.crear_reserva(_datos(telefono="+59390000006"))


def test_cancelar_reserva_libera_capacidad(db):
    _agotar_slot(db, "+59390000007")
    with pytest.raises(ReservaNoDisponibleError):
        db.crear_reserva(_datos(telefono="+59390000009"))

    reservas = db.obtener_reservas_por_fecha(FUTURA)
    assert len(reservas) >= 1
    assert db.cancelar_reserva(reservas[0]["id"], "test") is True

    # Tras cancelar, hay capacidad otra vez
    reserva_id = db.crear_reserva(_datos(telefono="+59390000008"))
    assert reserva_id > 0


def test_doble_reserva_mismo_cliente_mismo_slot(db):
    db.crear_reserva(_datos())
    with pytest.raises(ReservaDuplicadaError):
        db.crear_reserva(_datos())  # mismo telefono, fecha y hora


def test_doble_reserva_distintos_clientes_lo_une_capacidad(db):
    # Dos clientes distintos en el mismo slot con capacidad total
    _agotar_slot(db, "+59390000010")
    with pytest.raises(ReservaNoDisponibleError):
        db.crear_reserva(_datos(telefono="+59390000011"))


def test_reservas_concurrentes_no_exceden_capacidad(db):
    """Varios hilos creando reservas al mismo tiempo en el mismo slot."""
    import os

    errores = []
    creadas = []
    lock = threading.Lock()

    # Capacidad reducida: 6+6=12 > 10 -> solo una reserva debe entrar
    os.environ["RESTAURANT_TOTAL_CAPACITY"] = "10"
    try:
        db_local = RestaurantDB(db.database_url)
    finally:
        os.environ.pop("RESTAURANT_TOTAL_CAPACITY", None)

    def intentar_local(telefono):
        try:
            rid = db_local.crear_reserva(_datos(personas=6, telefono=telefono))
            with lock:
                creadas.append(rid)
        except ReservaNoDisponibleError:
            pass
        except Exception as e:  # pragma: no cover
            with lock:
                errores.append(e)

    hilos = [
        threading.Thread(target=intentar_local, args=(f"+5939000001{i}",))
        for i in range(4)
    ]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    assert not errores, f"Errores inesperados: {errores}"
    assert len(creadas) <= 1, (
        f"Se crearon {len(creadas)} reservas con capacidad para 1 "
        f"(doble reserva detectada)"
    )


def test_cliente_id_inventado_es_rechazado(db):
    with pytest.raises(ReservaInvalidaError):
        db.crear_reserva(_datos(cliente_id=999999, telefono="+593900000012"))


def test_reserva_resuelve_cliente_por_telefono(db):
    """Sin cliente_id, el sistema identifica/crea al cliente por telefono."""
    reserva_id = db.crear_reserva(_datos(telefono="+593900000099"))
    assert reserva_id > 0
    cliente = db.obtener_cliente_por_telefono("+593900000099")
    assert cliente is not None
    assert cliente["nombre"] == "Cliente Test"
