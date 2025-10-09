import tkinter as tk
from tkinter import ttk
import wx
from PIL import Image, ImageTk
import cv2

# UI tkinter class
class FilterUI:
    def __init__(self, root, video_filter):
        self.root = root
        self.video_filter = video_filter
        self.lower_bound = [0, 0, 0]
        self.upper_bound = [255, 255, 255]

        self.build_ui()
        self.update_frame()

    def build_ui(self):
        self.root.title("Filtro de Color con OpenCV y Tkinter")

        self.frame_controls = ttk.Frame(self.root)
        self.frame_controls.pack(side=tk.LEFT, padx=10, pady=10)

        self.frame_video = ttk.Frame(self.root)
        self.frame_video.pack(side=tk.RIGHT, padx=10, pady=10)

        self.sliders = {}
        for color in ('R', 'G', 'B'):
            low = tk.Scale(self.frame_controls, from_=0, to=255, label=f"Low {color}",
                           orient=tk.HORIZONTAL, command=self.update_bounds)
            high = tk.Scale(self.frame_controls, from_=0, to=255, label=f"High {color}",
                            orient=tk.HORIZONTAL, command=self.update_bounds)
            low.pack()
            high.pack()
            self.sliders[f'low_{color}'] = low
            self.sliders[f'high_{color}'] = high

        self.label_video = tk.Label(self.frame_video)
        self.label_video.pack()

    def update_bounds(self, _=None):
        self.lower_bound = [self.sliders[f'low_{c}'].get() for c in ('R', 'G', 'B')]
        self.upper_bound = [self.sliders[f'high_{c}'].get() for c in ('R', 'G', 'B')]
        self.video_filter.set_bounds(self.lower_bound, self.upper_bound)

    def update_frame(self):
        frame = self.video_filter.get_filtered_frame()
        if frame is not None:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label_video.imgtk = imgtk
            self.label_video.configure(image=imgtk)

        self.root.after(10, self.update_frame)

