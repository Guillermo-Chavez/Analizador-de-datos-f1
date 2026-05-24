# 🏎️ Analizador de Fórmula 1 — Módulo 1: Comparador de telemetría

Dashboard interactivo hecho con **Streamlit** + **FastF1** para comparar la telemetría de dos pilotos vuelta a vuelta.

## Qué incluye esta primera versión

- Selector de temporada, Gran Premio y sesión (FP1-3, Clasificación, Sprint, Carrera)
- Comparación de **velocidad, acelerador y freno** vs distancia
- Comparación de **RPM y marcha**
- **Delta de tiempo** acumulado a lo largo de la vuelta (quién va por delante y dónde)
- **Mapa del circuito** coloreado por velocidad, con números de curva
- Tabla **resumen de vuelta**: tiempo, sectores, compuesto de neumático, vida del neumático, velocidad punta

Las demás secciones que mencionaste (temporada completa, clasificación general, neumáticos/estrategia, pit stops, sectores a fondo, posiciones) las iremos añadiendo como pestañas nuevas sobre esta misma base.

## Instalación

```bash
# (opcional pero recomendado) crear un entorno virtual
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

# instalar dependencias
pip install -r requirements.txt
```

## Ejecutar

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador (normalmente en `http://localhost:8501`).

## Notas importantes

- **Necesitas conexión a internet**: FastF1 descarga los datos oficiales desde la API de F1 la primera vez que cargas una sesión. Después quedan guardados en la carpeta `f1_cache/` que se crea junto al script, así que las siguientes cargas son instantáneas.
- **Telemetría solo desde 2018**: temporadas anteriores no tienen datos de telemetría/posición disponibles.
- Si cambias Temporada, Gran Premio o Sesión en la barra lateral, tienes que volver a pulsar **"Cargar sesión"** para que se aplique. Los selectores de piloto y vuelta sí se actualizan al instante.
- Si eliges una sesión que todavía no se ha corrido (por ejemplo, un GP futuro de la temporada en curso), verás un mensaje de error porque F1 aún no ha publicado esos datos.
# Analizador-de-datos-f1