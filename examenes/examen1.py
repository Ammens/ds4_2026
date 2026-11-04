"""Examen 1 - Jonathan Rascon Sifuentes - 24/09/2026 - Leer y escribir un archivo CSV (frases de peliculas) -
La forma de ejecutar el programa es: python examen1.py entrada.csv salida.csv - Gemini Pro 3.1"""

import csv
import argparse
import re
from collections import defaultdict

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Static

# Clase para representar una frase y su película asociada
class FrasePelicula:
    def __init__(self, frase, pelicula):
        self.frase = frase.strip()
        self.pelicula = pelicula.strip()

    def __str__(self):
        return f'"{self.frase}" - {self.pelicula}'

# Funciones para leer y escribir archivos CSV
def leer_csv(archivo_entrada):
    lista_frases = []
    try:
        with open(archivo_entrada, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None) 
            
            for row in reader:
                if len(row) >= 2:
                    frase = row[0]
                    pelicula = row[1]
                    lista_frases.append(FrasePelicula(frase, pelicula))
        return lista_frases, f"Archivo '{archivo_entrada}' leido correctamente con {len(lista_frases)} frases."
    except FileNotFoundError:
        return lista_frases, f"El archivo '{archivo_entrada}' no existe. Se creara uno nuevo al guardar."

