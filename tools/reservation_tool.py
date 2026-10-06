"""Herramientas de reservas para LangGraph."""

import logging

from langchain_core.tools import tool
from database.db_manager import ReservaError
from skills.reservations.reservation_skill import ReservationSkill

logger = logging.getLogger(__name__)

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
    try:
        disponibilidad = _reservation_skill.execute("verificar_disponibilidad", {
            "fecha": fecha,
            "hora": hora_preferida,
            "personas": personas
        })
    except (ReservaError, ValueError) as e:
        return f"No pude consultar la disponibilidad: {e}"
    except Exception:
        logger.exception("Error consultando disponibilidad fecha=%s", fecha)
        return "No pude consultar la disponibilidad en este momento."

    libres = [s for s in disponibilidad if s.get("disponible")]
    if not libres:
        return (f"No hay horarios disponibles para {personas} personas "
                f"el {fecha}.")

    respuesta = f"Para {personas} personas el {fecha} estan disponibles:\n\n"
    for slot in libres:
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
        Confirmacion de la reserva o motivo de rechazo
    """
    prefs = {}
    if preferencias:
        for pref in preferencias.split(","):
            prefs[pref.strip()] = True

    try:
        reserva_id = _reservation_skill.execute("crear_reserva", {
            "fecha": fecha,
            "hora": hora,
            "personas": personas,
            "nombre_contacto": nombre,
            "telefono": telefono,
            "preferencias": prefs
        })
    except ReservaError as e:
        return f"NO se creo la reserva: {e}"
    except Exception:
        logger.exception(
            "Error creando reserva fecha=%s hora=%s personas=%s",
            fecha, hora, personas,
        )
        return "No pude crear la reserva en este momento."

    return (f"Reserva #{reserva_id} confirmada para {personas} personas "
            f"el {fecha} a las {hora}. A nombre de {nombre}.")


@tool
def cancelar_reserva(reserva_id: int, motivo: str = None) -> str:
    """Cancela una reserva.

    Args:
        reserva_id: ID de la reserva
        motivo: Motivo de cancelacion

    Returns:
        Confirmacion de cancelacion
    """
    try:
        exito = _reservation_skill.execute("cancelar_reserva", {
            "reserva_id": reserva_id,
            "motivo": motivo
        })
    except Exception:
        logger.exception("Error cancelando reserva id=%s", reserva_id)
        return "No pude cancelar la reserva en este momento."

    if exito:
        return "Reserva cancelada correctamente."
    else:
        return "No pude cancelar la reserva. Verifica el ID."