# UI Wxpython class 
class ZZZUI(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        
        # Inicializar datos para múltiples personajes
        self.personajes_data = {}
        for i in range(1, 10):  # 9 personajes
            self.personajes_data[f"Personaje {i}"] = {}
            for j in range(1, 7):  # 6 discos por personaje
                self.personajes_data[f"Personaje {i}"][f"Disco {j}"] = None  # Inicialmente vacío
        
        # Configuración de la ventana
        self.SetTitle("Gestor de Discos - Reemplazo de Duplicados")
        self.SetMinSize((650, 600))
        
        # Panel principal
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Sizer principal
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Fuentes personalizadas
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        
        # Título
        title = wx.StaticText(panel, label="Gestión de Discos (Reemplaza Duplicados)")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(70, 70, 70))
        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        # Línea divisoria
        main_sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Sizer para controles
        grid = wx.FlexGridSizer(rows=7, cols=2, vgap=10, hgap=10)
        grid.AddGrowableCol(1, 1)
        
        # Selección de personaje
        personaje_label = wx.StaticText(panel, label="Personaje:")
        personaje_label.SetFont(label_font)
        grid.Add(personaje_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        
        self.selected_personaje = wx.Choice(panel, choices=list(self.personajes_data.keys()))
        self.selected_personaje.SetSelection(0)
        self.selected_personaje.SetBackgroundColour(wx.WHITE)
        self.selected_personaje.Bind(wx.EVT_CHOICE, self.on_personaje_change)
        grid.Add(self.selected_personaje, 0, wx.EXPAND)
        
        # Selección de disco
        disco_label = wx.StaticText(panel, label="Disco:")
        disco_label.SetFont(label_font)
        grid.Add(disco_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        
        self.selected_disco = wx.Choice(panel, choices=[])
        self.selected_disco.SetBackgroundColour(wx.WHITE)
        self.update_discos_choices()
        grid.Add(self.selected_disco, 0, wx.EXPAND)
        
        # Main stat
        main_stat_label = wx.StaticText(panel, label="Main Stat:")
        main_stat_label.SetFont(label_font)
        grid.Add(main_stat_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        
        self.main_stat_var = wx.Choice(panel, choices=["15", "12", "9", "6", "3", "0"])
        self.main_stat_var.SetSelection(0)
        self.main_stat_var.SetBackgroundColour(wx.WHITE)
        grid.Add(self.main_stat_var, 0, wx.EXPAND)
        
        # Sub stat
        sub_stat_label = wx.StaticText(panel, label="Sub Stat (0-4):")
        sub_stat_label.SetFont(label_font)
        grid.Add(sub_stat_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        
        self.entry_sub_stat = wx.SpinCtrl(panel, min=0, max=4)
        self.entry_sub_stat.SetValue(0)
        grid.Add(self.entry_sub_stat, 0, wx.EXPAND)
        
        # 4 stats
        four_stats_label = wx.StaticText(panel, label="4 Stats (0-1):")
        four_stats_label.SetFont(label_font)
        grid.Add(four_stats_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        
        self.entry_four_stats = wx.SpinCtrl(panel, min=0, max=1)
        self.entry_four_stats.SetValue(0)
        grid.Add(self.entry_four_stats, 0, wx.EXPAND)
        
        # Sub stat subida
        subida_label = wx.StaticText(panel, label="Sub Stat Subida (0-5):")
        subida_label.SetFont(label_font)
        grid.Add(subida_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        
        self.entry_subida = wx.SpinCtrl(panel, min=0, max=5)
        self.entry_subida.SetValue(0)
        grid.Add(self.entry_subida, 0, wx.EXPAND)
        
        # Agregar grid al sizer principal
        main_sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 20)
        
        # Botones
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Botón Guardar/Reemplazar
        guardar_btn = wx.Button(panel, label="Guardar/Reemplazar")
        guardar_btn.SetBackgroundColour(wx.Colour(100, 200, 100))
        guardar_btn.SetForegroundColour(wx.WHITE)
        guardar_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        guardar_btn.Bind(wx.EVT_BUTTON, self.guardar_o_reemplazar)
        btn_sizer.Add(guardar_btn, 0, wx.RIGHT, 10)
        
        # Botón Limpiar
        limpiar_btn = wx.Button(panel, label="Limpiar Campos")
        limpiar_btn.SetBackgroundColour(wx.Colour(200, 200, 100))
        limpiar_btn.SetForegroundColour(wx.WHITE)
        limpiar_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        limpiar_btn.Bind(wx.EVT_BUTTON, self.limpiar_campos)
        btn_sizer.Add(limpiar_btn, 0, wx.RIGHT, 10)
        
        main_sizer.Add(btn_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 20)
        
        # ListCtrl (Tabla)
        self.tree = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.LC_SINGLE_SEL)
        self.tree.SetBackgroundColour(wx.Colour(250, 250, 250))
        self.tree.InsertColumn(0, "Personaje", width=120)
        self.tree.InsertColumn(1, "Disco", width=120)
        self.tree.InsertColumn(2, "Puntos", width=100)
        self.tree.InsertColumn(3, "Estado", width=120)
        
        # Configurar encabezados
        header_attr = wx.ItemAttr()
        header_attr.SetBackgroundColour(wx.Colour(80, 80, 80))
        header_attr.SetTextColour(wx.WHITE)
        header_attr.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        for i in range(self.tree.GetColumnCount()):
            self.tree.SetHeaderAttr(header_attr)
        
        main_sizer.Add(self.tree, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        
        # Actualizar tabla inicial
        self.actualizar_tabla()
        
        panel.SetSizer(main_sizer)
        self.Centre()
        self.Show()
    
    def update_discos_choices(self):
        personaje = self.selected_personaje.GetStringSelection()
        if personaje:
            discos = list(self.personajes_data[personaje].keys())
            self.selected_disco.SetItems(discos)
            if discos:
                self.selected_disco.SetSelection(0)
    
    def on_personaje_change(self, event):
        self.update_discos_choices()
        self.actualizar_tabla()
    
    def calcular(self):
        try:
            main_stat_val = int(self.main_stat_var.GetStringSelection())
            main_stat_puntos = main_stat_val * 10 / 15
            
            sub_stat = self.entry_sub_stat.GetValue()
            four_stats = self.entry_four_stats.GetValue()
            sub_stat_subida = self.entry_subida.GetValue()
            
            total = main_stat_puntos + sub_stat + four_stats + sub_stat_subida
            return round(total, 2)
        except ValueError:
            wx.MessageBox("Por favor ingresa valores numéricos válidos.", "Error", wx.OK | wx.ICON_ERROR)
            return 0
    
    def guardar_o_reemplazar(self, event):
        personaje = self.selected_personaje.GetStringSelection()
        disco = self.selected_disco.GetStringSelection()
        puntos = self.calcular()
        
        if puntos <= 0 or not personaje or not disco:
            return
        
        # Verificar si ya existe un disco con este nombre
        disco_existente = self.personajes_data[personaje][disco] is not None
        
        
        # Guardar/reemplazar los datos
        self.personajes_data[personaje][disco] = puntos
        self.actualizar_tabla()
    
        
        # Limpiar campos
        self.limpiar_campos()
    
    def limpiar_campos(self, event=None):
        self.entry_sub_stat.SetValue(0)
        self.entry_four_stats.SetValue(0)
        self.entry_subida.SetValue(0)
        self.main_stat_var.SetSelection(0)
    
    def actualizar_tabla(self):
        self.tree.DeleteAllItems()
        personaje_actual = self.selected_personaje.GetStringSelection()
        
        if personaje_actual:
            for disco, puntos in self.personajes_data[personaje_actual].items():
                if puntos is not None:  # Solo mostrar discos con datos
                    index = self.tree.InsertItem(self.tree.GetItemCount(), personaje_actual)
                    self.tree.SetItem(index, 1, disco)
                    self.tree.SetItem(index, 2, f"{puntos:.2f}")
                    
                    estado = "Existente" if self.personajes_data[personaje_actual][disco] is not None else "Nuevo"
                    self.tree.SetItem(index, 3, estado)
                    
                    color = self.get_color(puntos)
                    self.tree.SetItemBackgroundColour(index, color)
    
    def get_color(self, puntos):
        if puntos >= 16:
            return wx.Colour(100, 200, 100)  # Verde
        elif puntos >= 13:
            return wx.Colour(150, 220, 150)  # Verde claro
        elif puntos >= 10:
            return wx.Colour(255, 255, 150)  # Amarillo
        elif puntos >= 8:
            return wx.Colour(255, 200, 100)  # Naranja
        else:
            return wx.Colour(255, 150, 150)  # Rojo

class MyZZZApp(wx.Frame):
    #  ventana = ZZZUI(None, title="Gestión de Discos", size=(600, 400))
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        panel = wx.Panel(self)
        grid = wx.GridBagSizer(5,5)

        # pos 0 
        wx.StaticText(panel, label="Selecciona Disco:", pos=(0,0)).SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        
        # pos 1
        guardar_btn = wx.Button(panel, label="Guardar")
        guardar_btn.Bind(wx.EVT_BUTTON, self.guardar)
        grid.Add(guardar_btn, pos=(1, 0), flag=wx.TOP, border=10) # posición (row, col)

        panel.SetSizer(grid)
        self.Centre()
        self.Show()

    def guardar(self, event):
        print("Datos guardados")