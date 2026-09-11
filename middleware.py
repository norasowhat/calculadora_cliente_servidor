import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 9090

clientes = []
servidores = []
lock = threading.Lock()

def conexion(conn, addr):
    try:
        datosIdentificador = conn.recv(1024).decode('utf-8')
        if not datosIdentificador:
            return
        dato_guardado = json.loads(datosIdentificador)
        emisor = dato_guardado.get("ident")

        with lock:
            if emisor == "cliente":
                clientes.append(conn)
                print(f"Cliente conectado {addr}")
            elif emisor == "servidor":
                servidores.append(conn)
                print(f"Servidor conectado {addr}")
            else:
                conn.close()
                return

        while True:
            peticion = conn.recv(1024).decode('utf-8')
            if not peticion:
                break

            info = json.loads(peticion)
            tipo_peticion = info.get("tipo")

            if tipo_peticion == "peticion":
                print(f"Operación viaja a: {len(servidores)} servidores...")
                with lock:
                    for s in list(servidores):
                        try:
                            s.sendall(peticion.encode('utf-8'))
                        except:
                            servidores.remove(s)

            elif tipo_peticion == "respuesta":
                print(f"Resultado viaja a: {len(clientes)} clientes...")
                with lock:
                    for c in list(clientes):
                        try:
                            c.sendall(peticion.encode('utf-8'))
                        except:
                            clientes.remove(c)

    except Exception as e:
        print(f"Error en {addr}: {e}")
    finally:
        with lock:
            if conn in clientes: clientes.remove(conn)
            if conn in servidores: servidores.remove(conn)
        conn.close()

def main():
    socket_middleware = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_middleware.bind((HOST, PORT))
    socket_middleware.listen()
    print(f"Middleware activo en {HOST}:{PORT}")

    while True:
        conn, addr = socket_middleware.accept()
        threading.Thread(target=conexion, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()

    