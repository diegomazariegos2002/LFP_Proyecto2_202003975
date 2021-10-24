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
print(datos)

print(datos[1][0], datos[2][0], datos[3][0])

#Haciendo sumas de una columna dada.
fila = 1
columna = 0
while(fila < (len(datos))):
    while(columna < len(datos[fila])):
        print(datos[fila][columna])
        columna += 1
    columna = 0
    fila += 1
