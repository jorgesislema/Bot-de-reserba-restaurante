"""Herramientas de reservas para LangGraph."""

from langchain_core.tools import tool
from skills.reservations.reservation_skill import ReservationSkill


_reservation_skill = ReservationSkill()
_reservation_skill.initialize({})


@tool
def verificar_disponibilidad_reserva(fecha: str, personas: int, hora_preferida: str = None) -> str:
    """Verifica disponibilidad de mesas para una reserva.

    Args:
        fecha: Fecha de la reserva (YYYY-MM-DD)
        personas: Numero de personas
        hora_preferida: Hora preferida (HH:MM) - opcional

    Returns:
        Horarios disponibles
    """
    disponibilidad = _reservation_skill.execute("verificar_disponibilidad", {
        "fecha": fecha,
        "hora": hora_preferida,
        "personas": personas
    })

    if not disponibilidad:
        return "No tengo disponibilidad para esa fecha y hora."

    respuesta = f"Para {personas} personas el {fecha} tengo disponibilidad:\n\n"
    for slot in disponibilidad:
        respuesta += f"- {slot['hora']}\n"

    respuesta += "\nCual prefieres?"

    return respuesta


@tool
def crear_reserva(fecha: str, hora: str, personas: int, nombre: str, telefono: str, preferencias: str = None) -> str:
    """Crea una reserva en el restaurante.

    Args:
        fecha: Fecha de la reserva (YYYY-MM-DD)
        hora: Hora de la reserva (HH:MM)
        personas: Numero de personas
        nombre: Nombre del contacto
        telefono: Telefono de contacto
        preferencias: Preferencias (terraza, interior, privado)

    Returns:
        Confirmacion de la reserva
    """
    prefs = {}
    if preferencias:
        for pref in preferencias.split(","):
            prefs[pref.strip()] = True

    reserva_id = _reservation_skill.execute("crear_reserva", {
        "fecha": fecha,
        "hora": hora,
        "personas": personas,
        "nombre_contacto": nombre,
        "telefono": telefono,
        "preferencias": prefs
    })

    return f"Reserva confirmada para {personas} personas el {fecha} a las {hora}. A nombre de {nombre}."


@tool
def cancelar_reserva(reserva_id: int, motivo: str = None) -> str:
    """Cancela una reserva.

    Args:
        reserva_id: ID de la reserva
        motivo: Motivo de cancelacion

    Returns:
        Confirmacion de cancelacion
    """
    exito = _reservation_skill.execute("cancelar_reserva", {
        "reserva_id": reserva_id,
        "motivo": motivo
    })

    if exito:
        return "Reserva cancelada correctamente."
    else:
        return "No pude cancelar la reserva."
