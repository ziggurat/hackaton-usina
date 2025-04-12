from semantic_router import Route, SemanticRouter
from semantic_router.encoders import OpenAIEncoder

import sys
sys.path.append("data-tramites")
sys.path.append("data-organigrama")
sys.path.append("data-historia")

import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path('.') / 'usina.env'
result = load_dotenv(dotenv_path=ENV_PATH.resolve(), override=True)
# print("Reading OPENAI config:", ENV_PATH.resolve(), result)
os.environ["OPENAI_MODEL_NAME"] =  os.getenv('LLM_MODEL') # 'gpt-4o-mini'
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["EMBEDDINGS_MODEL"] = os.getenv("EMBEDDINGS_MODEL")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRAMITES_DB"] = os.getenv("TRAMITES_DB")
os.environ["HISTORIA_DB"] = os.getenv("HISTORIA_DB")
os.environ["ORGANIGRAMA_DB"] = os.getenv("ORGANIGRAMA_DB")
print(os.environ["OPENAI_MODEL_NAME"])
# print(os.environ["EMBEDDINGS_MODEL"])
print(os.environ["TRAMITES_DB"])
print(os.environ["ORGANIGRAMA_DB"])
print(os.environ["HISTORIA_DB"])

from tramite import ConsultorTramites
from query_processor import QueryProcessor
from usina_tandil_qa import UsinaTandilQA

class UsinaSemanticRouter:

    historia = Route(
        name="historia",
        utterances=[
            '¿Quién fue el fundador de la Usina y en qué año se estableció la empresa?',
            '¿Qué hitos importantes se mencionan en el libro La Usina 80 años que marcaron el crecimiento y evolución de la empresa?',
            "¿Cuál fue el rol de Juan Nigro en la creación y consolidación de la Usina Popular de Tandil?",
            "¿Cómo se describe la evolución de la Usina en relación al desarrollo local de Tandil a lo largo de las décadas?",
            "¿Qué desafíos históricos se resaltan en el relato y cómo se abordaron?",
            "¿Quien fue el primer empleado de la Usina?",
            "¿Quien fue el primer presidente de la Usina?",
            "¿Quien era el presidente de la Usina en 1995"
        ],
    )

    organigrama = Route(
        name="organigrama",
        utterances=[
            "¿Cuáles son los cargos principales y en qué áreas o secciones se ubican dentro del edificio?",
            "¿Cómo determina el sistema la ubicación de un empleado específico en el mapa del edificio?",
            "¿Qué datos personales se muestran al usuario y cuáles se omiten para garantizar la privacidad?",
            "¿Quien es el presidente actual de la Usina?"
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

    def __init__(self):

        self.backends = {
            'tramites': ConsultorTramites(),
            'organigrama': QueryProcessor(),
            'historia': UsinaTandilQA(),
        }

        self.encoder = OpenAIEncoder(openai_api_key=os.getenv("OPENAI_API_KEY"))

        # we place both of our decisions together into single list
        self.routes = [UsinaSemanticRouter.historia, UsinaSemanticRouter.organigrama, UsinaSemanticRouter.tramites]
        self.semantic_router = SemanticRouter(encoder=self.encoder, routes=self.routes, auto_sync="local")

    def get_route(self, query):
        # encoder = OpenAIEncoder()
        # semantic_router = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")
        route =  self.semantic_router(query)
        return route.name if route is not None else None
    
    def get_answer(self, query):
        route = self.get_route(query)
        target_backend = None

        if route is not None:
            target_backend = self.backends[route]
        print("Redirecting to backend:", route, target_backend)
        if target_backend is None:
            return "Lo siento, no tengo información sobre ese tema."

        return target_backend.consultar(query)
    

# Ejemplo de uso
if __name__ == "__main__":
    semantic_router = UsinaSemanticRouter()
    
    while True:
        pregunta = input("Ingresa tu pregunta sobre trámites (o 'salir' para terminar): ")
        if pregunta.lower() == 'salir':
            break
            
        respuesta = semantic_router.get_answer(pregunta)
        print()
        print(respuesta)
        print("\n\n")
        

        
