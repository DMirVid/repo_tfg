#!/usr/bin/python

## Programa antiguo para la ejecuticón de programas sin el Manager.
## Daniel Mirón

import os
import shutil
import subprocess
import sys

parentPath = "/home/dmirvid/pruebas/"

name = ""
skel = ""
cmd = ""
stdin = None
stdout = None
spec_2017 = False

def ejecutar():
        global skel
        if name:
                try:
                        #Crear directorio
                        os.mkdir(name)
                        #Copiar datos
                        #Para las spec_2017 skel está en formato lista
                        if spec_2017:
                                skel = skel[1:-1]
                                dir = skel.split(",")
                                for x in dir:
                                        shutil.copytree(x.strip(), parentPath + name, dirs_exist_ok=True)
                        else:
                                shutil.copytree(skel, parentPath + name, dirs_exist_ok=True)
                except FileExistsError:
                        print("El directorio ya existe, no hace falta copiar")

        #Ejecutar aplicación
        entrada = stdin
        salida = stdout
        if stdin:
                entrada = open(parentPath + name + "/" + stdin)
        if stdout:
                salida = open(parentPath + name + "/" + stdout, w)

        try:
                subprocess.run(cmd.split(" "), stdin=entrada, stdout=salida, cwd=parentPath + name, text=True)
        except Exception as e:
                print("Error al ejecutar la aplicación:\t" + str(e))

        if stdin:
                entrada.close()
        if stdout:
                salida.close()

# Main

aplicacion = sys.argv[1].lower()

with open("/home/dmirvid/spec-applications.txt") as file:
        os.chdir(parentPath)

        for line in file:

                if "cpu_spec_2017" in line:
                        spec_2017 = True
                elif "cpu_spec" in line:
                        continue

                #Linea en blanco. Nueva aplicación
                if line == "\n":
                        if name == aplicacion:
                                print ("Ejecutando " + name)
                                ejecutar()
                        name = ""
                        skel = ""
                        cmd = ""
                        stdin = None
                        stdout = None
                        continue

                data = line.strip().split(":", 1)

                #Obtener parámetros
                if len(data) == 2:
                        if data[0] == "name":
                                name = data[1][1:]
                        elif data[0] == "skel":
                                skel = data[1][1:]
                        elif data[0] == "cmd":
                                cmd = data[1][1:]
                        elif data[0] == "stdin":
                                stdin = data[1][1:]
                        elif data[0] == "stdout":
                                stdout == data[1][1:]
                        else:
                        #Ignorar el numero de la app y client
                                continue

                else:
                        #Mas lineas de comando
                        if "\\" in cmd :
                                cmd = cmd + line.strip()
                        else : #Error
                                print("Error, última app:\t" + name)
