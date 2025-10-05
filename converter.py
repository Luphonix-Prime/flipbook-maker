import os
import pymupdf as fitz
from pdf2image import convert_from_path
from PIL import Image
from pathlib import Path


class PDFConverter:
    def __init__(self, pdf_path, output_dir="temp_images"):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.pages = []
        
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def convert_to_images(self, dpi=200):
        print(f"Converting PDF: {self.pdf_path}")
        print(f"Output directory: {self.output_dir}")
        
        try:
            images = convert_from_path(
                self.pdf_path,
                dpi=dpi,
                output_folder=self.output_dir,
                fmt='png',
                thread_count=4
            )
            
            self.pages = []
            for i, image in enumerate(images, start=1):
                page_path = os.path.join(self.output_dir, f"page_{i:03d}.png")
                image.save(page_path, 'PNG')
                self.pages.append(page_path)
                print(f"Saved page {i}/{len(images)}: {page_path}")
            
            print(f"✓ Successfully converted {len(self.pages)} pages")
            return self.pages
            
        except Exception as e:
            print(f"Error converting PDF with pdf2image: {e}")
            return self._fallback_pymupdf_conversion()
    
    def _fallback_pymupdf_conversion(self):
        print("Attempting fallback conversion with PyMuPDF...")
        try:
            doc = fitz.open(self.pdf_path)
            self.pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat) if hasattr(page, 'get_pixmap') else page.get_pixmap(mat=mat)
                
                page_path = os.path.join(self.output_dir, f"page_{page_num + 1:03d}.png")
                pix.save(page_path)
                self.pages.append(page_path)
                print(f"Saved page {page_num + 1}/{len(doc)}: {page_path}")
            
            doc.close()
            print(f"✓ Successfully converted {len(self.pages)} pages using PyMuPDF")
            return self.pages
            
        except Exception as e:
            print(f"Error in fallback conversion: {e}")
            return []
    
    def get_page_count(self):
        try:
            doc = fitz.open(self.pdf_path)
            count = len(doc)
            doc.close()
            return count
        except:
            return len(self.pages) if self.pages else 0
    
    def clear_temp_images(self):
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                if file.endswith('.png'):
                    os.remove(os.path.join(self.output_dir, file))
            print(f"✓ Cleared temporary images from {self.output_dir}")


if __name__ == "__main__":
    print("PDF Converter Module")
    print("Use this module to convert PDF files to images")
