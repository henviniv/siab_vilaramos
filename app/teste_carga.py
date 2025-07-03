import requests
import threading
import time

# Altere para sua URL real
URL = "https://siab-vilaramos.onrender.com/"

NUM_USUARIOS = 30
resultados = []

def simular_usuario(id_usuario):
    inicio = time.time()
    try:
        resposta = requests.get(URL)
        duracao = time.time() - inicio
        print(f"Usuário {id_usuario:02d}: {resposta.status_code} em {duracao:.2f}s")
        resultados.append(duracao)
    except Exception as e:
        print(f"Usuário {id_usuario:02d}: erro - {e}")
        resultados.append(None)

def main():
    threads = []
    inicio_total = time.time()

    for i in range(NUM_USUARIOS):
        t = threading.Thread(target=simular_usuario, args=(i+1,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    fim_total = time.time()
    print("\n--- Estatísticas ---")
    tempos_validos = [t for t in resultados if t is not None]
    if tempos_validos:
        print(f"Tempo médio: {sum(tempos_validos)/len(tempos_validos):.2f}s")
        print(f"Tempo total: {fim_total - inicio_total:.2f}s")
    else:
        print("Nenhuma requisição foi bem-sucedida.")

if __name__ == "__main__":
    main()
