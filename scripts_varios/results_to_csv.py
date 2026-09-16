#!/usr/bin/python

## Prgrama que guarda en un csv cuanto tarda una aplicación en ejecutarse. 
## Daniel Mirón

import sys

lista = sys.argv[1:]

out = open("results.csv", "a")
out.write("App,Core,Time")
print (lista)
for archivo in lista:
	partes = archivo.split('-')
	app = partes[0]
	core = partes[1]
	
	print ("app" + app)
	f = open(archivo)
	tiempo = float(f.read())
	f.close()

	out.write("\n" + app + "," + core + "," + tiempo)


out.close()
print ("Hecho")
