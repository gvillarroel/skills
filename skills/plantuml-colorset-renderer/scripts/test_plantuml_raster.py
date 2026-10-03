#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0", "resvg-py>=0.5,<0.6"]
# ///
"""Exercise actual PNG delivery from finished SVG without remote rendering."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from render_plantuml_directory import render_source
from arrow_contrast import contrast

SVG='<svg xmlns="http://www.w3.org/2000/svg" width="160" height="140"><polygon points="10,10 150,10 150,90 10,90" fill="#294d19"/><g class="link"><path id="shaft" d="M80 40L80 120" fill="none" stroke="#696969" stroke-width="4"/><polygon points="74,112 80,120 86,112" fill="#696969"/></g></svg>'

class RasterTests(unittest.TestCase):
    def run_formats(self,formats):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
            base=Path(temporary);source=base/'diagram.puml';source.write_text('@startuml\nA --> B\n@enduml')
            calls=[]
            def render(text,fmt,target,*args):
                calls.append(fmt);self.assertEqual(fmt,'svg');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(SVG)
            with patch('render_plantuml_directory.render_with_kroki',render):
                result=render_source(source_path=source,input_dir=base,output_dir=base/'out',formats=formats,theme='',engine='kroki',server_url='',kroki_url='',plantuml_command='',timeout=1,write_themed=False,colorset='colorset2')
            self.assertTrue(result.ok,result.error);self.assertEqual(calls,['svg'])
            png=next(output for output in result.outputs if output.format=='png');self.assertTrue(png.svg_derived)
            with Image.open(base/'out'/png.path) as image:
                self.assertEqual(image.convert('RGBA').getpixel((158,138)),(255,255,255,255))
                pixels=image.convert('RGB')
                shaft='#'+''.join(f'{c:02x}' for c in pixels.getpixel((80,60)))
                head='#'+''.join(f'{c:02x}' for c in pixels.getpixel((80,115)))
                self.assertGreaterEqual(contrast(shaft,'#294d19'),3)
                self.assertGreaterEqual(contrast(shaft,'#ffffff'),3)
                self.assertGreaterEqual(contrast(head,'#ffffff'),3)
            self.assertFalse(any((base/'out').glob('.native-svg-*')))
            return {output.format for output in result.outputs}

    def test_png_only_renders_one_finished_source(self):self.assertEqual(self.run_formats(['png']),{'png'})
    def test_svg_and_png_share_one_source(self):self.assertEqual(self.run_formats(['png','svg']),{'svg','png'})

    def test_raster_only_and_source_media_keep_native_path(self):
        for text in ['@startditaa\n+---+\n| A |\n+---+\n@endditaa','@startuml\n<img:source.png>\n@enduml']:
            with tempfile.TemporaryDirectory(dir=Path.cwd()) as temporary:
                base=Path(temporary);source=base/'diagram.puml';source.write_text(text)
                calls=[]
                def render(body,fmt,target,*args):
                    calls.append(fmt);target.parent.mkdir(parents=True,exist_ok=True);Image.new('RGB',(10,10),'white').save(target)
                with patch('render_plantuml_directory.render_with_kroki',render):
                    result=render_source(source_path=source,input_dir=base,output_dir=base/'out',formats=['png'],theme='',engine='kroki',server_url='',kroki_url='',plantuml_command='',timeout=1,write_themed=False,colorset='colorset1')
                self.assertTrue(result.ok,result.error);self.assertEqual(calls,['png']);self.assertFalse(result.outputs[0].svg_derived)

if __name__=='__main__':unittest.main()
