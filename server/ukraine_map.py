from functools import lru_cache
import os
import xml.etree.ElementTree as ET
from cairosvg import svg2png
from PIL import Image
import io

class UkraineMap:
    def __init__(self):
        self._svg = self._load_svg()
        self._regions = self._default_regions()

        self._COLOR_BG       = "#000000"
        self._COLOR_LINES    = "#FFFFFF"

        self._COLOR_NORMAL   = "#B0CACA"   # no alert
        self._COLOR_PARTIAL  = "#F1B181"   # partial alert
        self._COLOR_FULL     = "#BE6055"   # alert in region
        self._COLOR_NODATA   = "#D0CECA"   # no data

        self.set({})
    

    @staticmethod
    def _load_svg() -> ET.ElementTree:
        path = os.path.join(os.path.dirname(__file__), 'ukraine_map.svg')
        tree = ET.parse(path)
        return tree

    
    def _default_regions(self):
        result = {}
    
        for child in self._svg.getroot():
            try:
                name = child.attrib["name"]
                result[name] = None
            except:
                pass

        return result


    ## Update
    def set(self, regions):
        changes_count = 0

        for name in self._regions:
            try:
                oldValue = self._regions[name]
                newValue = regions[name]

                self._regions[name] = newValue
                if newValue != oldValue:
                    changes_count += 1
            except:
                oldValue = self._regions[name]
                self._regions[name] = None
                if oldValue != None:
                    changes_count += 1

        if changes_count > 0:
            self._update_svg()


    def _update_svg(self):
        for name in self._regions:
            value = self._regions[name]
            items = self._svg.findall(f'.//*[@name="{name}"]')

            for item in items:
                if value == "full":
                    item.set("fill", self._COLOR_FULL)
                elif value == "partial":
                    item.set("fill", self._COLOR_PARTIAL)
                elif value == "no_data":
                    item.set("fill", self._COLOR_NODATA)
                else:
                    item.set("fill", self._COLOR_NORMAL)

        root = self._svg.getroot()
        root.set("fill", self._COLOR_NORMAL)
        root.set("stroke", self._COLOR_LINES)
        root.set("stroke-width", "2")
        # pprint(self._svg.getroot().attrib)

        self._generate_image.cache_clear()


    def get_image(self, width: int, height: int, type: str):
        w = self._range_limit(10, 1920, width)
        h = self._range_limit(10, 1920, height)

        image = self._generate_image(width=w, height=h, type=type)
        return image


    def _range_limit(self, min: int, max: int, value: int) -> int:
        if value < min:
            return min
        if value > max:
            return max
        return value


    @lru_cache(maxsize=20)
    def _generate_image(self, width: int, height: int, type: str = "png"):
        root = self._svg.getroot()
        xmlstr = ET.tostring(root, encoding='utf8', method='xml').decode("utf-8")
        
        png_image = svg2png(
            bytestring=xmlstr,
            output_width=width,
            output_height=height,
            background_color=self._COLOR_BG
        )

        if type == 'png':
            return png_image

        if type == 'jpeg':
            image_byte_arr = io.BytesIO()

            image = Image.open(io.BytesIO(png_image))
            image.save(image_byte_arr, format='jpeg')
            return image_byte_arr.getvalue()

        return None

