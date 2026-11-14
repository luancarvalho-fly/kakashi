# -*- coding: utf-8 -*-
"""Qual VISUAL o Kakashi usa (14/11/2026). Padrão = 8 BITS (visual8.py: ele, 14/11, «bota aquela [UI] 8-bits original do jeito que
tava» → «Barra 3.0 em 8 bits»). config.json "visual": "grafite" volta pro liso de 12/11 (visual.py). Os dois têm a mesma interface."""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))


def nome():
    try:
        with open(os.path.join(AQUI, "config.json"), encoding="utf-8") as f:
            v = str(json.load(f).get("visual", "8bits")).lower()
    except (OSError, ValueError):
        v = "8bits"
    return "grafite" if v == "grafite" else "8bits"


def modulo():
    if nome() == "grafite":
        import visual as m
    else:
        import visual8 as m
    return m
