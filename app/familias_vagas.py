import re

def obter_numero_micro(aba):
    
    if not aba:
        return None

    numeros = re.findall(r'\d+', aba)
    return int(numeros[0]) if numeros else None


def obter_prefixo_por_micro(micro_numero):
    
    return 3495 + ((micro_numero - 1) // 6 + 1)


def gerar_familias_micro(micro_numero, inicio=1, fim=220):
    prefixo_base = obter_prefixo_por_micro(micro_numero)
    prefixo = f"{prefixo_base}-{micro_numero:02d}-"

    return [f"{prefixo}{str(i).zfill(3)}" for i in range(inicio, fim + 1)]


def encontrar_familias_vagas(lista_familias_planilha, micro_numero):
    todas = set(gerar_familias_micro(micro_numero))
    ocupadas = set(lista_familias_planilha)

    return sorted(list(todas - ocupadas))