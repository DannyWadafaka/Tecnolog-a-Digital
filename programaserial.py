import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports

"""
==============================================================================
 MONITOR SERIAL ESP32 - GUI
==============================================================================

LÓGICA DEL PROGRAMA
--------------------
1. El usuario elige el puerto COM y el baudrate, y presiona "Conectar".
2. El programa abre una conexión serial hacia el ESP32 (igual que el
   Monitor Serial del IDE de Arduino, pero con nuestra propia ventana).
3. Cada 100 milisegundos, el programa se pregunta a sí mismo: "¿llegaron
   datos nuevos por el puerto?". Si llegaron, los lee y los muestra en la
   consola de la ventana. Si no llegaron, no hace nada y vuelve a preguntar
   100ms después.
4. Ese "preguntar cada 100ms" se hace con root.after(), una función propia
   de tkinter que reemplaza a un bucle while(true) tradicional, permitiendo
   que la ventana siga respondiendo a clics mientras tanto (no se congela).

PLATAFORMA / LENGUAJE
------------------------
- Lenguaje: Python 3 (recomendado 3.10 o superior).
- Librería gráfica: tkinter (incluida en Python, no se instala aparte).
- Librería de comunicación serial: pyserial (se instala con pip).
- Sistema operativo de destino: Windows (para generar el .exe final),
  aunque el mismo script .py corre igual en Windows, Linux o Mac.

AMBIENTE INTEGRADO (IDE) UTILIZADO
--------------------------------------
Se puede escribir y probar este código en cualquier editor con soporte para
Python, por ejemplo: Visual Studio Code (con la extensión de Python),
PyCharm, o incluso el IDLE que trae Python instalado por defecto.
No se necesita un IDE especial: cualquiera que permita correr
"python nombre_archivo.py" desde una terminal es suficiente.

COMPILADOR / INTÉRPRETE
---------------------------
Python NO se compila a lenguaje máquina como C++ (que usa un compilador
como g++ o MSVC). Python es un lenguaje INTERPRETADO: el intérprete oficial
de Python (CPython, que se descarga desde python.org) lee el archivo .py
línea por línea y lo va ejecutando directamente, sin generar un binario
previo. Por eso no existe un "compilador de Python" propiamente dicho.

CÓMO SE CONVIERTE A .EXE
----------------------------
Como Python no genera un ejecutable por sí solo, se usa una herramienta
externa llamada PyInstaller, que EMPAQUETA el script, el intérprete de
Python y todas las librerías necesarias (tkinter, pyserial) dentro de un
único archivo .exe que ya puede correr en cualquier PC con Windows, sin
necesidad de tener Python instalado.

    1) pip install pyinstaller
    2) pyinstaller --onefile --windowed --name MonitorESP32 monitor_simple.py
    3) El ejecutable final queda en la carpeta "dist" -> dist/MonitorESP32.exe

    --onefile   -> junta todo en un solo archivo .exe
    --windowed  -> no abre una consola negra de fondo (la app ya tiene su
                   propia ventana gráfica)

Requisitos para correr el script en modo desarrollo (antes de compilar):
    pip install pyserial
"""

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Serial ESP32")
        self.root.geometry("700x450")
        self.ser = None

        top = ttk.Frame(root, padding=8)
        top.pack(fill=tk.X)

        self.puerto_combo = ttk.Combobox(top, width=12, state="readonly")
        self.puerto_combo.pack(side=tk.LEFT, padx=4)

        # se setea el puerto
        self.puerto_combo["values"] = [p.device for p in serial.tools.list_ports.comports()]

        if self.puerto_combo["values"]:
            self.puerto_combo.current(0)

        # baudrate para enviar los pulsos por s
        self.baud_combo = ttk.Combobox(top, width=8, state="readonly", values=["9600", "115200"])
        self.baud_combo.set("115200")
        self.baud_combo.pack(side=tk.LEFT, padx=4)

        self.boton_conectar = ttk.Button(top, text="Conectar", command=self.conectar)
        self.boton_conectar.pack(side=tk.LEFT, padx=4)

        ttk.Button(top, text="Limpiar", command=self.limpiar).pack(side=tk.RIGHT, padx=4)

        self.consola = tk.Text(root, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10))
        self.consola.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.root.after(100, self.revisar_puerto)

    def conectar(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None
            self.boton_conectar.config(text="Conectar")
            self.consola.insert(tk.END, "--- Desconectado ---\n")
            return

        puerto = self.puerto_combo.get()
        baud = int(self.baud_combo.get())
        try:
            self.ser = serial.Serial(puerto, baud, timeout=0)
            self.boton_conectar.config(text="Desconectar")
            self.consola.insert(tk.END, f"--- Conectado a {puerto} ---\n")
        except serial.SerialException as e:
            messagebox.showerror("Error", str(e))

    def revisar_puerto(self):
        if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
            datos = self.ser.read(self.ser.in_waiting)
            self.consola.insert(tk.END, datos.decode("utf-8", errors="replace"))
            self.consola.see(tk.END)
        self.root.after(100, self.revisar_puerto)

    def limpiar(self):
        self.consola.delete("1.0", tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()