#Libreria para interfaz grafica
from tkinter import Label, Tk, Button, filedialog, messagebox, Menu, scrolledtext
import tkinter
from tkinter.constants import COMMAND, TRUE
from typing import Text
#Libreria creada
from PartesAnalizador import ErrorLexico, Token, ErrorSintactico
#Libreria para abrir directamente los reportes
import webbrowser


#=================================================Variables globales=================================================
listaTokens = []
listaErrores = []
datos = []
lista_Claves = []
lista_Registros = []
estadoError = False
reservadasDeclaracion = ["Palabra reservada Claves", "Palabra reservada Registros"]
reservadasFuncion = ["Palabra reservada imprimir", "Palabra reservada imprimirln", "Palabra reservada conteo", 
                    "Palabra reservada promedio", "Palabra reservada contarsi", "Palabra reservada datos",
                    "Palabra reservada max", "Palabra reservada min", "Palabra reservada exportarReporte"]
simbolos = []
tk = Token()
contImprimirln = 0 #Contador para completar la funcionalidad de imprimirln

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
        messagebox.showwarning('ADVERTENCIA', 'No se seleccionó ningun archivo.')
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

def analisisLexico(entrada):
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

        if c == "~": #Si ya se termino el archivo
            #Crear token de simbolos
                lexActual += c
                token = Token("Fin", lexActual, "~", fila, (columna-(len(lexActual)-1)))
                listaTokens.append(token)
                lexActual = ""

        elif estado == 0:
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
                token = Token(f"Simbolo {lexActual}", lexActual, "Sim = (=, [,],’,’, {,}, (,),’;’)", fila, (columna-(len(lexActual)-1)))
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
                # Espacio - Salto de línea - TAB
                if cter == 32 or cter == 10 or cter == 9:
                    lexActual = ""
                    estado = 0
                else:
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
                        # Se reconoce el comentario multilinea pero se obvia en los la lista de tokens.
                        # token = Token("Comentario multilinea", lexActual, "LeT = [A_Z, a_z, \.n, \.t, \.r, _] -> '''(LeT)*'''", fila, (columna-(len(lexActual)-1)))
                        #listaTokens.append(token)
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
                # Se reconoce el comentario de una sola línea pero se obvia en los la lista de tokens.
                #token = Token("Comentario de una sola línea", lexActual, "Let = [A_Z, a_z,\.t, _] -> #(Let)*(\.n)", fila, (columna-(len(lexActual)-1)))
                #listaTokens.append(token)
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
                    token = Token(f"Palabra reservada {lexActual}", lexActual, "Le = [A_Z, a_z] -> Palabra = Le+", fila, (columna-(len(lexActual)-1)))
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
            if isNumero(c) or cter == 46: #Si el caracter es un numero o un punto
                if cter == 46:#Si el caracter es un punto
                    estado = 8
                elif isNumero(entrada[cont + 1]) or (ord(entrada[cont + 1]) == 46):#Si el siguiente es un numero y no hay un punto
                    pass
                else:#crear token digito si el siguiente caracter no es un numero entonces hay que aceptar
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

        #Digito despues del punto
        elif estado == 8:
            lexActual += c
            if isNumero(c):
                if isNumero(entrada[cont + 1]):
                    pass
                else: #Creamos token aceptacion estado 9
                    token = Token("Digito", lexActual, "Digito = (-)?Di+(.Di+)?", fila, (columna-(len(lexActual)-1)))
                    listaTokens.append(token)
                    lexActual = "" 
                    estado = 0
            else: # Si no es un numero despues del punto es un error
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

        cont += 1
        columna += 1
                
def generarErrorSintactico(mensaje):
    global estadoError
    global listaTokens
    global tk
    global listaErrores
    errorSintactico = ErrorSintactico(tk.token,tk.fila,tk.columna, f"{mensaje}")
    listaErrores.append(errorSintactico)
    estadoError = True
    if tk.token != "Fin":
        listaTokens.pop(0)
        tk = listaTokens[0]

