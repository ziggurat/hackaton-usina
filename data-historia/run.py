import sys
from usina_tandil_qa import UsinaTandilQA

def main():
    query = input("Preguntá algo acerca de la historia de la Usina:")
    qa_system = UsinaTandilQA()
    response = qa_system.run_query(query)
    print(response)

if __name__ == "__main__":
    main()
