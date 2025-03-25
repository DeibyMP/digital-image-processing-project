import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Button, RadioButtons
from .constants import BUTTON_POSITIONS, COLORS

class EditorUI:
    def __init__(self, editor):
        self.editor = editor
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        self.fig = plt.figure(figsize=(10, 6))
        self.gs = gridspec.GridSpec(1, 2, width_ratios=[4, 1])
        self.ax = plt.subplot(self.gs[0])
        self.ax_controls = plt.subplot(self.gs[1])
        self.ax_controls.axis('off')
        
        # Crear controles
        self._create_buttons()
        self._create_color_selector()
        self._connect_events()
        
        # Estado del menú
        self.menu_visible = False
        self.menu_buttons = []
        
    def _create_buttons(self):
        """Crea los botones de control"""
        # Botón del menú principal
        self.btn_menu = Button(
            plt.axes([0.02, 0.92, 0.08, 0.05]),
            'Image',
            hovercolor='lightgray'
        )
        self.btn_menu.on_clicked(self._toggle_menu)
        
        # Botones principales
        self.btn_prev = Button(plt.axes(BUTTON_POSITIONS['prev_img']), '<---')
        self.btn_next = Button(plt.axes(BUTTON_POSITIONS['next_img']), '--->')
        self.btn_up = Button(plt.axes(BUTTON_POSITIONS['up_slice']), '↑')
        self.btn_down = Button(plt.axes(BUTTON_POSITIONS['down_slice']), '↓')
        self.btn_draw = Button(plt.axes(BUTTON_POSITIONS['toggle_draw']), 'Activar Dibujo')
        self.btn_clear = Button(plt.axes(BUTTON_POSITIONS['clear_slice']), 'Limpiar Capa')
        self.btn_inc_brush = Button(plt.axes(BUTTON_POSITIONS['inc_brush']), f'{self.editor.brush_size} +')
        self.btn_dec_brush = Button(plt.axes(BUTTON_POSITIONS['dec_brush']), f'{self.editor.brush_size} -')

        # Asignar manejadores
        self.btn_prev.on_clicked(lambda _: self.editor.change_image('prev'))
        self.btn_next.on_clicked(lambda _: self.editor.change_image('next'))
        self.btn_up.on_clicked(lambda _: self.editor.change_slice(self.editor.current_slice + 1))
        self.btn_down.on_clicked(lambda _: self.editor.change_slice(self.editor.current_slice - 1))
        self.btn_draw.on_clicked(lambda _: self.editor.toggle_drawing())
        self.btn_clear.on_clicked(lambda _: self.editor.clear_current_slice())
        self.btn_inc_brush.on_clicked(self._increase_brush_size)
        self.btn_dec_brush.on_clicked(self._decrease_brush_size)
        
    def _create_color_selector(self):
        """Crea el selector de color tipo dropdown"""
        self.radio = RadioButtons(
            plt.axes([0.67, 0.35, 0.15, 0.12]),
            ('red', 'green', 'yellow'),
            active=0
        )
        self.radio.on_clicked(lambda label: self.editor.set_color(label))
        
    def _toggle_menu(self, event):
        """Muestra/oculta el menú de imágenes"""
        if self.menu_visible:
            # Ocultar menú
            for btn in self.menu_buttons:
                btn.ax.remove()
            self.menu_buttons = []
        else:
            # Mostrar menú
            btn_load = Button(
                plt.axes([0.02, 0.86, 0.08, 0.05]),
                'Cargar',
                hovercolor='lightgray'
            )
            btn_load.on_clicked(lambda _: (self.editor.load_image(), self._toggle_menu(None)))
            
            btn_save = Button(
                plt.axes([0.02, 0.80, 0.08, 0.05]),
                'Guardar',
                hovercolor='lightgray'
            )
            btn_save.on_clicked(lambda _: (self.editor.save_image(), self._toggle_menu(None)))
            
            self.menu_buttons = [btn_load, btn_save]
        
        self.menu_visible = not self.menu_visible
        self.fig.canvas.draw_idle()

    def _increase_brush_size(self, event):
        """Incrementa el tamaño del pincel"""
        self.editor.brush_size += 1
        self._update_brush_buttons()
        
    def _decrease_brush_size(self, event):
        """Disminuye el tamaño del pincel"""
        if self.editor.brush_size > 1:
            self.editor.brush_size -= 1
        self._update_brush_buttons()
        
    def _update_brush_buttons(self):
        """Actualiza los labels de los botones de pincel"""
        self.btn_inc_brush.label.set_text(f'{self.editor.brush_size} +')
        self.btn_dec_brush.label.set_text(f'{self.editor.brush_size} -')
        plt.draw()

    def _connect_events(self):
        """Conecta los eventos del mouse"""
        self.cid_click = self.fig.canvas.mpl_connect(
            'button_press_event', 
            self._on_click
        )
        self.cid_motion = self.fig.canvas.mpl_connect(
            'motion_notify_event', 
            self._on_motion
        )
        self.cid_release = self.fig.canvas.mpl_connect(
            'button_release_event',
            self._on_release
        )
        
    def update_drawing_button(self):
        """Actualiza el texto del botón de dibujo"""
        text = "Desactivar Dibujo" if self.editor.drawing_enabled else "Activar Dibujo"
        self.btn_draw.label.set_text(text)
        
    def update_display(self):
        """Actualiza la visualización de la imagen"""
        if self.editor.image is None:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'No hay imagen cargada', 
                        ha='center', va='center', fontsize=12)
            self.fig.suptitle('Editor de Imágenes - Ninguna imagen cargada', fontsize=12)
            plt.draw()
            return
        
        self.ax.clear()
        img_slice = self.editor.image[..., self.editor.current_slice]
        self.ax.imshow(img_slice, cmap='gray')

        if self.editor.mask is not None:
            mask_slice = self.editor.mask[..., self.editor.current_slice]
            
            red_mask = np.ma.masked_where(mask_slice != 1, mask_slice)
            green_mask = np.ma.masked_where(mask_slice != 2, mask_slice)
            yellow_mask = np.ma.masked_where(mask_slice != 3, mask_slice)
        
            if red_mask.any():
                self.ax.imshow(red_mask, alpha=0.5, cmap='Reds', vmin=0, vmax=3)
            if green_mask.any():
                self.ax.imshow(green_mask, alpha=0.5, cmap='Greens', vmin=0, vmax=3)
            if yellow_mask.any():
                self.ax.imshow(yellow_mask, alpha=0.5, cmap='YlOrBr', vmin=0, vmax=3)
    
            title = f'Imagen: {self.editor.image_names[self.editor.current_image_index]} | Capa: {self.editor.current_slice}'
            if self.editor.drawing_enabled:
                title += f" | Modo dibujo: ACTIVADO | Color: {self.editor.current_color}"
            self.fig.suptitle(title, fontsize=12)
            plt.draw()
        
    def _on_click(self, event):
        """Manejador de eventos de clic del mouse"""
        if event.inaxes != self.ax or not self.editor.drawing_enabled:
            return
            
        if event.button == 1:
            self.editor.drawing = True
            self._paint_area(event)
                
    def _on_motion(self, event):
        """Manejador de eventos de movimiento del mouse"""
        if event.inaxes != self.ax or not self.editor.drawing or not self.editor.drawing_enabled:
            return
        self._paint_area(event)
        
    def _on_release(self, event):
        """Manejador de liberación del botón del mouse"""
        if event.button == 1:
            self.editor.drawing = False
        
    def _paint_area(self, event):
        """Pinta un área alrededor de la posición del mouse"""
        if not hasattr(event, 'xdata') or event.xdata is None:
            return
        
        orig_col = int(event.xdata)
        orig_row = int(event.ydata)
        
        color_value = {'red': 1, 'green': 2, 'yellow': 3}[self.editor.current_color]
    
        # Pintar un área circular alrededor del punto
        for i in range(max(0, orig_col - self.editor.brush_size), 
                      min(self.editor.image.shape[1], orig_col + self.editor.brush_size + 1)):
            for j in range(max(0, orig_row - self.editor.brush_size), 
                          min(self.editor.image.shape[0], orig_row + self.editor.brush_size + 1)):
                if (i - orig_col)**2 + (j - orig_row)**2 <= self.editor.brush_size**2:
                    self.editor.mask[j, i, self.editor.current_slice] = color_value
    
        self.update_display()
        
    def show(self):
        """Muestra la interfaz"""
        plt.show()