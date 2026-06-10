# Organización de la Carpeta de Resultados

Carpeta para pasar resultados entre la máquina y el ordenador.

## Estructura de Directorios

```
resultados/
├── m1/, m2/, m3/, m4/        # Mezclas (combinaciones de benchmarks)
│   ├── p0/, p1/, ..., p6/    # Políticas (diferentes estrategias de ejecución)
│   │   ├── r1/, r2/, r3/     # Runs (ejecuciones repetidas)
│   │   └── *_summary.txt     # Resumen de resultados
│   └── *_summary.txt         # Resumen agregado de la mezcla
├── instr/                     # Resultados de instrucciones
│   ├── p0/, p1/, ..., p6/    # Políticas
│   │   └── m1/, m2/, m3/, m4/ # Mezclas
│       ├── r1/, r2/          # Runs
│       └── *_summary.txt     # Resumen
└── onemin/                    # Resultados de análisis One Minute
    ├── e/                     # Energía
    └── p/                     # Potencia
```

## Nomenclatura

- **m (Mezcla)**: Combinación específica de benchmarks ejecutados conjuntamente
  - m1: Primera mezcla de benchmarks
  - m2: Segunda mezcla de benchmarks
  - m3: Tercera mezcla de benchmarks
  - m4: Cuarta mezcla de benchmarks

- **p (Política)**: Estrategia o política de ejecución/configuración del sistema
  - p0, p1, ..., p6: Diferentes políticas (7 en total)
  - Cada política representa una configuración diferente del sistema

- **r (Run)**: Ejecución individual de los benchmarks bajo una mezcla y política específica
  - r1, r2, r3, etc.: Ejecuciones repetidas para obtener resultados confiables
  - Permite calcular medias, desviaciones estándar y análisis estadístico

## Archivos de Resumen

- `*_summary.txt`: Archivos que contienen los resultados agregados de una ejecución
  - Ubicados en cada carpeta de política (m1/p0/, m1/p1/, etc.)
  - Contienen métricas y estadísticas de rendimiento

## Cómo Leer los Resultados

1. **Para analizar una mezcla específica**: Navega a `m{X}/` donde X es el número de la mezcla
2. **Para ver resultados de una política**: Entra a `m{X}/p{Y}/` donde Y es el número de política
3. **Para ver runs individuales**: Busca en `m{X}/p{Y}/r{Z}/` para el run número Z
4. **Para comparar políticas**: Revisa los archivos en `m{X}/` que contienen resúmenes agregados