def exportarReporte(entrada):
    global datos
    if(entrada != None):
        #abrir o crear el reporte
        f = open('Reporte_Exportado_Datos.html','w', encoding='utf-8')
        #Cuerpo del documento
        cuerpo = '''<!doctype html>
        <html lang="en">

        <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
            integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

        <title>Reporte de datos</title>
        </head>

        <body style="background-color: lightseagreen;">
        <div class="container-fluid container p-3 my-3 bg-dark text-white">
            <div class="row">
            <div class="col-12" style="text-align: center; ">
                <h1>REPORTE DE DATOS</h1>
            </div>
            </div>
        </div>
        <div class="container-fluid" style="background-color: rgb(255, 255, 255); ">
            
            <div class="row justify-content-md-center">
            <div class="col-md-auto">
                <h2 style="text-decoration: underline tomato;">''' 
        cuerpo += f'''{entrada}'''
        cuerpo += '''</h2>
            </div>
            </div>
            <div class="row justify-content-md-center">
            <div class="col-md-auto">
                <table class="table table-bordered table-striped text-center table-hover table-responsive"
                style="text-align: center; width: 600px;">
                <thead>
                    <tr class="table-dark">'''
        for item in datos[0]:
            cuerpo += f'''<th>{item}</th>'''
        cuerpo += '''</tr>
                </thead>
                <tbody>
                '''  
        fila = 1
        columna = 0
        while(fila < (len(datos))):
            cuerpo += "<tr>"
            while(columna < len(datos[fila])):
                cuerpo += f'''
                        <td class="table-success">{datos[fila][columna]}</td>
                        '''
                columna += 1
            columna = 0
            fila += 1
            cuerpo += "</tr>"

        cuerpo += '''
            </tbody>
            </table>
            </div>
            </div>
            <div class="container-fluid container p-3 my-3 bg-dark text-white">
            <div class="row">
            <div class="col-12" style="text-align: center; ">
                <h1></h1>
            </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
            crossorigin="anonymous"></script>
        </body>

        </html>'''

        f.write(cuerpo)
        f.close
        #Aquí se hace la magia de abrirlo automaticamente
        webbrowser.open_new_tab('Reporte_Exportado_Datos.html')
    else:
        print("No se ha cargado ningun archivo")
        messagebox.showwarning('ADVERTENCIA', 'Intente de nuevo.')

