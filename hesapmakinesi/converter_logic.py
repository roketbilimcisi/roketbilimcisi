# --- START OF FILE converter_logic.py ---
# converter_logic.py
import math

class UnitConverterLogic:
    def __init__(self):
        self.categories = {
            "Uzunluk": {
                "Kilometre (km)": 1000, "Metre (m)": 1, "Santimetre (cm)": 0.01, "Milimetre (mm)": 0.001,
                "Mil (mi)": 1609.34, "Yard (yd)": 0.9144, "Fit (ft)": 0.3048, "İnç (in)": 0.0254,
            },
            "Kütle": {
                "Kilogram (kg)": 1, "Gram (g)": 0.001, "Miligram (mg)": 0.000001, "Ton (t)": 1000,
                "Pound (lbs)": 0.453592, "Ons (oz)": 0.0283495,
            },
            "Sıcaklık": ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"], # Özel işlem
            "Veri": { # 1024 tabanlı
                "Bayt (B)": 1, "Kilobayt (KB)": 1024, "Megabayt (MB)": 1024**2,
                "Gigabayt (GB)": 1024**3, "Terabayt (TB)": 1024**4, "Petabayt (PB)": 1024**5,
            },
            "Hacim": {
                "Litre (L)": 1, "Mililitre (mL)": 0.001, "Metreküp (m³)": 1000, "Santimetreküp (cm³)": 0.001,
                "Galon (US sıvı)": 3.78541, "Quart (US sıvı)": 0.946353, "Pint (US sıvı)": 0.473176,
                "Fluid Ounce (US)": 0.0295735,
            },
            "Alan": {
                "Metrekare (m²)": 1, "Kilometrekare (km²)": 10**6, "Hektar (ha)": 10**4,
                "Santimetrekare (cm²)": 10**-4, "Acre (ac)": 4046.86, "Square Mile (mi²)": 2.59 * (10**6),
            },
            "Hız": {
                "Metre/saniye (m/s)": 1, "Kilometre/saat (km/h)": 1/3.6,
                "Mil/saat (mph)": 0.44704, "Knot (kn)": 0.514444,
            },
            "Sayı Sistemi": ["Decimal", "Binary", "Octal", "Hexadecimal"], # Özel işlem
        }

    def get_units_for_category(self, category_name):
        category_data = self.categories.get(category_name)
        if isinstance(category_data, dict):
            return list(category_data.keys())
        elif isinstance(category_data, list): # Sıcaklık, Sayı Sistemi
            return category_data
        return []

    def convert(self, value_str, from_unit_name, to_unit_name, category_name):
        category_data = self.categories.get(category_name)
        if not category_data: return "Kategori Hatası"

        # Sayı Sistemi Dönüşümü
        if category_name == "Sayı Sistemi":
            try:
                # Gelen değerin string olduğundan emin olalım, özellikle kopyala-yapıştır ile gelebilir
                value_str_processed = str(value_str).strip()
                if not value_str_processed: return "Geçersiz Sayı Formatı"


                if from_unit_name == "Decimal": val = int(value_str_processed)
                elif from_unit_name == "Binary": val = int(value_str_processed, 2)
                elif from_unit_name == "Octal": val = int(value_str_processed, 8)
                elif from_unit_name == "Hexadecimal": val = int(value_str_processed, 16)
                else: return "Bilinmeyen Kaynak Sistem"

                if to_unit_name == "Decimal": result = str(val)
                elif to_unit_name == "Binary": result = bin(val)[2:]
                elif to_unit_name == "Octal": result = oct(val)[2:]
                elif to_unit_name == "Hexadecimal": result = hex(val)[2:].upper()
                else: return "Bilinmeyen Hedef Sistem"
                return result
            except ValueError:
                return "Geçersiz Sayı Formatı"
            except Exception as e:
                return f"Sistem Hata: {e}"

        # Diğer kategoriler için değerin float olması beklenir
        try:
            # Türkçe klavyelerde virgül kullanılabileceği için replace ekleyelim
            value_str_processed = str(value_str).strip().replace(',', '.')
            if not value_str_processed: return "Geçersiz Değer"
            value = float(value_str_processed)
        except ValueError:
            return "Geçersiz Değer"

        # Sıcaklık Dönüşümü
        if category_name == "Sıcaklık":
            if from_unit_name == to_unit_name: result = value
            elif from_unit_name == "Celsius (°C)":
                if to_unit_name == "Fahrenheit (°F)": result = (value * 9/5) + 32
                elif to_unit_name == "Kelvin (K)": result = value + 273.15
                else: return "Bilinmeyen Birim"
            elif from_unit_name == "Fahrenheit (°F)":
                c = (value - 32) * 5/9
                if to_unit_name == "Celsius (°C)": result = c
                elif to_unit_name == "Kelvin (K)": result = c + 273.15
                else: return "Bilinmeyen Birim"
            elif from_unit_name == "Kelvin (K)":
                c = value - 273.15
                if to_unit_name == "Celsius (°C)": result = c
                elif to_unit_name == "Fahrenheit (°F)": result = (c * 9/5) + 32
                else: return "Bilinmeyen Birim"
            else: return "Bilinmeyen Birim"
        # Diğer Birimler (Faktör Tabanlı)
        else:
            units_dict = category_data # Bu bir dict olmalı
            if not isinstance(units_dict, dict):
                return "Birim Tanımları Hatalı" # Kategori için birimler dict değilse
            if from_unit_name not in units_dict or to_unit_name not in units_dict:
                return "Bilinmeyen Birim"

            try:
                value_in_base = value * units_dict[from_unit_name]
                result = value_in_base / units_dict[to_unit_name]
            except ZeroDivisionError:
                return "Dönüşüm Faktörü Sıfır Olamaz"
            except Exception as e:
                return f"Dönüşüm Hatası: {e}"


        # Sonuç Formatlama
        if isinstance(result, (int, float)): # Sadece sayısal sonuçları formatla
            if isinstance(result, float):
                if abs(result) < 1e-9 and result != 0: # Çok küçük sayılar için bilimsel gösterim
                    return f"{result:.4e}"
                elif result.is_integer():
                    return str(int(result))
                else: # Ondalıklı ise
                    # Eğer çok fazla ondalık varsa veya çok büyük/küçükse, anlamlı basamaklarla göster
                    if abs(result) > 1e7 or (abs(result) < 1e-4 and result != 0):
                        return f"{result:.6g}" # 6 anlamlı basamak
                    else:
                        # Gereksiz sıfırları ve noktayı temizle
                        formatted_result = f"{result:.6f}"
                        if '.' in formatted_result:
                            formatted_result = formatted_result.rstrip('0').rstrip('.')
                        return formatted_result
            return str(result) # int ise veya formatlanmamışsa
        else: # Eğer result bir string ise (hata mesajı vb.) doğrudan döndür
            return str(result)
# --- END OF FILE converter_logic.py ---