# main.py
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty, DictProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import webbrowser # Linkleri açmak için

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, OneLineIconListItem, IconLeftWidget
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton, MDFillRoundFlatIconButton, MDIconButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

from calculator_logic import CalculatorLogic
from converter_logic import UnitConverterLogic 

AVAILABLE_PALETTES = sorted([
    "Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue", "LightBlue",
    "Cyan", "Teal", "Green", "LightGreen", "Lime", "Yellow", "Amber",
    "Orange", "DeepOrange", "Brown", "Gray", "BlueGray"
])

class ThemeDialogContent(MDBoxLayout): pass
class SettingsContent(MDBoxLayout): pass
class HistoryDialogContent(MDBoxLayout): pass 

class AdvancedCalculatorApp(MDApp):
    title = "Modern Hesap Makinesi"
    calculator_logic = ObjectProperty(None)
    converter_logic = ObjectProperty(None)

    theme_dialog = ObjectProperty(None)
    settings_dialog = ObjectProperty(None)
    history_dialog = ObjectProperty(None) 

    special_button_color_map = DictProperty({
        "C": "#E53935", "AC": "#D32F2F",
        "DEL": "#FF8F00",
        "MODE": "#42A5F5", 
        "%": "#64B5F6", 
        "2nd": "#FFC107", 
        "DEG": "#4CAF50", "RAD":"#4CAF50" 
    })

    calculator_mode = StringProperty("simple")
    display_font_size = StringProperty("42sp")

    current_category_name = StringProperty("")
    current_from_unit = StringProperty("")
    current_to_unit = StringProperty("")
    category_menu = ObjectProperty(None)
    unit_menus = DictProperty({'from': None, 'to': None})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calculator_logic = CalculatorLogic()
        self.converter_logic = UnitConverterLogic()

    def build(self):
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = "Dark" 
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Amber"
        return Builder.load_file('calculator_ui.kv')

    def on_start(self):
        Clock.schedule_once(self._on_start_setup, 0.1)

    def _on_start_setup(self, *args):
        if self.root and hasattr(self.root, 'ids') and 'bottom_nav' in self.root.ids:
            self.root.ids.bottom_nav.switch_tab('calculator_tab')
        
        self.update_calculator_buttons()
        self.update_display()
        self.update_mode_label()
        self.update_deg_rad_button_text()
        self.update_ui_text_colors() # Hem hesap makinesi hem de dönüştürücü için renkleri günceller

    def adjust_display_font_size(self, instance):
        text_len = len(instance.text)
        font_size_map = {
            (0, 9): "42sp", (10, 14): "36sp", (15, 19): "30sp",
            (20, 24): "24sp"
        }
        new_font_size = "20sp" 
        for (min_len, max_len), size_sp in font_size_map.items():
            if min_len <= text_len <= max_len:
                new_font_size = size_sp
                break
        instance.font_size = new_font_size

    def update_ui_text_colors(self):
        """Temaya göre hem hesap makinesi ekranının hem de dönüştürücü sonucunun metin rengini günceller."""
        if self.theme_cls.theme_style == "Light":
            text_color = get_color_from_hex("#000000") # Açık tema için siyah
        else:
            text_color = get_color_from_hex("#FFFFFF") # Koyu tema için beyaz

        # Hesap makinesi ekranı
        if self.root and hasattr(self.root, 'ids') and 'display' in self.root.ids:
            display_widget = self.root.ids.display
            display_widget.text_color_normal = text_color
            display_widget.text_color_focus = text_color
        
        # Dönüştürücü sonuç alanı
        if self.root and hasattr(self.root, 'ids') and 'conversion_result' in self.root.ids:
            conversion_result_widget = self.root.ids.conversion_result
            conversion_result_widget.color = text_color # MDLabel için 'color' özelliği

    def toggle_theme_style(self):
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        self.update_ui_text_colors() 

    def change_palette(self, palette_name, palette_type="primary"):
        if palette_type == "primary":
            self.theme_cls.primary_palette = palette_name
        elif palette_type == "accent":
            self.theme_cls.accent_palette = palette_name
        if self.theme_dialog: self.theme_dialog.dismiss()
        self.update_ui_text_colors() # Palet değişince de renkleri güncellemek iyi olabilir

    def open_settings_dialog(self, *args):
        if not self.settings_dialog:
             self.settings_dialog = MDDialog(
                title="Uygulama Ayarları", type="custom", content_cls=SettingsContent(),
                buttons=[MDRaisedButton(text="KAPAT", on_release=lambda x: self.settings_dialog.dismiss())])
        self.settings_dialog.open()

    def open_link(self, url):
        """Verilen URL'yi varsayılan web tarayıcısında açar."""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Link açılamadı: {url}, Hata: {e}")
            Snackbar(text=f"Link açılamadı: {e}").open()

    def open_theme_picker_dialog(self, *args):
        # ... (Bu metod değişmedi) ...
        if not self.theme_dialog:
            dialog_content = ThemeDialogContent()
            for p_name in AVAILABLE_PALETTES:
                primary_item = OneLineIconListItem(text=p_name)
                primary_item.add_widget(IconLeftWidget(icon="palette"))
                primary_item.bind(on_release=lambda instance, p=p_name: self.change_palette(p, "primary"))
                dialog_content.ids.primary_palette_list.add_widget(primary_item)

                accent_item = OneLineIconListItem(text=p_name)
                accent_item.add_widget(IconLeftWidget(icon="format-paint"))
                accent_item.bind(on_release=lambda instance, p=p_name: self.change_palette(p, "accent"))
                dialog_content.ids.accent_palette_list.add_widget(accent_item)
            
            self.theme_dialog = MDDialog(
                title="Tema Seçimi", type="custom", content_cls=dialog_content,
                buttons=[MDRaisedButton(text="KAPAT", on_release=lambda x: self.theme_dialog.dismiss())])
        
        self.theme_dialog.open()


    def clear_history_and_update(self):
        # ... (Bu metod değişmedi) ...
        self.calculator_logic.history = []
        if self.history_dialog and self.history_dialog.content_cls:
            dialog_list = self.history_dialog.content_cls.ids.get('dialog_history_list')
            if dialog_list:
                dialog_list.clear_widgets()
                list_item = OneLineListItem(
                    text="Geçmiş kaydı bulunmamaktadır.", 
                    theme_text_color="Secondary",
                    font_style="Caption"
                )
                dialog_list.add_widget(list_item)
        
        if self.settings_dialog: self.settings_dialog.dismiss()
        
        snackbar = Snackbar() 
        snackbar.text = "Geçmiş temizlendi." 
        snackbar.open()

    def update_display(self, text=None):
        # ... (Bu metod değişmedi) ...
        if self.root and hasattr(self.root, 'ids') and 'display' in self.root.ids:
            if text is not None: self.root.ids.display.text = text
            else:
                current_display_text = self.calculator_logic.get_current_expression_display()
                self.root.ids.display.text = current_display_text if current_display_text else "0"


    def open_history_dialog(self, *args): 
        # ... (Bu metod değişmedi) ...
        if not self.history_dialog:
            self.history_dialog = MDDialog(
                type="custom",
                content_cls=HistoryDialogContent(), 
                buttons=[
                    MDRaisedButton(text="KAPAT", on_release=lambda x: self.history_dialog.dismiss())
                ]
            )
        
        history_list_widget = self.history_dialog.content_cls.ids.get('dialog_history_list')
        if not history_list_widget:
            print("HATA: dialog_history_list, HistoryDialogContent içinde bulunamadı!")
            if self.history_dialog: self.history_dialog.dismiss()
            Snackbar(text="Geçmiş görüntülenirken bir sorun oluştu.").open()
            return

        history_list_widget.clear_widgets()
        
        if not self.calculator_logic.history:
            list_item = OneLineListItem(
                text="Geçmiş kaydı bulunmamaktadır.", 
                theme_text_color="Secondary", 
                font_style="Caption"
            )
            history_list_widget.add_widget(list_item)
        else:
            for internal_expr, display_expr, result_str in reversed(self.calculator_logic.history):
                item_text = f"{display_expr} = {result_str}"
                list_item = OneLineListItem(
                    text=item_text, 
                    theme_text_color="Secondary", 
                    font_style="Caption"
                )
                list_item.bind(on_release=lambda instance, expr_to_load=internal_expr: self.load_expression_from_history(expr_to_load))
                history_list_widget.add_widget(list_item)

        self.history_dialog.open()

    def load_expression_from_history(self, expression_to_load):
        # ... (Bu metod değişmedi) ...
        self.calculator_logic.current_expression = expression_to_load 
        self.update_display() 
        if self.history_dialog:
            self.history_dialog.dismiss() 
        
        if self.root and self.root.ids and 'bottom_nav' in self.root.ids:
            try:
                self.root.ids.bottom_nav.switch_tab('calculator_tab')
            except Exception as e:
                print(f"Hesap makinesi sekmesine geçilemedi: {e}")
                Snackbar(text="Hesap makinesi sekmesine geçilemedi.").open()
        else:
            print("HATA: bottom_nav widget'ı bulunamadı.")
            Snackbar(text="Navigasyon hatası.").open()

        snackbar = Snackbar()
        snackbar.text = "İfade hesap makinesine yüklendi."
        snackbar.open()

    def on_calc_button_press(self, button_value):
        # ... (Bu metod değişmedi) ...
        if button_value == "MODE": self.toggle_calculator_mode()
        elif button_value == "2nd": self.toggle_second_function_mode_and_update_ui()
        elif button_value.isdigit() or button_value == ".": self.calculator_logic.input_digit(button_value)
        elif button_value in ["+", "-", "*", "/", "^", "%"]: 
            self.calculator_logic.input_operator(button_value)
        elif button_value in [
            "sin", "cos", "tan", "log", "ln", "sqrt", "pi", "e", 
            "(", ")", "1/x", "x!", "percentage", "mod", "pow" 
        ]:
            self.calculator_logic.input_function(button_value)
        self.update_display()

    def on_clear_all(self, *args):
        # ... (Bu metod değişmedi) ...
        self.calculator_logic.clear_all() 
        self.update_display()
        self.update_calculator_buttons() 

    def on_clear_entry(self, *args):
        # ... (Bu metod değişmedi) ...
        self.calculator_logic.clear_entry()
        self.update_display()

    def on_delete(self, *args):
        # ... (Bu metod değişmedi) ...
        self.calculator_logic.delete_last()
        self.update_display()

    def on_calculate(self, *args):
        # ... (Bu metod değişmedi) ...
        result = self.calculator_logic.calculate()
        self.update_display(text=result)


    def toggle_calculator_mode(self):
        # ... (Bu metod değişmedi) ...
        self.calculator_mode = "advanced" if self.calculator_mode == "simple" else "simple"
        self.calculator_logic.second_function_active = False 
        self.update_calculator_buttons()
        self.update_mode_label()


    def toggle_second_function_mode_and_update_ui(self):
        # ... (Bu metod değişmedi) ...
        self.calculator_logic.toggle_second_function_mode()
        self.update_calculator_buttons() 


    def update_mode_label(self):
        # ... (Bu metod değişmedi) ...
        if self.root and hasattr(self.root, 'ids') and 'current_mode_label' in self.root.ids:
             self.root.ids.current_mode_label.text = f"Mod: {'Gelişmiş' if self.calculator_mode == 'advanced' else 'Basit'}"


    def toggle_deg_rad_mode(self):
        # ... (Bu metod değişmedi) ...
        mode_text = self.calculator_logic.toggle_degree_mode()
        self.update_deg_rad_button_text()
        snackbar = Snackbar()
        snackbar.text = f"Mod: {mode_text}"
        snackbar.open()


    def update_deg_rad_button_text(self):
        # ... (Bu metod değişmedi) ...
        if self.root and hasattr(self.root, 'ids') and 'deg_rad_toggle' in self.root.ids:
            btn = self.root.ids.deg_rad_toggle
            if self.calculator_logic.degree_mode:
                btn.icon = "alpha-d-box"
                btn.tooltip_text = "Derece Modu (RAD'a geç)"
            else:
                btn.icon = "alpha-r-box"
                btn.tooltip_text = "Radyan Modu (DEG'e geç)"

    def _get_button_text_for_2nd_mode(self, primary_text, second_text):
        # ... (Bu metod değişmedi) ...
        return second_text if self.calculator_logic.second_function_active else primary_text


    def update_calculator_buttons(self):
        # ... (Bu metod değişmedi, buton yerleşimi önceki gibi) ...
        if not (self.root and hasattr(self.root, 'ids') and 'button_grid' in self.root.ids):
            return
            
        grid = self.root.ids.button_grid
        grid.clear_widgets()
        
        if self.calculator_mode == "simple":
            grid.cols = 4
            buttons_def = [
                ("AC", "SpecialButton", self.on_clear_all), 
                ("DEL", "SpecialButton", self.on_delete),
                ("%", "SpecialButton", "percentage"), 
                ("/", "OperatorButton", "/"),
                
                ("7", "NumberButton", "7"), ("8", "NumberButton", "8"),
                ("9", "NumberButton", "9"), ("*", "OperatorButton", "*"),
                
                ("4", "NumberButton", "4"), ("5", "NumberButton", "5"),
                ("6", "NumberButton", "6"), ("-", "OperatorButton", "-"),
                
                ("1", "NumberButton", "1"), ("2", "NumberButton", "2"),
                ("3", "NumberButton", "3"), ("+", "OperatorButton", "+"),

                ("MODE", "SpecialButton", "MODE"), 
                ("0", "NumberButton", "0"), 
                (".", "NumberButton", "."), 
                ("=", "EqualsButton", self.on_calculate)
            ]
        else: 
            grid.cols = 5
            buttons_def = [
                # Satır 1
                (self._get_button_text_for_2nd_mode("sin", "sin^-1"), "FunctionButton", "sin"), 
                (self._get_button_text_for_2nd_mode("cos", "cos^-1"), "FunctionButton", "cos"),
                (self._get_button_text_for_2nd_mode("tan", "tan^-1"), "FunctionButton", "tan"),
                (self._get_button_text_for_2nd_mode("log", "10^x"), "FunctionButton", "log"), 
                ("C", "SpecialButton", self.on_clear_entry),
                # Satır 2
                (self._get_button_text_for_2nd_mode("ln", "eˣ"), "FunctionButton", "ln"),   
                (self._get_button_text_for_2nd_mode("√", "x²"), "FunctionButton", "sqrt"), 
                ("mod", "OperatorButton", "mod"), 
                ("x!", "FunctionButton", "x!"),
                ("DEL", "SpecialButton", self.on_delete),
                # Satır 3
                ("π", "FunctionButton", "pi"), 
                ("e", "FunctionButton", "e"), 
                ("1/x", "FunctionButton", "1/x"), 
                ("%", "FunctionButton", "percentage"), 
                ("2nd", "SpecialButton", "2nd"), 
                # Satır 4
                ("7", "NumberButton", "7"), ("8", "NumberButton", "8"), ("9", "NumberButton", "9"),
                ("(", "OperatorButton", "("), (")", "OperatorButton", ")"),
                # Satır 5
                ("4", "NumberButton", "4"), ("5", "NumberButton", "5"), ("6", "NumberButton", "6"),
                ("*", "OperatorButton", "*"), ("/","OperatorButton", "/"),
                # Satır 6
                ("1", "NumberButton", "1"), ("2", "NumberButton", "2"), ("3", "NumberButton", "3"),
                ("+", "OperatorButton", "+"), 
                ("-", "OperatorButton", "-"), 
                # Satır 7
                ("MODE", "SpecialButton", "MODE"), 
                ("0", "NumberButton", "0"), 
                (".", "NumberButton", "."),
                ("=", "EqualsButton", self.on_calculate),
                ("x^y", "FunctionButton", "pow"), 
            ]

        for item_def in buttons_def:
            text, btn_type_str, action_val = item_def[0], item_def[1], item_def[2]
            
            btn_kwargs = {"text": text}
            if text == "2nd": 
                if self.calculator_logic.second_function_active:
                    btn_kwargs["md_bg_color"] = self.theme_cls.accent_color 
                else:
                    btn_kwargs["md_bg_color"] = get_color_from_hex(self.special_button_color_map.get("2nd", "#FFC107"))

            if btn_type_str == "NumberButton": btn = NumberButton(**btn_kwargs)
            elif btn_type_str == "OperatorButton": btn = OperatorButton(**btn_kwargs)
            elif btn_type_str == "FunctionButton": btn = FunctionButton(**btn_kwargs)
            elif btn_type_str == "SpecialButton": btn = SpecialButton(**btn_kwargs)
            elif btn_type_str == "EqualsButton": btn = EqualsButton(**btn_kwargs)
            else: continue

            if callable(action_val): btn.bind(on_release=action_val)
            else: btn.bind(on_release=lambda instance, val=action_val: self.on_calc_button_press(val))
            grid.add_widget(btn)


    def on_tab_switch(self, instance_bottom_navigation, current_tab_widget, *args):
        if not (self.root and hasattr(self.root, 'ids') and 'top_app_bar' in self.root.ids): return
        tab_text = current_tab_widget.text 
        self.root.ids.top_app_bar.title = tab_text
        
        self.update_ui_text_colors() # Sekme değiştiğinde de renkleri güncelle

        if current_tab_widget.name == 'converter_tab': # Veya tab_text == "Dönüştür"
            if not self.category_menu:
                self.init_converter_dropdowns()
    
    # ... (converter ile ilgili diğer metodlar değişmedi) ...
    def init_converter_dropdowns(self):
        if not (self.root and hasattr(self.root, 'ids') and 'category_dropdown_item' in self.root.ids): return
        cat_items = []
        for cat_name in self.converter_logic.categories.keys():
            cat_items.append({"viewclass": "OneLineListItem", "text": cat_name, "height": dp(48),
                              "on_release": lambda x=cat_name, caller=self.root.ids.category_dropdown_item: self.select_category(x, caller)})
        self.category_menu = MDDropdownMenu(caller=self.root.ids.category_dropdown_item, items=cat_items, width_mult=3, max_height=dp(250))

    def open_category_menu(self, caller):
        if not self.category_menu: self.init_converter_dropdowns()
        if self.category_menu : self.category_menu.open()

    def select_category(self, category_name, caller_widget):
        self.current_category_name = category_name
        caller_widget.set_item(category_name)
        if self.category_menu: self.category_menu.dismiss()

        if self.root and hasattr(self.root, 'ids'):
            self.update_unit_dropdowns('from', self.root.ids.from_unit_dropdown_item)
            self.update_unit_dropdowns('to', self.root.ids.to_unit_dropdown_item)

            self.root.ids.from_unit_dropdown_item.disabled = False
            self.root.ids.to_unit_dropdown_item.disabled = False
            if 'input_value' in self.root.ids: self.root.ids.input_value.text = ""
            if 'conversion_result' in self.root.ids: self.root.ids.conversion_result.text = ""

    def update_unit_dropdowns(self, unit_type, caller_widget):
        units = self.converter_logic.get_units_for_category(self.current_category_name)
        if not units:
            caller_widget.set_item("Birim Yok")
            caller_widget.disabled = True
            if self.unit_menus.get(unit_type): self.unit_menus[unit_type].dismiss()
            self.unit_menus[unit_type] = None
            return

        caller_widget.disabled = False
        unit_items = []
        for unit_name in units:
            unit_items.append({"viewclass": "OneLineListItem", "text": unit_name, "height": dp(48),
                               "on_release": lambda x=unit_name, ut=unit_type, cw=caller_widget: self.select_unit(x, ut, cw)})

        if self.unit_menus.get(unit_type): self.unit_menus[unit_type].dismiss()
        self.unit_menus[unit_type] = MDDropdownMenu(caller=caller_widget, items=unit_items, width_mult=3.5, max_height=dp(280))

        if units:
            default_from_unit = units[0]
            default_to_unit = units[0]
            if len(units) > 1:
                if units[0] != units[1]: default_to_unit = units[1]
                elif len(units) > 2 and units[0] != units[2]: default_to_unit = units[2]


            if unit_type == 'from':
                caller_widget.set_item(default_from_unit)
                self.current_from_unit = default_from_unit
            elif unit_type == 'to':
                caller_widget.set_item(default_to_unit)
                self.current_to_unit = default_to_unit

    def open_unit_menu(self, unit_type, caller_widget):
        if not self.unit_menus.get(unit_type):
            self.update_unit_dropdowns(unit_type, caller_widget)
        if self.unit_menus.get(unit_type):
            self.unit_menus[unit_type].open()

    def select_unit(self, unit_name, unit_type, caller_widget):
        caller_widget.set_item(unit_name)
        if unit_type == 'from': self.current_from_unit = unit_name
        elif unit_type == 'to': self.current_to_unit = unit_name
        if self.unit_menus.get(unit_type): self.unit_menus[unit_type].dismiss()
        self.perform_conversion_if_possible()

    def swap_units(self):
        if not self.current_from_unit or not self.current_to_unit: return
        temp_from_unit, temp_to_unit = self.current_from_unit, self.current_to_unit
        from_caller, to_caller = self.root.ids.from_unit_dropdown_item, self.root.ids.to_unit_dropdown_item
        
        self.current_from_unit = temp_to_unit
        self.current_to_unit = temp_from_unit
        from_caller.set_item(self.current_from_unit)
        to_caller.set_item(self.current_to_unit)
        self.perform_conversion_if_possible()

    def perform_conversion_if_possible(self):
        if self.root and hasattr(self.root, 'ids') and 'input_value' in self.root.ids:
            if self.root.ids.input_value.text and self.current_category_name and self.current_from_unit and self.current_to_unit:
                self.perform_conversion()

    def perform_conversion(self):
        ids = self.root.ids if self.root and hasattr(self.root, 'ids') else None
        if not (ids and 'input_value' in ids and 'conversion_result' in ids and 'converter_spinner' in ids):
            return

        input_val = ids.input_value.text.strip()
        if not input_val: 
            ids.conversion_result.text = ""
            return
        if not (self.current_category_name and self.current_from_unit and self.current_to_unit):
            snackbar = Snackbar()
            snackbar.text = "Lütfen kategori ve birimleri seçin."
            snackbar.open()
            return

        ids.converter_spinner.active = True 
        # Dönüşüm yapılmadan önce sonuç rengini güncelleyelim
        self.update_ui_text_colors() 
        Clock.schedule_once(self._do_conversion_callback, 0.01) 

    def _do_conversion_callback(self, *args):
        ids = self.root.ids if self.root and hasattr(self.root, 'ids') else None
        if not (ids and 'input_value' in ids and 'conversion_result' in ids and 'converter_spinner' in ids):
            if ids and 'converter_spinner' in ids : ids.converter_spinner.active = False
            return
            
        input_val = ids.input_value.text.strip()
        result = self.converter_logic.convert(input_val, self.current_from_unit, self.current_to_unit, self.current_category_name)
        ids.conversion_result.text = str(result)
        ids.converter_spinner.active = False


class CalcButton(MDFillRoundFlatButton): pass
class NumberButton(CalcButton): pass
class OperatorButton(CalcButton): pass
class FunctionButton(CalcButton): pass
class SpecialButton(CalcButton): pass
class EqualsButton(CalcButton): pass

if __name__ == '__main__':
    AdvancedCalculatorApp().run()