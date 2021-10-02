#Libreria para interfaz grafica
from tkinter import Tk, Button, filedialog, messagebox, Menu
from typing import Text
#Libreria creada
from PartesAnalizador import ErrorLexico, Token


#=================================================Variables globales=================================================
listaTokens = []
listaErrores = []

estadoError = False

#====================================Declarando función para abrir un archivo========================================
def abrirArchivo():
    Tk().withdraw()
    archivo = filedialog.askopenfile(
        title = "Seleccionar un archivo LFP",
        initialdir = "./",
        filetypes= (
            ("archivos LFP", "*.lfp"),
            ("todos los archivos", "*.*")
        )
    )
    if archivo is None:
        print('No se seleccionó ningun archivo\n')
        return None
    else:
        texto = archivo.read()
        archivo.close()
        print('Lectura exitosa\n')
        return texto

#====================================Funciones para el analisis del archivo==========================================
def isLetra(caracter):
    cter = ord(caracter)
    if(cter >= 65 and cter <= 90) or (cter >= 97 and cter <= 122) or (cter == 164) or (cter ==165):
        return True
    else:
        return False

def isNumero(caracter):
    cter = ord(caracter)
    if(cter >= 48 and cter <= 57):
        return True
    else:
        return False

def analizarArchivo(entrada):
    global listaTokens
    global listaErrores
    global estadoError

    listaTokens = []
    listaErrores = []
    estadoError = False
    estadoComilla = False
    fila = 1
    columna = 0 
    estado = 0
    lexActual = ""
    contComillaSimple = 0
    simbolos = ['=', '[', ']', ',', '{', '}', '(', ')', ';']
    reservadas = ['Claves', 'Registros', 'imprimir', 'imprimirln', 'conteo',
                'promedio', 'contarsi', 'datos', 'max', 'min', 'exportarReporte']
    cont = 0

    #For inicial para ver caracter por caracter
    for c in entrada: 
        cter = ord(c)
        if estado == 0:
            if c == "'" or estadoComilla == True:
                if c == "'":
                    contComillaSimple += 1
                    lexActual += c
                    if contComillaSimple == 3:
                        estadoComilla = False
                        contComillaSimple = 0
                        estado = 1
                else:
                    #Crear error
                    errorLexico = ErrorLexico(c,fila,(columna-(len(lexActual)-1)), "Sintax error: Se esperaba otra comilla simple")
                    listaErrores.append(errorLexico)
                    estadoError = True
                    lexActual = ""
                    estado = 0 
                    estadoComilla = False
                    contComillaSimple = 0
            elif c == "#":
                lexActual += c
                estado = 2
            elif c in simbolos:
                #Crear token de simbolos
                lexActual += c
                token = Token("Simbolo", lexActual, "Sim = (=, [,],’,’, {,}, (,),’;’)", fila, (columna-(len(lexActual)-1)))
                listaTokens.append(token)
                lexActual = ""
            elif c == '"':
                lexActual += c
                estado = 5
            elif isNumero(c):
                lexActual += c
                if isNumero(entrada[cont + 1]) or (ord(entrada[cont + 1]) == 46): # Si es un número o un punto.
                   estado = 7
                else:#crear token digito
                    token = Token("Digito", lexActual, "Digito = (-)?Di+(.Di+)?", fila, (columna-(len(lexActual)-1)))
                    listaTokens.append(token)
                    lexActual = ""                
            elif c == '-':
                lexActual += c
                if isNumero(entrada[cont + 1]) or (ord(entrada[cont + 1]) == 46):# Si es un número o un punto.
                    estado = 6
                else: #Si no viene un numero o un punto despues de un - es un error
                    #Crear error
                    errorLexico = ErrorLexico(c,fila,(columna-(len(lexActual)-1)), "Sintax error: Se esperaba un numero")
                    listaErrores.append(errorLexico)
                    estadoError = True
                    lexActual = ""
                    estado = 0 
            elif isLetra(c):
                lexActual += c
                if isLetra(entrada[cont + 1]):
                    estado = 3
                else:#verificar si el lexema actual pertenece a las palabras reservadas porque si el siguiente
                     # caracter no es una letra quiere decir que hasta el caracter actual llega el lexema.
                    if lexActual in reservadas:
                        #crear token
                        lexActual += c
                        token = Token("Simbolo", lexActual, "Le = [A_Z, a_z] -> Palabra = Le+", fila, (columna-(len(lexActual)-1)))
                        listaTokens.append(token)
                        lexActual = ""
                        estado = 0
                    else:
                        #crear error
                        errorLexico = ErrorLexico(c,fila,(columna-(len(lexActual)-1)), "Sintax error: caracter invalido")
                        listaErrores.append(errorLexico)
                        estadoError = True
                        lexActual = ""
                        estado = 0 
            else: # Si el caracter no cumple con ningun estado inicial
                #Crear error
                errorLexico = ErrorLexico(c,fila,(columna-(len(lexActual)-1)), "Sintax error: caracter invalido")
                listaErrores.append(errorLexico)
                estadoError = True
                lexActual = ""
                estado = 0 
        
        #Comentario multilinea
        elif estado == 1:
            lexActual += c
            if c == "'" or estadoComilla == True:
                if c == "'":
                    contComillaSimple += 1
                    if contComillaSimple == 3:
                        estadoComilla = False
                        contComillaSimple = 0
                        #crear token porque estas comillas son de cierre
                        lexActual += c
                        token = Token("Comentario multilinea", lexActual, "LeT = [A_Z, a_z, \.n, \.t, \.r, _] -> '''(LeT)*'''", fila, (columna-(len(lexActual)-1)))
                        listaTokens.append(token)
                        lexActual = ""
                        estado = 0
                else:
                    #Crear error
                    errorLexico = ErrorLexico(c,fila,(columna-(len(lexActual)-1)), "Sintax error: Se esperaba otra comilla simple")
                    listaErrores.append(errorLexico)
                    estadoError = True
                    lexActual = ""
                    estado = 0 
                    estadoComilla = False
                    contComillaSimple = 0
        
        #Comentario de una sola linea
        elif estado == 2:
            if cter != 10 and cter != 11:
                lexActual += c
            elif cter == 10:
                token = Token("Comentario de una sola línea", lexActual, "Let = [A_Z, a_z,\.t, _] -> #(Let)*(\.n)", fila, (columna-(len(lexActual)-1)))
                listaTokens.append(token)
                lexActual = ""
                estado = 0

        #Palabras reservadas
        elif estado == 3: 
            lexActual += c
            if isLetra(entrada[cont + 1]):
                pass
            else:#verificar si el lexema actual pertenece a las palabras reservadas porque si el siguiente
                    # caracter no es una letra quiere decir que hasta el caracter actual llega el lexema.
                if lexActual in reservadas:
                    #crear token - estado 4 aceptacion
                    token = Token("Palabra reservada", lexActual, "Le = [A_Z, a_z] -> Palabra = Le+", fila, (columna-(len(lexActual)-1)))
                    listaTokens.append(token)
                    lexActual = ""
                    estado = 0
                else:
                    #crear error
                    errorLexico = ErrorLexico(lexActual,fila,(columna-(len(lexActual)-1)), "Sintax error: palabra no reconocida")
                    listaErrores.append(errorLexico)
                    estadoError = True
                    lexActual = ""
                    estado = 0 
        
        #Cadenas
        elif estado == 5:
            lexActual += c
            if isLetra(c) or cter == 32 or cter == 9 or cter == 95:
                pass
            elif '"': #Crear token estado = 4 - aceptacion
                token = Token("Cadena", lexActual, "Le = [A_Z, a_z] -> Palabra = Le+", fila, (columna-(len(lexActual)-1)))
                listaTokens.append(token)
                lexActual = ""
                estado = 0
            else:#Crear error
                
                errorLexico = ErrorLexico(c,fila,(columna-(len(lexActual)-1)), "Sintax error: caracter invalido en la cadena")
                listaErrores.append(errorLexico)
                estadoError = True
                lexActual = ""
                estado = 0 
        
        #Digitos con menos
        elif estado == 6:   
            lexActual += c
            if isNumero(c):
                if isNumero(entrada[cont + 1]):
                    estado = 7
                else:#crear token digito
                    token = Token("Digito", lexActual, "Digito = (-)?Di+(.Di+)?", fila, (columna-(len(lexActual)-1)))
                    listaTokens.append(token)
                    lexActual = "" 
                    estado = 0
            else:#Crear error
                errorLexico = ErrorLexico(c,fila,(columna-(len(lexActual)-1)), "Sintax error: se esperaba un numero")
                listaErrores.append(errorLexico)
                estadoError = True
                lexActual = ""
                estado = 0 
        
        #Digito
        elif estado == 7:
            lexActual += c
            if isNumero(c):
                if isNumero(entrada[cont + 1]):
                    estado = 7
                else:#crear token digito
                    token = Token("Digito", lexActual, "Digito = (-)?Di+(.Di+)?", fila, (columna-(len(lexActual)-1)))
                    listaTokens.append(token)
                    lexActual = "" 
                    estado = 0
            else:#Crear error
                errorLexico = ErrorLexico(c,fila,(columna-(len(lexActual)-1)), "Sintax error: se esperaba un numero")
                listaErrores.append(errorLexico)
                estadoError = True
                lexActual = ""
                estado = 0

        #Control de espacios, saltos de línea y Tab's
        if cter == 10:
            columna = 0
            fila += 1
        elif cter == 9:
            columna += 4
        elif cter == 32:
            columna += 1

        columna += 1
            
            
