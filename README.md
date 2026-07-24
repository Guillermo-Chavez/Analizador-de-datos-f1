<div align="center">

# 🏎️ Analizador de Fórmula 1
### Módulo 1 · Comparador de telemetría entre pilotos

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![FastF1](https://img.shields.io/badge/FastF1-E10600?style=flat&logo=formula1&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logoColor=white)

Dashboard interactivo para explorar datos **oficiales** de Fórmula 1: comparación de telemetría entre pilotos, vuelta a vuelta.

[**🚀 Ver demo en vivo**](https://analizador-de-datos-f1.onrender.com) · [Instalación](#️-instalación-y-uso-local) · [Roadmap](#️-roadmap)

</div>

---

## 📑 Tabla de contenido

- [Descripción](#-descripción)
- [Demo en vivo](#-demo-en-vivo)
- [Funcionalidades](#-funcionalidades)
- [Tecnologías](#️-tecnologías)
- [Instalación y uso local](#️-instalación-y-uso-local)
- [Estructura del repositorio](#-estructura-del-repositorio)
- [Notas importantes](#️-notas-importantes)
- [Roadmap](#️-roadmap)
- [Autor](#-autor)

---

## 📋 Descripción

**Analizador de Fórmula 1** es un dashboard construido con **Streamlit** y **[FastF1](https://github.com/theOehrly/Fast-F1)**, la librería que da acceso a los datos oficiales de telemetría y cronometraje de la F1. Este primer módulo se centra en comparar cómo afronta cada piloto una misma vuelta: dónde acelera, dónde frena, dónde gana o pierde tiempo respecto a su rival.

## 🌐 Demo en vivo

No hace falta instalar nada para probarla:

🔗 **[https://analizador-de-datos-f1.onrender.com](https://analizador-de-datos-f1.onrender.com)**

> ⏳ Al estar en un plan gratuito de Render, la app puede tardar unos segundos en despertar si nadie la ha usado recientemente.

## ✨ Funcionalidades

- 🗓️ Selector de **temporada, Gran Premio y sesión** (FP1-3, Clasificación, Sprint, Carrera)
- 🚀 Comparación de **velocidad, acelerador y freno** vs. distancia
- ⚙️ Comparación de **RPM y marcha**
- ⏱️ **Delta de tiempo** acumulado a lo largo de la vuelta (quién va por delante y en qué punto del trazado)
- 🗺️ **Mapa del circuito** coloreado por velocidad, con los números de curva marcados
- 📊 Tabla **resumen de vuelta**: tiempo total, sectores, compuesto de neumático, vida del neumático y velocidad punta

## 🛠️ Tecnologías

| Herramienta | Uso |
|---|---|
| [FastF1](https://github.com/theOehrly/Fast-F1) | Acceso a datos oficiales de telemetría y cronometraje de F1 |
| Streamlit | Interfaz del dashboard |
| Plotly | Gráficos interactivos de telemetría y delta de tiempo |
| Matplotlib | Mapa del circuito coloreado por velocidad |
| pandas / NumPy | Procesamiento de los datos de telemetría |

## ⚙️ Instalación y uso local

```bash
git clone https://github.com/Guillermo-Chavez/Analizador-de-datos-f1.git
cd Analizador-de-datos-f1

# (opcional pero recomendado) entorno virtual
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

La app se abre automáticamente en `http://localhost:8501`.

## 📁 Estructura del repositorio

```
├── app.py              # Aplicación de Streamlit
├── requirements.txt    # Dependencias del proyecto
└── f1_cache/           # Caché local de FastF1 (se crea sola al ejecutar la app)
```

## ⚠️ Notas importantes

- **Requiere conexión a internet**: FastF1 descarga los datos oficiales desde la API de F1 la primera vez que se carga una sesión. Después quedan guardados en `f1_cache/`, así que las siguientes cargas son instantáneas.
- **Telemetría disponible solo desde 2018**: temporadas anteriores no tienen datos de telemetría ni de posición.
- Si cambias Temporada, Gran Premio o Sesión en la barra lateral, hay que volver a pulsar **"Cargar sesión"** para aplicar el cambio. Los selectores de piloto y vuelta sí se actualizan al instante.
- Si eliges una sesión que aún no se ha corrido, verás un mensaje de error porque la F1 todavía no ha publicado esos datos.

## 🗺️ Roadmap

- [x] Comparador de telemetría entre pilotos
- [ ] Resumen de temporada
- [ ] Clasificación
- [ ] Neumáticos y estrategia
- [ ] Pit stops
- [ ] Sectores
- [ ] Posiciones

## 👤 Autor

**Guillermo Chávez** — Data Scientist Jr.
[LinkedIn](https://www.linkedin.com/in/guillermo-rafael-chavez-akita/) · [GitHub](https://github.com/Guillermo-Chavez)
