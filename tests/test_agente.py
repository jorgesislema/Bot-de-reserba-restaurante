"""Tests del gate de confirmacion y clasificacion de tools (FASE E)."""

import os

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from api.agent import (
    TOOLS_CRITICAS,
    TOOL_TIPOS,
    es_confirmacion,
    validar_confirmacion,
)


def _state_con_tool_calls(nombre, args, confirmado=None):
    messages = []
    if confirmado is not None:
        messages.append(HumanMessage(content=confirmado))
    messages.append(
        AIMessage(
            content="",
            tool_calls=[{
                "name": nombre,
                "args": args,
                "id": "call_1",
                "type": "tool_call",
            }],
        )
    )
    return {"messages": messages}


class TestEsConfirmacion:
    @pytest.mark.parametrize("texto", [
        "si", "Si", "SI", "sí", "confirmo", "claro", "dale", "ok", "adelante",
    ])
    def test_confirmaciones_positivas(self, texto):
        assert es_confirmacion(texto) is True

    @pytest.mark.parametrize("texto", [
        "no", "cancela", "otra hora", "quiero algo mas", "",
    ])
    def test_no_es_confirmacion(self, texto):
        assert es_confirmacion(texto) is False


class TestGateConfirmacion:
    def test_bloquea_crear_reserva_sin_confirmacion(self):
        state = _state_con_tool_calls(
            "crear_reserva", {"fecha": "2026-10-10", "hora": "20:00", "personas": 4}
        )
        result = validar_confirmacion(state)

        assert result["pendiente_confirmacion"]["name"] == "crear_reserva"
        messages = result["messages"]
        # AIMessage sin tool_calls + ToolMessage de bloqueo
        assert messages[0].tool_calls == []
        assert isinstance(messages[1], ToolMessage)
        assert messages[1].content.startswith("OPERACION_BLOQUEADA")
        # ToolNode nunca debe ver el tool_call original
        assert not getattr(messages[-1], "tool_calls", None)

    def test_aprueba_si_usuario_confirmo_y_args_coinciden(self):
        args = {"fecha": "2026-10-10", "hora": "20:00", "personas": 4}
        state = _state_con_tool_calls("crear_reserva", args, confirmado="si, confirmo")
        state["pendiente_confirmacion"] = {
            "name": "crear_reserva",
            "args": '{"fecha": "2026-10-10", "hora": "20:00", "personas": 4}',
        }
        result = validar_confirmacion(state)

        # Se deja pasar: sin mensajes bloqueados, pendiente consumido
        assert "messages" not in result
        assert result["pendiente_confirmacion"] is None

    def test_rechaza_si_args_distintos_a_los_pendientes(self):
        state = _state_con_tool_calls(
            "crear_reserva", {"fecha": "2026-10-11", "hora": "21:00", "personas": 2},
            confirmado="si",
        )
        state["pendiente_confirmacion"] = {
            "name": "crear_reserva",
            "args": '{"fecha": "2026-10-10", "hora": "20:00", "personas": 4}',
        }
        result = validar_confirmacion(state)

        assert "messages" in result  # bloqueado
        assert result["pendiente_confirmacion"]["name"] == "crear_reserva"

    def test_rechaza_si_usuario_no_confirmo_aunque_haya_pendiente(self):
        state = _state_con_tool_calls(
            "crear_reserva", {"fecha": "2026-10-10", "hora": "20:00", "personas": 4},
            confirmado="hola buenas",
        )
        state["pendiente_confirmacion"] = {
            "name": "crear_reserva",
            "args": '{"fecha": "2026-10-10", "hora": "20:00", "personas": 4}',
        }
        result = validar_confirmacion(state)
        assert "messages" in result  # bloqueado de nuevo

    def test_tools_no_criticas_pasan_directo(self):
        state = _state_con_tool_calls("buscar_producto", {"nombre": "pizza"})
        assert validar_confirmacion(state) == {}

    def test_descarta_pendiente_cuando_usuario_no_confirma(self):
        messages = [
            HumanMessage(content="quiero otra cosa"),
            AIMessage(content="te ayudo"),
        ]
        result = validar_confirmacion({
            "messages": messages,
            "pendiente_confirmacion": {"name": "crear_reserva", "args": "{}"},
        })
        assert result["pendiente_confirmacion"] is None

    @pytest.mark.parametrize("nombre", [
        "crear_reserva", "cancelar_reserva", "confirmar_pedido",
        "cancelar_pedido", "crear_envio_delivery",
        "enviar_mensaje_whatsapp", "enviar_mensaje_telegram",
    ])
    def test_toda_tool_critica_esta_en_el_gate(self, nombre):
        assert nombre in TOOLS_CRITICAS
        state = _state_con_tool_calls(nombre, {"x": 1})
        assert "messages" in validar_confirmacion(state)


class TestClasificacionTools:
    def test_todas_las_tools_estan_clasificadas(self):
        from tools import ALL_TOOL_NAMES
        sin_clasificar = set(ALL_TOOL_NAMES) - set(TOOL_TIPOS)
        assert not sin_clasificar

    def test_reads_no_son_criticas(self):
        reads = {n for n, t in TOOL_TIPOS.items() if t == "READ"}
        assert not reads & set(TOOLS_CRITICAS)


class TestCanales:
    def test_telegram_no_configurado_no_simula_exito(self, monkeypatch):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        from skills.channels.channel_skill import ChannelSkill
        skill = ChannelSkill()
        skill.initialize({})
        resultado = skill.execute("enviar_respuesta", {
            "channel": "telegram", "to": "123", "message": "hola",
        })
        assert resultado["success"] is False
        assert resultado["error"] == "channel_not_configured"

    def test_whatsapp_no_configurado_no_simula_exito(self, monkeypatch):
        monkeypatch.delenv("WHATSAPP_TOKEN", raising=False)
        monkeypatch.delenv("WHATSAPP_PHONE_ID", raising=False)
        from skills.channels.channel_skill import ChannelSkill
        skill = ChannelSkill()
        skill.initialize({})
        resultado = skill.execute("enviar_respuesta", {
            "channel": "whatsapp", "to": "+593999999999", "message": "hola",
        })
        assert resultado["success"] is False
        assert resultado["error"] == "channel_not_configured"

    def test_parametros_faltantes(self):
        from skills.channels.channel_skill import ChannelSkill
        skill = ChannelSkill()
        skill.initialize({})
        resultado = skill.execute("enviar_respuesta", {"channel": "whatsapp"})
        assert resultado == {"success": False, "data": None, "error": "missing_parameters"}