class VentanaMenu:
    def __init__(self):
        self.txt = None
        self.ventana = Tk()
        self.ventana.title("Menu Principal")
        #Posicionar ventana en el centro
        self.ancho_ventana = 1300
        self.alto_ventana = 500

        self.x_ventana = self.ventana.winfo_screenwidth() // 2 - self.ancho_ventana // 2
        self.y_ventana = self.ventana.winfo_screenheight() // 2 - self.alto_ventana // 2

        self.posicion = str(self.ancho_ventana) + "x" + str(self.alto_ventana) + "+" + str(self.x_ventana) + "+" + str(self.y_ventana)
        self.ventana.geometry(self.posicion)

        self.ventana.configure(bg = 'sky blue')
        self.ventana.resizable(False, False)

        #Por medio de esto accedo a lo que sucede al dar click sobre la X para cerrar la ventana
        self.ventana.protocol("WM_DELETE_WINDOW", self.on_closing)

        #Se crea el menú de la ventana / el tearoff = 0 es para que no se me cree un submenú al darle click al "----" que me sale en los cascade
        self.miMenu = Menu(self.ventana, tearoff=0)
        self.ventana.configure(menu=self.miMenu)
        
        #Creando una sección/SubMenú esta es la barrita que aparecere arriba en la ventana
        self.menuPrincipal = Menu(self.miMenu)
        self.miMenu.add_command(label="Cargar Archivo", command=self.cargarArchivo)
        self.miMenu.add_command(label="Analizar", command=self.on_closing)




        self.ventana.mainloop()

    # Metodo para cerrar la ventana 
    def on_closing(self):
        if messagebox.askokcancel("Cerrar Programa", "Seguro que desea Salir?"):
            self.ventana.quit()

    def cargarArchivo(self):
        self.txt = None
        self.txt = abrirArchivo()
        if self.txt != None:
            self.txt += "~"
            print(self.txt)
        
    
