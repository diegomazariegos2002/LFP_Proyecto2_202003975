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
busquedaCol = "adios1"
index = 0
for item in datos[0]:
    if item == busquedaCol:
        break
    index += 1
cont = 1
suma = 0
while(cont <= (len(datos)-1)):
    suma += datos[cont][index]
    cont+=1

print(suma)

a = '20'
b = '30'
print(float(a) + float(b))