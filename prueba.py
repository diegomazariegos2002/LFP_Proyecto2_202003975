#Librería utilizada para graficar grafos
from graphviz import Graph

#Forma de guardar datos
datos = []
lista_Claves = []
lista_Registros = []
lista_Claves.append('hola')
lista_Claves.append('adios1')
lista_Claves.append('adios2')
lista_Claves.append('adios3')
datos.append(lista_Claves)
lista_Registros.append(1)
lista_Registros.append(2)
lista_Registros.append(3)
lista_Registros.append(4)
datos.append(list(lista_Registros))
lista_Registros = []
lista_Registros.append(4)
lista_Registros.append(3)
lista_Registros.append(2)
lista_Registros.append(1)
datos.append(list(lista_Registros))
lista_Registros = []
lista_Registros.append(5)
lista_Registros.append(6)
lista_Registros.append(7)
lista_Registros.append(8)
datos.append(list(lista_Registros))
lista_Registros = []
lista_Registros.append(1)
lista_Registros.append(2)
lista_Registros.append(3)
lista_Registros.append(4)
datos.append(list(lista_Registros))
print(datos)

#Haciendo sumas de una columna dada.
fila = 1
columna = 0
while(fila < (len(datos))):
    while(columna < len(datos[fila])):
        print(datos[fila][columna])
        columna += 1
    columna = 0
    fila += 1

dot = Graph(comment='The Round Table')
dot.attr('node', shape = "plaintext")

dot.node('titulo',label=f'Titulo',)

dot.attr('node', shape = "circle")
dot.node(f'1',f'1')
dot.node(f'2',f'2')
dot.node(f'3',f'3')
dot.edge('1','3', constraint = "false")
dot.node('1','1')
dot.node(f'4',f'4')
dot.edge(f'1',f'2',constraint = 'false')
dot.render('Terreno', view=True)
