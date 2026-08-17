import requests
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, RoundedRectangle, Line
from kivy.metrics import dp


class WeatherIcon(Widget):

    def __init__(self, tipo="sol", **kwargs):
        super().__init__(**kwargs)
        self.tipo = tipo
        self.bind(pos=self.dibujar, size=self.dibujar)
        self.dibujar()
    def dibujar(self, *args):
        self.canvas.clear()
        Color(1, 0, 0, 1)
        Ellipse(pos=(500, 500), size=(100, 100))
        x, y = self.pos
        w, h = self.size

        if w < 5 or h < 5:
            return

        # SOL
        if self.tipo == "sol":

            Color(1, 0.8, 0, 1)

            radio = min(w, h) * 0.25

            Ellipse(
                pos=(
                    x + w / 2 - radio,
                    y + h / 2 - radio
                ),
                size=(radio * 2, radio * 2)
            )

            # Rayos
            Color(1, 0.9, 0.2, 1)

            Line(
                points=[
                    x + w/2, y + h*0.05,
                    x + w/2, y + h*0.25
                ],
                width=dp(4)
            )

            Line(
                points=[
                    x + w/2, y + h*0.75,
                    x + w/2, y + h*0.95
                ],
                width=dp(4)
            )

            Line(
                points=[
                    x + w*0.05, y + h/2,
                    x + w*0.25, y + h/2
                ],
                width=dp(4)
            )

            Line(
                points=[
                    x + w*0.75, y + h/2,
                    x + w*0.95, y + h/2
                ],
                width=dp(4)
            )

        # NUBE
        elif self.tipo == "nube":

            Color(0.85, 0.9, 0.95, 1)

            Ellipse(
                pos=(x + w*0.15, y + h*0.30),
                size=(w*0.45, h*0.40)
            )

            Ellipse(
                pos=(x + w*0.35, y + h*0.40),
                size=(w*0.45, h*0.50)
            )

            Ellipse(
                pos=(x + w*0.55, y + h*0.30),
                size=(w*0.35, h*0.40)
            )

            RoundedRectangle(
                pos=(x + w*0.15, y + h*0.25),
                size=(w*0.70, h*0.30),
                radius=[dp(20)]
            )

        # LLUVIA
        elif self.tipo == "lluvia":

            Color(0.60, 0.70, 0.82, 1)

            Ellipse(
                pos=(x + w*0.15, y + h*0.40),
                size=(w*0.45, h*0.35)
            )

            Ellipse(
                pos=(x + w*0.35, y + h*0.48),
                size=(w*0.45, h*0.42)
            )

            Ellipse(
                pos=(x + w*0.55, y + h*0.40),
                size=(w*0.35, h*0.35)
            )

            RoundedRectangle(
                pos=(x + w*0.15, y + h*0.35),
                size=(w*0.70, h*0.25),
                radius=[dp(15)]
            )

            # Gotas
            Color(0.2, 0.6, 1, 1)

            Line(
                points=[
                    x + w*0.30, y + h*0.28,
                    x + w*0.30, y + h*0.05
                ],
                width=dp(5)
            )

            Line(
                points=[
                    x + w*0.50, y + h*0.28,
                    x + w*0.50, y + h*0.05
                ],
                width=dp(5)
            )

            Line(
                points=[
                    x + w*0.70, y + h*0.28,
                    x + w*0.70, y + h*0.05
                ],
                width=dp(5)
            )

    
