"""
Nota: 
Sección 4 (futura): Reconocimiento avanzado
Que sea independiente
Que trabaje con bloques de píxeles, no con acciones del bot 

1️⃣ Uso de LAB + ΔE 
2️⃣ Muestreo por step (no pixel a pixel) 
step = 10
3️⃣ Uso de OrderedDict para colores únicos 
4️⃣ Overlay desacoplado 
5️⃣ Representación visual + leyenda 

1️⃣ color_mas_parecido no debería aplicar umbral 
Siempre devolver el mejor match:
return mejor, mejor_hex, menor_dist

advanced/
 ├── analyzer.py        ← captura + muestreo
 ├── overlay.py         ← SOLO pintar
 ├── matcher.py         ← LAB + ΔE
 ├── models.py          ← estructuras de datos
 └── controller.py      ← conecta todo

Flujo correcto (conceptual)
[F8]
 ↓
Screen Capture
 ↓
Region Sampler
 ↓
Unique Color Extractor
 ↓
Palette Matcher
 ↓
Overlay Renderer
 ↓
Legend Builder

"""