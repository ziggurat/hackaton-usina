from historia import UsinaTandilQA
from organigrama import QueryProcessor
from tramites import ConsultorTramites

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Example usage
    usina = UsinaTandilQA()
    query_processor = QueryProcessor()
    consultor_tramites = ConsultorTramites()