def analisisSintactico(self):
    global reservadasDeclaracion
    global reservadasFuncion
    global simbolos
    global estadoError
    global tk
    global datos
    global lista_Registros
    global lista_Claves

    datos = []
    lista_Claves = []
    lista_Registros = []
    tk = listaTokens[0]
    #Se borra todo lo que tuviese la consola
    self.text_Area2.configure(state = 'normal')
    self.text_Area2.delete("1.0", "end")
    self.text_Area2.configure(state = 'disable')

    def inicio():
        instrucciones()
        print("analisis sintactico completado")


    def instrucciones():
        if tk.token == "Fin":
            return
        else:
            instruccion()
            instrucciones()


    def instruccion():
        global estadoError
        if tk.token in reservadasDeclaracion:
            declaracion()
        elif tk.token in reservadasFuncion:
            funcion()
        else:
            #Crear error y agregarlo a la lista
            generarErrorSintactico("Syntactic error: se esperaba una palabra reservada.")


    def declaracion():
        global tk
        if tk.token == "Palabra reservada Claves": #entramos a palabra reservada claves
            listaTokens.pop(0)
            tk = listaTokens[0]
            declaracionTipo1()
        else: #Palabra reservada Registro
            listaTokens.pop(0)
            tk = listaTokens[0]
            declaracionTipo2()
    
    
    def funcion():
        #["Palabra reservada imprimir", "Palabra reservada imprimirln", "Palabra reservada conteo", 
                    #"Palabra reservada promedio", "Palabra reservada contarsi", "Palabra reservada datos",
                    #"Palabra reservada max", "Palabra reservada min", "Palabra reservada exportarReporte"]
        global tk
        comando = tk.lexema
        if tk.token == "Palabra reservada imprimir" or tk.token == "Palabra reservada imprimirln" or tk.token == "Palabra reservada promedio" or tk.token == "Palabra reservada max" or tk.token == "Palabra reservada min" or tk.token == "Palabra reservada exportarReporte":
            listaTokens.pop(0)
            tk = listaTokens[0]
            funcion_Tipo1(comando)
        elif tk.token == "Palabra reservada conteo" or tk.token == "Palabra reservada datos":
            listaTokens.pop(0)
            tk = listaTokens[0]
            funcion_Tipo2(comando)
        else:
            listaTokens.pop(0)
            tk = listaTokens[0]
            funcion_Tipo3(comando)


    def funcion_Tipo1(comando):
        global estadoError
        global tk
        global datos
        global contImprimirln
        cadenaEntrada = ""
        if tk.token == "Simbolo (":
            listaTokens.pop(0)
            tk = listaTokens[0]
            if tk.token == "Cadena":
                cadenaEntrada = tk.lexema #Guardamos el valor que viene en el token Cadena
                listaTokens.pop(0)
                tk = listaTokens[0]
                if tk.token == "Simbolo )":
                    listaTokens.pop(0)
                    tk = listaTokens[0]
                    if tk.token == "Simbolo ;": #Estado de aceptacion de la entrada
                        listaTokens.pop(0)  
                        tk = listaTokens[0]
                        #Una vez aceptado el comando podemos trabajar las funcionalidades de cada comando dependiendo del que venga
                        if estadoError != True:
                            if comando == "imprimir":
                                self.text_Area2.configure(state = 'normal')
                                self.text_Area2.insert("end", f"{cadenaEntrada}")
                                self.text_Area2.configure(state = 'disable')
                                contImprimirln = 0
                            elif comando == "imprimirln":
                                if contImprimirln == 0:
                                    self.text_Area2.configure(state = 'normal')
                                    self.text_Area2.insert("end", f"\n{cadenaEntrada}")
                                    self.text_Area2.configure(state = 'disable')
                                    contImprimirln = 1
                                else:
                                    self.text_Area2.configure(state = 'normal')
                                    self.text_Area2.insert("end", f"{cadenaEntrada}")
                                    self.text_Area2.configure(state = 'disable')
                                    self.text_Area2.configure(state = 'normal')
                                    self.text_Area2.insert("end", f"\n{cadenaEntrada}")
                                    self.text_Area2.configure(state = 'disable')
                                    contImprimirln = 0
                            elif comando == "promedio":
                                if cadenaEntrada in datos[0]:
                                    try:
                                        index = 0
                                        for item in datos[0]: #Con este for conseguimos la posicion del campo en las columnas
                                            if cadenaEntrada == item:
                                                break
                                            index += 1
                                        cont = 1 #Utilizamos un contador para ir avanzando en las filas de la columna
                                        suma = 0
                                        while(cont <= (len(datos)-1)): # Sumando los valores de la columna (campo)
                                            suma += float(datos[cont][index])
                                            cont+=1
                                        promedio = float(suma / (cont-1))
                                        self.text_Area2.configure(state = 'normal')
                                        self.text_Area2.insert("end", f"\n>>>{promedio}")
                                        self.text_Area2.configure(state = 'disable')
                                    except:
                                        print("Error los valores de este campo no pueden ser promediados.")
                                        self.text_Area2.configure(state = 'normal')
                                        self.text_Area2.insert("end", f"\n>>> Funcion promedio: Error los valores del campo proporcionado no pueden ser promediados.")
                                        self.text_Area2.configure(state = 'disable')
                                else:
                                    print("El campo ingresado no existe.")
                                    self.text_Area2.configure(state = 'normal')
                                    self.text_Area2.insert("end", f"\n>>> Funcion promedio: El campo ingresado no existe.")
                                    self.text_Area2.configure(state = 'disable')
                            elif comando == "max":
                                if cadenaEntrada in datos[0]:
                                    try:
                                        index = 0
                                        for item in datos[0]: #Con este for conseguimos la posicion del campo en las columnas
                                            if cadenaEntrada == item:
                                                break
                                            index += 1
                                        cont = 1 #Utilizamos un contador para ir avanzando en las filas de la columna
                                        lista = []
                                        while(cont <= (len(datos)-1)): # Sumando los valores de la columna (campo)
                                            lista.append(float(datos[cont][index]))
                                            cont+=1
                                        maxV = max(lista)
                                        self.text_Area2.configure(state = 'normal')
                                        self.text_Area2.insert("end", f"\n>>>{maxV}")
                                        self.text_Area2.configure(state = 'disable')
                                    except:
                                        print("Error los valores de este campo no son numericos.")
                                        self.text_Area2.configure(state = 'normal')
                                        self.text_Area2.insert("end", f"\n>>> Funcion max: Error los valores de este campo no son numericos.")
                                        self.text_Area2.configure(state = 'disable')
                                else:
                                    print("El campo ingresado no existe.")
                                    self.text_Area2.configure(state = 'normal')
                                    self.text_Area2.insert("end", f"\n>>> Funcion max: El campo ingresado no existe.")
                                    self.text_Area2.configure(state = 'disable')
                            elif comando == "min":
                                if cadenaEntrada in datos[0]:
                                    try:
                                        index = 0
                                        for item in datos[0]: #Con este for conseguimos la posicion del campo en las columnas
                                            if cadenaEntrada == item:
                                                break
                                            index += 1
                                        cont = 1 #Utilizamos un contador para ir avanzando en las filas de la columna
                                        lista = []
                                        while(cont <= (len(datos)-1)): # Sumando los valores de la columna (campo)
                                            lista.append(float(datos[cont][index]))
                                            cont+=1
                                        minV = min(lista)
                                        self.text_Area2.configure(state = 'normal')
                                        self.text_Area2.insert("end", f"\n>>>{minV}")
                                        self.text_Area2.configure(state = 'disable')
                                    except:
                                        print("Error los valores de este campo no son numericos.")
                                        self.text_Area2.configure(state = 'normal')
                                        self.text_Area2.insert("end", f"\n>>> Funcion min: Error los valores de este campo no son numericos.")
                                        self.text_Area2.configure(state = 'disable')
                                else:
                                    print("El campo ingresado no existe.")
                                    self.text_Area2.configure(state = 'normal')
                                    self.text_Area2.insert("end", f"\n>>> Funcion min: El campo ingresado no existe.")
                                    self.text_Area2.configure(state = 'disable')
                            elif comando == "exportarReporte":
                                exportarReporte(cadenaEntrada)
                    else:
                        generarErrorSintactico("Syntactic error: se esperaba ;.")                
                else:
                    generarErrorSintactico("Syntactic error: se esperaba ).")            
            else: 
                generarErrorSintactico("Syntactic error: se esperaba una cadena.")        
        else:
            generarErrorSintactico("Syntactic error: se esperaba (.")    


    def funcion_Tipo2(comando):
        pass


    def funcion_Tipo3(comando):
        pass


    def declaracionTipo1():
        global estadoError
        global tk
        global datos
        global lista_Claves
        global contImprimirln
        if tk.token == "Simbolo =":
            listaTokens.pop(0)
            tk = listaTokens[0]
            if tk.token == "Simbolo [":
                listaTokens.pop(0)
                tk = listaTokens[0]
                #Se resetean los datos si ya existian algunos
                datos = []
                lista_Claves = []
                cuerpoDeclaracionTipo1()
                if tk.token == "Simbolo ]": #Se acepta el comando Claves
                    #una vez aceptado se incorpora la lista de claves a los datos de modo que la posicion 0 sea la de la lista Claves
                    if estadoError != True:
                        datos.append(lista_Claves)
                    #Parte de continuacion del analisis sintactico
                    listaTokens.pop(0)
                    tk = listaTokens[0]
                    contImprimirln = 0
                    print("comando de claves aceptado")
                else:
                    generarErrorSintactico("Syntactic error: se esperaba ].")
            else:
                generarErrorSintactico("Syntactic error: se esperaba [.")
        else:
            generarErrorSintactico("Syntactic error: se esperaba =.")


    def declaracionTipo2():
        global estadoError
        global tk
        global contImprimirln
        if tk.token == "Simbolo =":
            listaTokens.pop(0)
            tk = listaTokens[0]
            if tk.token == "Simbolo [":
                listaTokens.pop(0)
                tk = listaTokens[0]
                cuerpoDeclaracionTipo2()
                if tk.token == "Simbolo ]":
                    listaTokens.pop(0)
                    tk = listaTokens[0]
                    #Se acepta el comando de Registros
                    contImprimirln = 0
                    print("comando de registros aceptados")
                else:
                    generarErrorSintactico("Syntactic error: se esperaba ].")
            else:
                generarErrorSintactico("Syntactic error: se esperaba [.")
        else:
            generarErrorSintactico("Syntactic error: se esperaba =.")


    def cuerpoDeclaracionTipo1():
        global estadoError
        global tk
        global lista_Claves
        if tk.token == "Cadena": 
            #Se reconoce el token Cadena del comando claves por lo que se tiene que añadir a lista de claves
            if estadoError != True:
                lista_Claves.append(tk.lexema)
            listaTokens.pop(0)
            tk = listaTokens[0]
            if tk.token == "Simbolo ,":
                listaTokens.pop(0)
                tk = listaTokens[0]
                cuerpoDeclaracionTipo1()
        else:
            generarErrorSintactico("Syntactic error: se esperaba una cadena.")


    def cuerpoDeclaracionTipo2():
        global estadoError
        global tk
        global datos
        global lista_Registros
        if tk.token == "Simbolo {":
            listaTokens.pop(0)
            tk = listaTokens[0]
            #limpiando datos
            lista_Registros = []
            filaCuerpoDeclaracionTipo2() 
            if tk.token == "Simbolo }":
                listaTokens.pop(0)
                tk = listaTokens[0]
                
                #Una vez aceptados los registros de entrada se verifica si existen los campos claves donde se agregaran
                if len(datos) != 0 and estadoError != True: #Si len(datos) es igual a 0 quiere decir que no existen campos claves
                    datos.append(lista_Registros)

                if tk.token == "Simbolo {":
                    cuerpoDeclaracionTipo2()
            else:
                generarErrorSintactico("Syntactic error: se esperaba {.")
        else:
            generarErrorSintactico("Syntactic error: se esperaba {.")


    def filaCuerpoDeclaracionTipo2():
        global estadoError
        global tk
        global lista_Registros
        if tk.token == "Cadena" or tk.token == "Digito":
            #Una vez aceptada la cadena o el digito se agrega a la lista de registros si no hay errores
            if estadoError != True:
                lista_Registros.append(tk.lexema)

            listaTokens.pop(0)
            tk = listaTokens[0]

            if tk.token == "Simbolo ,":
                listaTokens.pop(0)
                tk = listaTokens[0]
                filaCuerpoDeclaracionTipo2()
        else: 
            generarErrorSintactico("Syntactic error: se esperaba una cadena o un digito.")
    
    

    return inicio()


