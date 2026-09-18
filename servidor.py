import socket
import json
import os
import sys

HOST = '127.0.0.1'
PORT = 9090

ID_SERVIDOR = sys.argv[1] if len(sys.argv) > 1 else "1"
SERVIDOR_FILE = f"servidor{ID_SERVIDOR}.json"

def guardar(info_log):
    logs = []
    if os.path.exists(SERVIDOR_FILE):
        with open(SERVIDOR_FILE, 'r') as f:
            try: logs = json.load(f)
            except: logs = []
    logs.append(info_log)
    with open(SERVIDOR_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

def calcular_operacion(op, num1, num2):
    if op == '+': return num1 + num2
    if op == '-': return num1 - num2
    if op == '*': return num1 * num2
    if op == '/': return num1 / num2 if num2 != 0 else "indeterminado"
    return "Operación no válida"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.sendall(json.dumps({"ident": "servidor"}).encode('utf-8'))
    print(f"{ID_SERVIDOR} arriba")

    buffer = ""
    while True:
        operacion = sock.recv(1024).decode('utf-8')
        if not operacion:
            break
        
        buffer += operacion
        while "\n" in buffer:
            linea, buffer = buffer.split("\n", 1)
            linea = linea.strip()
            if not linea:
                continue

            peticion_op = json.loads(linea)
            if peticion_op.get("tipo") == "peticion":
                op = peticion_op.get("op")
                n1 = float(peticion_op.get("num1"))
                n2 = float(peticion_op.get("num2"))
                
                res = calcular_operacion(op, n1, n2)
                
                respuesta = {
                    "tipo": "respuesta",
                    "id_servidor": ID_SERVIDOR,
                    "origen": peticion_op.get("id_cliente"),
                    "expresion": f"{n1} {op} {n2}",
                    "resultado": res
                }

                guardar(respuesta)
                sock.sendall((json.dumps(respuesta) + "\n").encode('utf-8'))

if __name__ == "__main__":
    main()