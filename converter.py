import os
import fitz  # PyMuPDF
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
            # First attempt with pdf2image
            try:
                images = convert_from_path(
                    self.pdf_path,
                    dpi=dpi,
                    output_folder=self.output_dir,
                    fmt='png',
                    thread_count=4,
                    poppler_path=None  # Let it find poppler automatically
                )
                
                self.pages = []
                for i, image in enumerate(images, start=1):
                    page_path = os.path.join(self.output_dir, f"page_{i:03d}.png")
                    image.save(page_path, 'PNG')
                    self.pages.append(page_path)
                    print(f"Saved page {i}/{len(images)}: {page_path}")
                
                return self.pages
                
            except Exception as e:
                print(f"pdf2image failed, trying PyMuPDF: {e}")
                return self._fallback_pymupdf_conversion()
                
        except Exception as e:
            print(f"All conversion methods failed: {e}")
            return []

    def _fallback_pymupdf_conversion(self):
        print("Using PyMuPDF for conversion...")
        try:
            doc = fitz.open(self.pdf_path)
            self.pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                page_path = os.path.join(self.output_dir, f"page_{page_num + 1:03d}.png")
                pix.save(page_path)
                self.pages.append(page_path)
                print(f"Saved page {page_num + 1}/{len(doc)}: {page_path}")
            
            doc.close()
            return self.pages
            
        except Exception as e:
            print(f"PyMuPDF conversion failed: {e}")
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
