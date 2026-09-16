# repo_tfg
Repositorio para compartir recursos con la maquina de tfg.

## ATENCIÓN
### Se ha cambiado la estructura del proyecto para mejorar legibilidad.
### Cuidado con los nombres de los directorios y la dependencia de archivos.

## Estructura del proyecto

```text
repo_tfg/
├── apps.yaml
├── lib.py
├── lista_eventos.txt
├── README.md
├── trabajo.sh
├── copia_archivos_Manager/         Hice copia de algunos archivos para estudiarlos mejor.
│   ├── launch.bash
│   ├── manager.py
│   └── process.py
├── generar_graficas/               Programas para dibujar gráficas.
│   ├── comparativa_topdown.py
│   ├── graficar_topdown_all.py
│   ├── graficar_topdown.py
│   ├── graficar.py
│   ├── juntas_grafico.py
│   ├── mpki.py
│   └── topdown_juntas.py
├── politicas/                      Politicas cradas durante el proyecto.
│   ├── bajo_back.py
│   ├── buena_pol.py
│   ├── ipc_alto.py
│   ├── ipc_bajo.py
│   ├── new_pol.py
│   ├── pol_FPint.py
│   ├── politica.py
│   ├── politica5.py
│   ├── random_pol.py
├── resultados/                     Carpeta donde guardo los resultados obtenidos.
│   ├── README.md
│   ├── energia_nucleos.csv
│   ├── energia_nucleosE.csv
│   ├── energia_nucleosP.csv
│   ├── energia_nucleosPSMT.csv
│   ├── energia_nucleosSMTE.csv
│   ├── energia_nucleosSMTP.csv
│   ├── energia_nucleosTODO.csv
│   ├── norm_instr.csv
│   ├── norm_tiempos.csv
│   ├── salida_tiempos.csv
│   └── instr/
├── scripts_varios/                 Diversos scripts usados durante el proyecto.
│   ├── all_to_csv.py
│   ├── app_sola.py
│   ├── apps.py
│   ├── cambiar_dir.py
│   ├── combine_vtune_ecores.py
│   ├── core_microbenchmark.c
│   ├── ejecutar_prueba.py
│   ├── energia.sh
│   ├── frec_down.sh
│   ├── frec_up.sh
│   ├── launch.sh
│   ├── lista.sh
│   ├── nucleo_solo.sh
│   ├── nucleos_E.sh
│   ├── nucleos_P.sh
│   ├── print_results.py
│   ├── results_to_csv.py
│   ├── run_core_benchmark.sh
│   ├── scritp.sh
│   └── topdown_all_to_csv.py
├── vtune/
│   └── archivos de resumen de VTune
├── vtuneP/
│   └── archivos de resumen de VTune para P-core
└── .gitignore
```


