# Tamaño inicial del pincel
DEFAULT_BRUSH_SIZE = 1

# Posiciones de los botones:
BUTTON_POSITIONS = {
    'prev_img': (0.15, 0.02, 0.04, 0.05),    # Imagen Anterior
    'next_img': (0.62, 0.02, 0.04, 0.05),    # Imagen Siguiente
    'up_slice': (0.67, 0.80, 0.04, 0.08),    # Subir Capa
    'down_slice': (0.67, 0.70, 0.04, 0.08),  # Bajar Capa
    'toggle_draw': (0.67, 0.21, 0.15, 0.05), # Activar/Desactivar Dibujo
    'inc_brush': (0.79, 0.16, 0.03, 0.05),   # Aumentar Pincel
    'dec_brush': (0.67, 0.16, 0.03, 0.05),   # Disminuir Pincel
    'clear_slice': (0.67, 0.11, 0.15, 0.05)  # Limpiar Capa Actual
}

# Colores disponibles
COLORS = {
    'red': (228, 8, 34),
    'green': (8, 255, 8),
    'yellow': (255, 245, 84)
}