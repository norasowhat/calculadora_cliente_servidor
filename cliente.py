import socket
import json
import threading
import os
import sys
import tkinter as tk
from tkinter import messagebox

HOST = '127.0.0.1'
PORT = 9090

ID_CLIENTE = sys.argv[1] if len(sys.argv) > 1 else "A"
FILE_CLIENTE = f"cliente{ID_CLIENTE}.json"

class Cliente:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Calculadora {ID_CLIENTE}")
        self.root.resizable(False, False)
        self.root.configure(bg="#FFEC8E")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((HOST, PORT))
            self.sock.sendall(json.dumps({"ident": "cliente"}).encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Error")

        self.texto_pantalla = tk.StringVar()
        self.pantalla = tk.Entry(
            root, 
            textvariable=self.texto_pantalla, 
            font=('Arial', 20), 
            bd=10, 
            bg="powder blue", 
            justify='right'
        )
        self.pantalla.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        btn_clear = tk.Button(
            root, text="Limpiar", width=23, height=1, font=('Arial', 10, 'bold'),
            bg="#FF8080", activebackground="#FF5050", command=self.limpiar_pantalla
        )
        btn_clear.grid(row=1, column=0, columnspan=4, padx=2, pady=2)

        botones = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]

        for fila_idx, fila in enumerate(botones):
            for col_idx, texto in enumerate(fila):
                btn = tk.Button(
                    root, 
                    text=texto, 
                    width=5, 
                    height=2, 
                    font=('Arial', 14),
                    command=lambda t=texto: self.presionar_boton(t)
                )
                btn.grid(row=fila_idx + 2, column=col_idx, padx=2, pady=2)
                btn.configure(bg="#C6C954", activebackground="#667436")

        lbl_hist = tk.Label(root, text="Resultados:", bg="#FFEC8E", font=('Arial', 10, 'bold'))
        lbl_hist.grid(row=6, column=0, columnspan=4, pady=(5, 0))

        self.txt_historial = tk.Text(root, height=8, width=32, font=('Consolas', 9))
        self.txt_historial.grid(row=7, column=0, columnspan=4, padx=5, pady=5)

        threading.Thread(target=self.escuchar_respuestas, daemon=True).start()

    def presionar_boton(self, valor):
        if valor == '=':
            self.enviar_operacion()
        else:
            texto_actual = self.texto_pantalla.get()
            self.texto_pantalla.set(texto_actual + str(valor))

    def limpiar_pantalla(self):
        self.texto_pantalla.set("")

    def enviar_operacion(self):
        expresion = self.texto_pantalla.get()

        operador_encontrado = None
        for op in ['+', '-', '*', '/']:
            if op in expresion:
                operador_encontrado = op
                break
        
        if not operador_encontrado:
            messagebox.showerror("La expresión debe tener un operador válido")
            return

        try:
            partes = expresion.split(operador_encontrado)
            num1 = float(partes[0])
            num2 = float(partes[1])
        except Exception:
            messagebox.showerror("La expresión está mal formulada")
            return

        diccionario_cliente = {
            "tipo": "peticion",
            "id_cliente": ID_CLIENTE,
            "num1": num1,
            "num2": num2,
            "op": operador_encontrado
        }

        self.guardar({"peticion": diccionario_cliente})

        try:
            mensaje_envio = json.dumps(diccionario_cliente) + "\n"
            self.sock.sendall(mensaje_envio.encode('utf-8'))
            self.texto_pantalla.set("")
        except Exception as e:
            messagebox.showerror("Error")

    def escuchar_respuestas(self):
        buffer = ""
        while True:
            try:
                datos = self.sock.recv(1024).decode('utf-8')
                if not datos:
                    break
                
                buffer += datos
               
                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    linea = linea.strip()
                    
                    if linea:
                        mensaje = json.loads(linea)
                        if mensaje.get("tipo") == "respuesta":
                            linea_texto = f"[Serv. {mensaje['id_servidor']}] {mensaje['expresion']} = {mensaje['resultado']}\n"

                            self.txt_historial.insert(tk.END, linea_texto)
                            self.txt_historial.see(tk.END)
                            self.guardar({"resultado": mensaje})
            except Exception:
                break

    def guardar(self, info_log):
        logs = []
        if os.path.exists(FILE_CLIENTE):
            with open(FILE_CLIENTE, 'r') as f:
                try:
                    logs = json.load(f)
                except Exception:
                    logs = []
        logs.append(info_log)
        with open(FILE_CLIENTE, 'w') as f:
            json.dump(logs, f, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = Cliente(root)
    root.mainloop()