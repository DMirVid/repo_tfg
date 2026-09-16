## Script que genera una lista de 8 aplicaciones aleatorias de la lista de aplicaciones de SPEC CPU 2006 & 2017.
## Daniel Mirón

from random import randint

medio = ("deepsjeng_r","hmmer","leela_r","mcf_r","bzip2","gobmk","sjeng","astar","soplex","xalancbmk","cactusADM","x264_r","dealII","zeusmp","milc","mcf")
alto = ("h264ref","omnetpp_r","lbm","perlbench","lbm_r","xalancbmk_r","gamess","calculix","blender_r","gcc","nab_r","leslie3d","povray")
muy_alto = ("bwaves","libquantum","omnetpp","namd_r","GemsFDTD","sphinx3","tonto","gromacs","povray_r","parest_r","wrf","namd","cactuBSSN_r","imagick_r")

salida = []
junto = medio + alto + muy_alto

for i in range(8):
    salida.append(junto[randint(0, len(junto)-1)])

print(salida)
# salida.clear()

# for i in range(8):
#     salida.append(alto[randint(0, len(alto)-1)])

# print(salida)
# salida.clear()

# for i in range(8):
#     salida.append(muy_alto[randint(0, len(muy_alto)-1)])

# print(salida)

