from semantic_router import Route, SemanticRouter

import os
from semantic_router.encoders import CohereEncoder, OpenAIEncoder

from fastapi import APIRouter

historia = Route(
    name="historia",
    utterances=[
        '¿Quién fue el fundador de la Usina y en qué año se estableció la empresa?',
        '¿Qué hitos importantes se mencionan en el libro La Usina 80 años que marcaron el crecimiento y evolución de la empresa?',
        "¿Cuál fue el rol de Juan Nigro en la creación y consolidación de la Usina Popular de Tandil?",
        "¿Cómo se describe la evolución de la Usina en relación al desarrollo local de Tandil a lo largo de las décadas?",
        "¿Qué desafíos históricos se resaltan en el relato y cómo se abordaron?",
    ],
)

# this could be used as an indicator to our chatbot to switch to a more
# conversational prompt
organigrama = Route(
    name="organigrama",
    utterances=[
        "¿Cuáles son los cargos principales y en qué áreas o secciones se ubican dentro del edificio?",
        "¿Cómo determina el sistema la ubicación de un empleado específico en el mapa del edificio?",
        "¿Qué datos personales se muestran al usuario y cuáles se omiten para garantizar la privacidad?",
    ],
)

tramites = Route(
    name="tramites",
    utterances=[
        "¿Cuáles son los pasos fundamentales para iniciar el trámite de baja de suministro?",
        "¿Qué documentación se requiere para realizar un cambio de titularidad y cuáles son las diferencias entre trámite residencial y no residencial?",
        "¿Cómo se orienta al usuario para adherirse al servicio de factura digital?",
        "¿Qué opciones y condiciones se ofrecen en el trámite de Conexión (habilitación de nuevo suministro)?",
        "¿Cuáles son los tiempos de aviso y las condiciones especiales para solicitar trámites como el cambio de titularidad o la baja de suministro?",
    ],
)

# we place both of our decisions together into single list
routes = [historia, organigrama, tramites]

class UsinaSemanticRouter:

    def get_route(self, query):
        encoder = OpenAIEncoder()
        semantic_router = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")
        return semantic_router(query).name
