#!/usr/bin/python

salida = open ("spec-applications.txt", "w")

with open("Intel-spec-applications.txt") as file:
	for line in file:
		salida.write(line.replace("/vmhdd/vmssd", "/home"))

salida.close()
print("Cambio de directorio copmletado")