class TarjetaDia(BoxLayout):

    def __init__(self, dia, maxima, minima, lluvia, codigo, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = dp(10)
        self.spacing = dp(4)

        self.size_hint_x = None
        self.width = dp(125)

        with self.canvas.before:
            Color(0.10, 0.22, 0.40, 1)

            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )

        self.bind(pos=self.actualizar_rect, size=self.actualizar_rect)

        self.add_widget(
            Label(
                text=dia,
                font_size=dp(16),
                bold=True,
                color=(1, 1, 1, 1)
            )
        )

        tipo = WeatherApp.tipo_clima(codigo)

        icono = WeatherIcon(
            tipo=tipo,
            size_hint=(1, None),
               height=dp(70)
        )

        self.add_widget(icono)

        self.add_widget(
            Label(
                text=f"{maxima:.1f}°",
                font_size=dp(22),
                bold=True,
                color=(1, 1, 1, 1)
            )
        )

        self.add_widget(
            Label(
                text=f"Mín {minima:.1f}°",
                font_size=dp(14),
                color=(0.75, 0.85, 1, 1)
            )
        )

        self.add_widget(
            Label(
                text=f"Lluvia {lluvia}%",
                font_size=dp(13),
                color=(0.65, 0.85, 1, 1)
            )
        )

    def actualizar_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class WeatherApp(App):

    @staticmethod
    def tipo_clima(codigo):

        if codigo is None:
            return "sol"

        # Lluvia / tormenta / nieve
        if codigo >= 51:
            return "lluvia"

        # Nubes
        if codigo in [1, 2, 3]:
            return "nube"

        # Despejado
        return "sol"

    def consultar_clima(self):

        ciudad = self.root.ids.ciudad.text.strip()

        if not ciudad:
            self.root.ids.nombre_ciudad.text = "Escribe una ciudad"
            return

        try:

            # Buscar ciudad
            url_ciudad = "https://geocoding-api.open-meteo.com/v1/search"

            parametros_ciudad = {
                "name": ciudad,
                "count": 1,
                "language": "es",
                "format": "json"
            }

            respuesta = requests.get(
                url_ciudad,
                params=parametros_ciudad,
                timeout=10
            )

            datos_ciudad = respuesta.json()

            if "results" not in datos_ciudad:
                self.root.ids.nombre_ciudad.text = "Ciudad no encontrada"
                return

            lugar = datos_ciudad["results"][0]

            latitud = lugar["latitude"]
            longitud = lugar["longitude"]
            nombre = lugar["name"]

            # Obtener clima
            url_clima = "https://api.open-meteo.com/v1/forecast"

            parametros_clima = {
                "latitude": latitud,
                "longitude": longitud,

                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "wind_speed_10m,"
                    "weather_code"
                ),

                "daily": (
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "precipitation_probability_max,"
                    "weather_code"
                ),

                "forecast_days": 7,
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "timezone": "auto"
            }

            respuesta_clima = requests.get( 
                url_clima,
                params=parametros_clima,
                timeout=10
            )

            datos = respuesta_clima.json()

            actual = datos["current"]
            diario = datos["daily"]

            temperatura = actual["temperature_2m"]
            humedad = actual["relative_humidity_2m"]
            viento = actual["wind_speed_10m"]
            codigo_actual = actual["weather_code"]

            # Información principal
            self.root.ids.nombre_ciudad.text = nombre
            self.root.ids.temperatura.text = f"{temperatura:.1f} °C"
            self.root.ids.humedad.text = f"{humedad}%"
            self.root.ids.viento.text = f"{viento:.1f} km/h"

            # Cambiar dibujo principal
            contenedor = self.root.ids.icono_actual
            contenedor.clear_widgets()

            contenedor.add_widget(
                WeatherIcon(
                    tipo=self.tipo_clima(codigo_actual)
                )
            )

            # Limpiar pronóstico
            pronostico = self.root.ids.pronostico
            pronostico.clear_widgets()

            dias_semana = [
                "LUN",
                "MAR",
                "MIÉ",
                "JUE",
                "VIE",
                "SÁB",
                "DOM"
            ]

            for i in range(7):

                fecha = datetime.strptime(
                    diario["time"][i],
                    "%Y-%m-%d"
                )

                dia = dias_semana[fecha.weekday()]

                maxima = diario["temperature_2m_max"][i]
                minima = diario["temperature_2m_min"][i]
                lluvia = diario["precipitation_probability_max"][i]
                codigo = diario["weather_code"][i]

                tarjeta = TarjetaDia(
                    dia,
                    maxima,
                    minima,
                    lluvia,
                    codigo
                )

                pronostico.add_widget(tarjeta)

        except Exception as error:

            print("ERROR:", error)

            self.root.ids.nombre_ciudad.text = "Error al consultar"


if __name__ == "__main__":

    Builder.load_file("weather.kv")

    WeatherApp().run()