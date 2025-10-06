# PDF Flipbook Converter

## Overview

A web-based PDF flipbook converter that transforms PDF documents into interactive flipbooks with realistic 3D page-turning animations. The system allows users to upload PDFs, view them as flipbooks in their browser, and export standalone Windows executables (.exe) that bundle the flipbook viewer and all images into a single distributable file.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Framework**: Flask-based web application
- **Flipbook Animation**: turn.js library for realistic 3D page-turning effects with curl animations
- **Visual Design**: Brushed metal gradient background with procedural texture patterns
- **Navigation**: Thumbnail sidebar, page navigation controls, zoom, and fullscreen mode
- **Responsive UI**: Modern gradient styling with shadow effects and smooth transitions

### Backend Architecture
- **PDF Processing Pipeline**: Two-tier conversion strategy
  - Primary: pdf2image library for high-quality raster conversion (150 DPI default)
  - Fallback: PyMuPDF (fitz) for compatibility when pdf2image fails
- **Image Management**: Persistent storage in static/flipbooks/<flipbook_id>/
- **File Naming Convention**: Sequential page naming (page_001.png, page_002.png, etc.)
- **Multi-threading**: pdf2image configured with 4 threads for parallel conversion
- **Metadata**: JSON-based metadata tracking for each flipbook

### Export System
- **Standalone Launcher**: flipbook_launcher.py embeds HTTP server and auto-opens browser
- **PyInstaller Packaging**: Bundles flipbook viewer HTML, images, and launcher into single .exe
- **Background Processing**: Asynchronous export with progress tracking and download
- **File Structure**: Exports to output_exe/ directory with automatic cleanup

### Application Structure
- **app.py**: Flask web server with upload, viewing, and export routes
- **converter.py**: PDF to image conversion logic (PDFConverter class)
- **flipbook_launcher.py**: Standalone launcher for exported executables
- **export_flipbook.py**: PyInstaller packaging and standalone viewer generation
- **templates/**: HTML templates for upload page and flipbook viewer
- **static/**: CSS, JavaScript, and generated flipbook assets

### Packaging Strategy
- **Distribution**: PyInstaller for creating standalone Windows executables
- **Build Process**: Background threading with export status checking
- **Dependency Bundling**: All images and HTML bundled in flipbook_data/ subdirectory
- **Path Resolution**: sys._MEIPASS for accessing bundled resources

## External Dependencies

### Core PDF Processing
- **pdf2image**: Primary PDF to image conversion
- **PyMuPDF (fitz)**: Fallback PDF rendering and conversion
- **Pillow**: Image manipulation and processing

### Web Framework
- **Flask**: Web server and routing
- **jQuery**: DOM manipulation and AJAX requests
- **turn.js**: 3D flipbook page-turning animation library (CDN)

### System-Level Requirements
- **Poppler**: Required by pdf2image for PDF rendering (system package)
- **PyInstaller**: Executable packaging for .exe export

### Python Runtime
- Python 3.x standard library modules: os, sys, subprocess, shutil, pathlib, threading, json, datetime, http.server, socket, webbrowser

## Workflow

1. **Upload**: User uploads PDF via web interface
2. **Conversion**: Backend converts PDF pages to images
3. **Viewing**: Flipbook displayed with 3D page-turning animation
4. **Export**: User clicks "Export as .exe" to create standalone executable
5. **Download**: User downloads .exe file for distribution

## Recent Changes (January 2025)

- Migrated from Tkinter desktop app to Flask web application
- Integrated turn.js for realistic 3D page-turning animations
- Added export-to-.exe functionality with PyInstaller
- Implemented background export processing with progress tracking
- Fixed image path resolution in exported standalone viewers (using basename)
- Added metadata-based flipbook management system
