#bot.py            ← clics
# bot.py
import pyautogui
import numpy as np
import cv2
import time
import keyboard
import random
import os

running = False


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def start_bot(hex_color, tol, dist_min, orden):
    global running
    running = True

    # =========================
    # 📌 Cargar puntos editados
    # =========================
    puntos = None
    if os.path.exists("puntos_temp.npy"):
        try:
            puntos = np.load("puntos_temp.npy")
            os.remove("puntos_temp.npy")  # se usan una sola vez
            print(f"📌 Usando {len(puntos)} puntos editados")
        except Exception as e:
            print("⚠️ Error cargando puntos editados:", e)
            puntos = None

    r, g, b = hex_to_rgb(hex_color)
    color_bgr = (b, g, r)

    screen = pyautogui.screenshot()
    img_rgb = np.array(screen)
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    lower = np.array([max(0, c - tol) for c in color_bgr])
    upper = np.array([min(255, c + tol) for c in color_bgr])

    mask = cv2.inRange(img_bgr, lower, upper)
    coords = cv2.findNonZero(mask)

    if coords is None or len(coords) == 0:
        print("⚠️ No se encontraron píxeles.")
        return

    if puntos is not None:
        # Usar puntos editados
        coords = puntos.reshape(-1, 1, 2)
    else:
        # Detectar por color
        mask = cv2.inRange(img_bgr, lower, upper)
        coords = cv2.findNonZero(mask)

        if coords is None or len(coords) == 0:
            print("⚠️ No se encontraron píxeles.")
            return

    # Orden
    if orden == "Izquierda → Derecha":
        coords = sorted(coords, key=lambda p: (p[0][1], p[0][0]))
    elif orden == "Arriba → Abajo":
        coords = sorted(coords, key=lambda p: (p[0][0], p[0][1]))
    elif orden == "Aleatorio":
        random.shuffle(coords)

    print(f"🎯 {len(coords)} puntos detectados")

    height, width = img_bgr.shape[:2]
    usado = np.zeros((height, width), dtype=bool)

    for p in coords:
        if not running:
            print("🛑 Bot detenido")
            return

        x, y = p[0]
        if usado[y, x]:
            continue

        pyautogui.click(x, y)

        y1, y2 = max(0, y - dist_min), min(height, y + dist_min)
        x1, x2 = max(0, x - dist_min), min(width, x + dist_min)
        usado[y1:y2, x1:x2] = True

        time.sleep(0.001)

        if keyboard.is_pressed("esc"):
            running = False
            print("🧨 ESC detectado")
            return

    
    print("✅ Proceso finalizado")


def stop_bot():
    global running
    running = False


def vista_previa_y_editar_hex(
    hex_color,
    tol,
    usar_area=False,
    area_w=500,
    area_h=500,
    orden="Izquierda → Derecha"
):
    # HEX → RGB
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Captura
    if usar_area:
        x, y = pyautogui.position()
        left = max(0, x - area_w // 2)
        top = max(0, y - area_h // 2)
        screen = pyautogui.screenshot(region=(left, top, area_w, area_h))
    else:
        screen = pyautogui.screenshot()

    img_rgb = np.array(screen)
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    # Máscara
    color_bgr = (b, g, r)
    lower = np.array([max(0, c - tol) for c in color_bgr])
    upper = np.array([min(255, c + tol) for c in color_bgr])

    mask = cv2.inRange(img_bgr, lower, upper)
    coords = cv2.findNonZero(mask)

    if coords is None:
        print("⚠️ No se encontraron píxeles.")
        return

    # Orden
    if orden == "Aleatorio":
        np.random.shuffle(coords)
    elif orden == "Arriba → Abajo":
        coords = sorted(coords, key=lambda p: (p[0][1], p[0][0]))
    else:
        coords = sorted(coords, key=lambda p: (p[0][0], p[0][1]))

    puntos_originales = set(tuple(p[0]) for p in coords)
    puntos_activos = set(puntos_originales)

    # =========================
    # 🖱 Editor
    # =========================
    zoom = 1.0
    brush = 3
    ventana = "Vista previa - Editor BOT"

    def dibujar():
        vista = img_bgr.copy()
        overlay = vista.copy()

        for x, y in puntos_activos:
            cv2.circle(overlay, (x, y), 2, (0, 255, 0), -1)

        cv2.addWeighted(overlay, 0.6, vista, 0.4, 0, vista)
        vista = cv2.resize(
            vista, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_NEAREST
        )
        cv2.imshow(ventana, vista)

    def mouse(event, x, y, flags, param):
        nonlocal puntos_activos
        rx, ry = int(x / zoom), int(y / zoom)

        if event == cv2.EVENT_LBUTTONDOWN:
            afectados = {
                p for p in puntos_activos
                if abs(p[0] - rx) <= brush and abs(p[1] - ry) <= brush
            }

            if afectados:
                puntos_activos -= afectados
            else:
                for dx in range(-brush, brush + 1):
                    for dy in range(-brush, brush + 1):
                        nx, ny = rx + dx, ry + dy
                        if 0 <= nx < img_bgr.shape[1] and 0 <= ny < img_bgr.shape[0]:
                            puntos_activos.add((nx, ny))

            dibujar()

    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(ventana, mouse)
    dibujar()

    print("""
🖱 CONTROLES:
• Clic izquierdo → borrar / agregar puntos
• ENTER → guardar y cerrar
• ESC → salir sin guardar
• R → restaurar puntos originales
• + / - → tamaño pincel
• Z → reset zoom
""")

    while True:
        key = cv2.waitKey(30) & 0xFF

        if key == 13:  # ENTER
            np.save("puntos_temp.npy", np.array(list(puntos_activos)))
            print("💾 Puntos guardados")
            break

        elif key == 27:  # ESC
            print("❌ Edición cancelada")
            break

        elif key == ord("r"):
            puntos_activos = set(puntos_originales)
            dibujar()

        elif key in (ord("+"), ord("=")):
            brush = min(20, brush + 1)
            print(f"🖌 Pincel: {brush}")

        elif key == ord("-"):
            brush = max(1, brush - 1)
            print(f"🖌 Pincel: {brush}")

        elif key == ord("z"):
            zoom = 1.0
            dibujar()

    cv2.destroyAllWindows()