def escribir_csv(archivo_salida, lista_frases):
    try:
        with open(archivo_salida, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frase', 'Pelicula'])
            for f in lista_frases:
                writer.writerow([f.frase, f.pelicula])
        return True, f"Cambios guardados exitosamente en '{archivo_salida}'."
    except Exception as e:
        return False, f"Error al intentar escribir el archivo: {e}"

# Funcion para buscar palabras en las frases
def buscar_palabra(lista_frases, palabra):
    palabra = palabra.strip().lower()
    if not palabra:
        return lista_frases
    return [f for f in lista_frases if palabra in f.frase.lower()]

# Función para obtener estadísticas de frases, películas y palabras
def obtener_estadisticas(lista_frases):
    if not lista_frases:
        return 0, 0, 0

    total_frases = len(lista_frases)
    
    peliculas_unicas = set(f.pelicula.lower() for f in lista_frases)
    total_peliculas = len(peliculas_unicas)
    
    palabras_unicas = set()
    for f in lista_frases:
        palabras = re.findall(r'\b\w+\b', f.frase.lower())
        palabras_unicas.update(palabras)
        
    total_palabras = len(palabras_unicas)

    return total_frases, total_peliculas, total_palabras

def frases_agrupadas(lista_frases):
    # Agrupar frases por película
    agrupado = defaultdict(list)
    for f in lista_frases:
        agrupado[f.pelicula].append(f.frase)
        
    peliculas_ordenadas = sorted(agrupado.items(), key=lambda x: len(x[1]), reverse=True)
    
    return peliculas_ordenadas


class GestorFrasesApp(App):
    TITLE = "Gestor de frases de cine"
    CSS = """
    Screen { background: #101820; color: #edf2f4; }
    Header { background: #ef8354; color: #101820; }
    Footer { background: #273b45; }
    #contenido { height: 1fr; padding: 1 2; }
    #barra { height: auto; margin-bottom: 1; }
    #busqueda { width: 1fr; }
    Button { margin-left: 1; min-width: 16; }
    #principal { height: 1fr; }
    #tabla { width: 3fr; height: 1fr; border: round #4f5d75; }
    #panel { width: 1fr; padding: 0 2; border: round #4f5d75; }
    .titulo { text-style: bold; color: #ef8354; margin-bottom: 1; }
    .campo { margin-top: 1; }
    #estado { height: 3; margin-top: 1; color: #f2cc8f; }
    #estadisticas { margin-top: 2; color: #8ecae6; }
    #frase, #pelicula { width: 100%; }
    """

    def __init__(self, frases, archivo_salida):
        super().__init__()
        self.frases = frases
        self.archivo_salida = archivo_salida

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="contenido"):
            with Horizontal(id="barra"):
                yield Input(placeholder="Buscar una palabra en las frases...", id="busqueda")
                yield Button("Limpiar", id="limpiar")
                yield Button("Guardar", id="guardar", variant="success")
            with Horizontal(id="principal"):
                yield DataTable(id="tabla", cursor_type="row")
                with Vertical(id="panel"):
                    yield Label("AGREGAR FRASE", classes="titulo")
                    yield Label("Frase", classes="campo")
                    yield Input(placeholder="Escribe la frase", id="frase")
                    yield Label("Película", classes="campo")
                    yield Input(placeholder="Escribe el título", id="pelicula")
                    yield Button("Agregar y guardar", id="agregar", variant="primary")
                    yield Button("Agrupar por película", id="agrupar")
                    yield Static(id="estadisticas")
            yield Static(id="estado")
        yield Footer()

    def on_mount(self) -> None:
        tabla = self.query_one("#tabla", DataTable)
        tabla.add_columns("Frase", "Película")
        self.actualizar_tabla(self.frases)
        self.actualizar_estadisticas()
        self.query_one("#estado", Static).update("Listo para trabajar.")

    def actualizar_tabla(self, frases) -> None:
        tabla = self.query_one("#tabla", DataTable)
        tabla.clear()
        tabla.add_rows((frase.frase, frase.pelicula) for frase in frases)

    def actualizar_estadisticas(self) -> None:
        total_frases, total_peliculas, total_palabras = obtener_estadisticas(self.frases)
        self.query_one("#estadisticas", Static).update(
            f"FRASES\n{total_frases}\n\nPELICULAS UNICAS\n{total_peliculas}\n\nPALABRAS DIFERENTES\n{total_palabras}"
        )

    def guardar(self) -> None:
        guardado, mensaje = escribir_csv(self.archivo_salida, self.frases)
        self.query_one("#estado", Static).update(mensaje)
        if guardado:
            self.actualizar_estadisticas()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "busqueda":
            resultados = buscar_palabra(self.frases, event.value)
            self.actualizar_tabla(resultados)
            self.query_one("#estado", Static).update(f"{len(resultados)} frase(s) encontradas.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        boton = event.button.id
        if boton == "limpiar":
            self.query_one("#busqueda", Input).value = ""
        elif boton == "guardar":
            self.guardar()
        elif boton == "agregar":
            self.agregar_frase_desde_formulario()
        elif boton == "agrupar":
            self.mostrar_agrupadas()

    def agregar_frase_desde_formulario(self) -> None:
        frase = self.query_one("#frase", Input).value.strip()
        pelicula = self.query_one("#pelicula", Input).value.strip()
        if not frase or not pelicula:
            self.query_one("#estado", Static).update("Completa la frase y la pelicula antes de agregar.")
            return
        self.frases.append(FrasePelicula(frase, pelicula))
        self.query_one("#frase", Input).value = ""
        self.query_one("#pelicula", Input).value = ""
        self.actualizar_tabla(self.frases)
        self.guardar()
        self.query_one("#estado", Static).update("Frase agregada y guardada correctamente.")

    def mostrar_agrupadas(self) -> None:
        grupos = frases_agrupadas(self.frases)
        filas = []
        for pelicula, frases in grupos:
            filas.extend(FrasePelicula(frase, pelicula) for frase in frases)
        self.actualizar_tabla(filas)
        self.query_one("#estado", Static).update("Vista agrupada por pelicula. Usa Limpiar para volver a todas las frases.")

def main():
    parser = argparse.ArgumentParser(description="Gestor de Frases y Películas usando archivos CSV.")
    parser.add_argument("entrada", help="Nombre del archivo CSV a leer (ej. entrada.csv)")
    parser.add_argument("salida", help="Nombre del archivo CSV a escribir (ej. salida.csv)")
    
    args = parser.parse_args()
    archivo_entrada = args.entrada
    archivo_salida = args.salida

    frases, mensaje = leer_csv(archivo_entrada)
    app = GestorFrasesApp(frases, archivo_salida)
    app.run()

if __name__ == "__main__":
    main()