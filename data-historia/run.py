import sys
from usina_tandil_qa import UsinaTandilQA

def main():
    if len(sys.argv) < 2:
        print("Uso: python run.py 'tu pregunta aquí'")
        sys.exit(1)

    query = sys.argv[1]
    qa_system = UsinaTandilQA()
    response = qa_system.run_query(query)
    print(response)

if __name__ == "__main__":
    main()