class VentanaMenu:
    def __init__(self):
        self.txt = None
        self.ventana = Tk()
        self.ventana.title("Menu Principal")
        #Posicionar ventana en el centro
        self.ancho_ventana = 1033
        self.alto_ventana = 500

        self.x_ventana = self.ventana.winfo_screenwidth() // 2 - self.ancho_ventana // 2
        self.y_ventana = self.ventana.winfo_screenheight() // 2 - self.alto_ventana // 2

        self.posicion = str(self.ancho_ventana) + "x" + str(self.alto_ventana) + "+" + str(self.x_ventana) + "+" + str(self.y_ventana)
        self.ventana.geometry(self.posicion)

        self.ventana.configure(bg = 'gray')
        self.ventana.resizable(False, False)

        #Por medio de esto accedo a lo que sucede al dar click sobre la X para cerrar la ventana
        self.ventana.protocol("WM_DELETE_WINDOW", self.on_closing)

        #Se crea el menú de la ventana / el tearoff = 0 es para que no se me cree un submenú al darle click al "----" que me sale en los cascade
        self.miMenu = Menu(self.ventana, tearoff=0)
        self.ventana.configure(menu=self.miMenu)
        
        #Creando una sección/SubMenú esta es la barrita que aparecere arriba en la ventana
        self.miMenu.add_command(label="Cargar Archivo", command=self.cargarArchivo)
        self.miMenu.add_command(label="Analizar", command=self.analizarArchivo)

        #menu bar with cascade 
        self.menuCascade = Menu(self.miMenu, tearoff=False)
        self.miMenu.add_cascade(label="Generar reportes", menu=self.menuCascade)
        self.menuCascade.add_command(label="Reporte de Tokens", command=self.generarReporteTokens)
        self.menuCascade.add_separator()
        self.menuCascade.add_command(label="Reporte de erorres", command=self.generarReporteErrores)

        #scrolledtext 1      
        self.text_Area1 = scrolledtext.ScrolledText(self.ventana,
                                                    wrap = tkinter.WORD,
                                                    width = 60, 
                                                    height = 20, 
                                                    font = ("Terminal",
                                                        15))
        self.text_Area1.configure(state = 'normal')
        self.text_Area1.place(x=10, y = 100) 

        #scrolledtext 2
        self.text_Area2 = scrolledtext.ScrolledText(self.ventana,
                                                    wrap = tkinter.WORD,
                                                    width = 30, 
                                                    height = 20, 
                                                    font = ("Terminal",
                                                        15))
        self.text_Area2.configure(state = 'disable')
        self.text_Area2.place(x=700, y = 100) 

        #Label
        self.label1 = Label(self.ventana, text="Diego Andre Mazariegos Barrientos")
        self.label1.place( x = 10, y = 10)
        self.label2 = Label(self.ventana, text = "202003975")
        self.label2.place(x = 200, y = 10)

        self.ventana.mainloop()

    # Metodo para cerrar la ventana 
    def on_closing(self):
        if messagebox.askokcancel("Cerrar Programa", "Seguro que desea Salir?"):
            self.ventana.quit()

    def cargarArchivo(self): 
        textoEntrada = abrirArchivo()
        if textoEntrada != None:
            self.text_Area1.delete("1.0", "end")
            self.text_Area1.insert("1.0", textoEntrada)


    def analizarArchivo(self):
        global listaErrores
        global listaTokens
        global estadoError
        self.txt = self.text_Area1.get("1.0", "end")
        if self.txt != None:
            self.txt += "~"
            print(self.txt)
            analisisLexico(self.txt)
            print(listaTokens)
            analisisSintactico(self)


    def generarReporteTokens(self):
        if(self.txt != None):
            #abrir o crear el reporte
            f = open('ReporteTokens.html','w', encoding='utf-8')
            #Cuerpo del documento
            cuerpo = '''<!doctype html>
            <html lang="en">

            <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
                integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

            <title>Reporte de Tokens</title>
            </head>

            <body style="background-color: lightseagreen;">
            <div class="container-fluid container p-3 my-3 bg-dark text-white">
                <div class="row">
                <div class="col-12" style="text-align: center; ">
                    <h1>REPORTE DE TOKENS</h1>
                </div>
                </div>
            </div>
            <div class="container-fluid" style="background-color: rgb(255, 255, 255); ">
                
                <div class="row justify-content-md-center">
                <div class="col-md-auto">
                    <h2 style="text-decoration: underline tomato;">Tabla de tokens</h2>
                </div>
                </div>
                <div class="row justify-content-md-center">
                <div class="col-md-auto">
                    <table class="table table-bordered table-striped text-center table-hover table-responsive"
                    style="text-align: center; width: 600px;">
                    <thead>
                        <tr class="table-dark">
                        <th>Token</th>
                        <th>Lexema</th>
                        <th>Patrón</th>
                        <th>Fila</th>
                        <th>Columna</th>
                        </tr>
                    </thead>
                    <tbody>
                    '''  
            for i in listaTokens:
                cuerpo += f'''
                            <tr>
                            <td class="table-success">{i.token}</td>
                            <td class="table-success">{i.lexema}</td>
                            <td class="table-success">{i.expresion}</td>
                            <td class="table-success">{i.fila}</td>
                            <td class="table-success">{i.columna}</td>
                            </tr>
                            '''
    
    
            cuerpo += '''
                </tbody>
                </table>
                </div>
                </div>
                <div class="container-fluid container p-3 my-3 bg-dark text-white">
                <div class="row">
                <div class="col-12" style="text-align: center; ">
                    <h1></h1>
                </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
                integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
                crossorigin="anonymous"></script>
            </body>

            </html>'''

            f.write(cuerpo)
            f.close
            #Aquí se hace la magia de abrirlo automaticamente
            webbrowser.open_new_tab('ReporteTokens.html')
        else:
            print("No se ha cargado ningun archivo")
            messagebox.showwarning('ADVERTENCIA', 'No se selecciono ningun archivo.')

    def generarReporteErrores(self):
        if(self.txt != None):
            f = open('ReporteErrores.html','w',encoding='utf-8')
            
            #Cuerpo del documento
            cuerpo = '''<!doctype html>
            <html lang="en">

            <head>
            <!-- Required meta tags -->
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
                integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

            <title>Reporte de errores</title>
            </head>

            <body style="background-color: lightseagreen;">
            <div class="container-fluid container p-3 my-3 bg-dark text-white">
                <div class="row">
                <div class="col-12" style="text-align: center; ">
                    <h1>REPORTE DE ERRORES</h1>
                </div>
                </div>
            </div>
            <div class="container-fluid" style="background-color: rgb(255, 255, 255); ">
                
                <div class="row justify-content-md-center">
                <div class="col-md-auto">
                    <h2 style="text-decoration: underline tomato;">Tabla de errores</h2>
                </div>
                </div>
                <div class="row justify-content-md-center">
                <div class="col-md-auto">
                    <table class="table table-bordered table-striped text-center table-hover table-responsive"
                    style="text-align: center; width: 600px;">
                    <thead>
                        <tr class="table-dark">
                        <th>Caracter</th>
                        <th>Fila</th>
                        <th>Columna</th>
                        <th>Mensaje de error</th>
                        </tr>
                    </thead>
                    <tbody>
                    '''  
            for i in listaErrores:
                cuerpo += f'''
                            <tr>
                            <td class="table-success">{i.caracter}</td>
                            <td class="table-success">{i.fila}</td>
                            <td class="table-success">{i.columna}</td>
                            <td class="table-success">{i.mensaje}</td>
                            </tr>
                            '''
    
    
            cuerpo += '''
                </tbody>
                </table>
                </div>
                </div>
                <div class="container-fluid container p-3 my-3 bg-dark text-white">
                <div class="row">
                <div class="col-12" style="text-align: center; ">
                    <h1></h1>
                </div>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
                integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
                crossorigin="anonymous"></script>
            </body>

            </html>'''

            f.write(cuerpo)
            f.close
            webbrowser.open_new_tab('ReporteErrores.html')
        else:
            print("No se ha cargado ningun archivo")
            messagebox.showwarning('ADVERTENCIA', 'No se selecciono ningun archivo.')
