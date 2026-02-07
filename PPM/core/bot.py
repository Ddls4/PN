# bot.py
import pyautogui
import numpy as np
import cv2
import time
import keyboard
import random
import os
import mss

running = False

# =========================
# Utils
# =========================
def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def screenshot_pantalla():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = np.array(sct.grab(monitor))
    return img[:, :, :3]  # BGR

# =========================
# PIXEL LÓGICO (GRID)
# =========================
def detectar_cell_size(mask):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 3 <= w <= 60 and 3 <= h <= 60:
            return max(w, h)

    return None

def extraer_celdas(mask, cell):
    h, w = mask.shape
    celdas = []

    for y in range(0, h, cell):
        for x in range(0, w, cell):
            bloque = mask[y:y+cell, x:x+cell]
            if bloque.size == 0:
                continue

            if np.count_nonzero(bloque) > (cell * cell * 0.6):
                celdas.append((x, y))

    return celdas

# =========================
# BOT
# =========================
def start_bot(hex_color, tol, orden):
    global running
    if running:
        print("⚠️ El bot ya está en ejecución")
        return
    running = True

    puntos = None
    if os.path.exists("puntos_temp.npy"):
        puntos = np.load("puntos_temp.npy")
        os.remove("puntos_temp.npy")

    img_bgr = screenshot_pantalla()

    r, g, b = hex_to_rgb(hex_color)
    color_bgr = (b, g, r)

    # =========================
    # MODO 1 — puntos manuales
    # =========================
    if puntos is not None:
        grupos = [[tuple(p)] for p in puntos]

    # =========================
    # MODO 2 — detección por color (FIX ZOOM)
    # =========================
    else:
        lower = np.array([max(0, c - tol) for c in color_bgr])
        upper = np.array([min(255, c + tol) for c in color_bgr])

        mask = cv2.inRange(img_bgr, lower, upper)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, connectivity=8
        )

        grupos = []

        for i in range(1, num_labels):  # 0 = fondo
            area = stats[i, cv2.CC_STAT_AREA]
            cx, cy = centroids[i]

            if area > 10:  # ajustable, evita ruido
                grupos.append([(int(cx), int(cy))])

        if not grupos:
            print("⚠️ No se encontraron píxeles")
            running = False
            return




    # =========================
    # ORDEN
    # =========================
    if orden == "Aleatorio":
        random.shuffle(grupos)
    elif orden == "Izquierda → Derecha":
        grupos.sort(key=lambda g: g[0][0])
    elif orden == "Arriba → Abajo":
        grupos.sort(key=lambda g: g[0][1])

    # =========================
    # CLICKS
    # =========================
    for grupo in grupos:
        if not running or keyboard.is_pressed("esc"):
            break

        cx, cy = grupo[0]
        pyautogui.click(cx, cy)
        time.sleep(0.01)

    running = False
    print("✅ Bot finalizado")


def stop_bot():
    global running
    running = False


# =========================
# VISTA PREVIA + EDITOR
# =========================
def vista_previa_y_editar_hex(hex_color, tol, orden):
    r, g, b = hex_to_rgb(hex_color)
    color_bgr = (b, g, r)

    img_bgr = screenshot_pantalla()

    lower = np.array([max(0, c - tol) for c in color_bgr])
    upper = np.array([min(255, c + tol) for c in color_bgr])

    mask = cv2.inRange(img_bgr, lower, upper)
    coords = cv2.findNonZero(mask)

    if coords is None:
        print("⚠️ No se encontraron píxeles.")
        return

    puntos_originales = set(tuple(p[0]) for p in coords)
    puntos_activos = set(puntos_originales)

    zoom = 1.0
    brush = 3
    ventana = "Vista previa - Editor BOT"

    def dibujar():
        vista = img_bgr.copy()
        overlay = vista.copy()

        # puntos verdes (detección real)
        for x, y in puntos_activos:
            cv2.circle(overlay, (x, y), 2, (0, 255, 0), -1)

        # =========================
        # puntos rojos (click real)
        # =========================
        mask_preview = np.zeros(img_bgr.shape[:2], dtype=np.uint8)
        for x, y in puntos_activos:
            mask_preview[y, x] = 255

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask_preview, connectivity=8
        )

        for i in range(1, num_labels):
            cx, cy = centroids[i]
            cv2.circle(overlay, (int(cx), int(cy)), 4, (0, 0, 255), -1)

        cv2.addWeighted(overlay, 0.6, vista, 0.4, 0, vista)

        vista = cv2.resize(
            vista, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_NEAREST
        )
        cv2.imshow(ventana, vista)

    def mouse(event, x, y, flags, param):

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
                        puntos_activos.add((rx + dx, ry + dy))

            dibujar()

    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(ventana, mouse)
    dibujar()

    while True:
        key = cv2.waitKey(30) & 0xFF

        if key == 13:  # ENTER
            np.save("puntos_temp.npy", np.array(list(puntos_activos)))
            print("💾 Puntos guardados")
            break
        elif key == 27:  # ESC
            print("❌ Cancelado")
            break
        elif key == ord("r"):
            puntos_activos = set(puntos_originales)
            dibujar()
        elif key in (ord("+"), ord("=")):
            brush = min(20, brush + 1)
        elif key == ord("-"):
            brush = max(1, brush - 1)
        elif key == ord("z"):
            zoom = 1.0
            dibujar()

    cv2.destroyAllWindows()

def estimar_tile_size(coords):
    xs = sorted(set(p[0] for p in coords))
    diffs = [xs[i+1] - xs[i] for i in range(len(xs)-1)]
    diffs = [d for d in diffs if d > 1]

    if not diffs:
        return 1

    return int(np.median(diffs))

def agrupar_por_tiles(coords, tile):
    tiles = {}

    for x, y in coords:
        tx = (x // tile) * tile
        ty = (y // tile) * tile
        tiles.setdefault((tx, ty), []).append((x, y))

    return tiles

def centro_tile(pixels):
    xs = [p[0] for p in pixels]
    ys = [p[1] for p in pixels]
    return int(sum(xs) / len(xs)), int(sum(ys) / len(ys))
