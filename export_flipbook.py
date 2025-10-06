import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def create_standalone_viewer_html(metadata, output_dir):
    # Copy audio file to output directory
    source_audio = 'static/audio/page-flp.mp3'
    if os.path.exists(source_audio):
        dest_audio = os.path.join(output_dir, 'page-flp.mp3')
        shutil.copy(source_audio, dest_audio)
        print(f"Copied audio file to {dest_audio}")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['filename']} - Flipbook</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/turn.js/3/turn.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #a8b8c8 0%, #8899aa 100%);
            background-attachment: fixed;
            overflow: hidden;
        }}

        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                repeating-linear-gradient(0deg, rgba(255,255,255,0.03) 0px, transparent 2px, transparent 4px),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.03) 0px, transparent 2px, transparent 4px);
            pointer-events: none;
        }}

        .flipbook-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        .header {{
            background: linear-gradient(180deg, #5a6a7a 0%, #4a5a6a 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}

        .title {{
            font-size: 1.2rem;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}

        .page-info {{
            font-size: 1rem;
            background: rgba(0,0,0,0.2);
            padding: 5px 15px;
            border-radius: 5px;
        }}

        .main-content {{
            flex: 1;
            display: flex;
            overflow: hidden;
        }}

        .thumbnails-panel {{
            width: 100px;
            background: linear-gradient(180deg, #3a4a5a 0%, #2a3a4a 100%);
            border-right: 2px solid #1a2a3a;
            display: flex;
            flex-direction: column;
            box-shadow: 2px 0 10px rgba(0,0,0,0.3);
        }}

        .thumbnails-header {{
            padding: 10px;
            background: #2a3a4a;
            color: #aaa;
            text-align: center;
            font-size: 0.8rem;
            font-weight: bold;
            border-bottom: 1px solid #1a2a3a;
        }}

        .thumbnails-list {{
            flex: 1;
            overflow-y: auto;
            padding: 5px;
        }}

        .thumbnail-item {{
            margin-bottom: 10px;
            cursor: pointer;
            position: relative;
            border: 2px solid transparent;
            border-radius: 4px;
            transition: all 0.3s ease;
        }}

        .thumbnail-item:hover {{
            border-color: #667eea;
            transform: scale(1.05);
        }}

        .thumbnail-item.active {{
            border-color: #ffa500;
        }}

        .thumbnail-item img {{
            width: 100%;
            display: block;
            border-radius: 3px;
        }}

        .thumbnail-number {{
            position: absolute;
            bottom: 2px;
            right: 2px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 2px 6px;
            font-size: 0.7rem;
            border-radius: 3px;
        }}

        .flipbook-wrapper {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            overflow: hidden;
        }}

        #flipbook {{
            width: 800px;
            height: 600px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}

        #flipbook .page {{
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.1);
        }}

        #flipbook .page img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}

        .controls {{
            background: linear-gradient(180deg, #4a5a6a 0%, #3a4a5a 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
        }}

        .control-btn {{
            padding: 10px 20px;
            background: linear-gradient(180deg, #6a7a8a 0%, #5a6a7a 100%);
            border: none;
            border-radius: 5px;
            color: white;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }}

        .control-btn:hover {{
            background: linear-gradient(180deg, #7a8a9a 0%, #6a7a8a 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        }}

        .control-btn:active {{
            transform: translateY(0);
        }}

        .control-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .page-curl {{
            position: absolute;
            bottom: 0;
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 0;
            border-color: transparent;
            transition: all 0.35s cubic-bezier(0.4, 0.0, 0.2, 1);
            pointer-events: none;
            z-index: 150;
        }}

        .page-curl.right {{
            right: 0;
            border-bottom-color: rgba(0, 0, 0, 0.15);
            border-left-color: rgba(255, 255, 255, 0.3);
        }}

        .page-curl.left {{
            left: 0;
            border-bottom-color: rgba(0, 0, 0, 0.15);
            border-right-color: rgba(255, 255, 255, 0.3);
        }}

        .page-flip-area {{
            position: absolute;
            top: 0;
            bottom: 0;
            width: 50%;
            cursor: pointer;
            z-index: 100;
        }}

        .page-flip-area.left {{
            left: 0;
        }}

        .page-flip-area.right {{
            right: 0;
        }}

        .grid-modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            z-index: 2000;
            overflow-y: auto;
            padding: 20px;
        }}

        .grid-modal.active {{
            display: block;
        }}

        .grid-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .grid-item {{
            cursor: pointer;
            position: relative;
            border: 3px solid transparent;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}

        .grid-item:hover {{
            border-color: #667eea;
            transform: scale(1.05);
        }}

        .grid-item img {{
            width: 100%;
            border-radius: 5px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        }}

        .grid-item-number {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
        }}

        .grid-close {{
            position: fixed;
            top: 20px;
            right: 30px;
            background: #dc3545;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 1.2rem;
            cursor: pointer;
            border-radius: 5px;
            z-index: 2001;
        }}

        .help-modal {{
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            z-index: 2000;
            max-width: 500px;
            width: 90%;
        }}

        .help-modal.active {{
            display: block;
        }}

        .help-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            z-index: 1999;
        }}

        .help-overlay.active {{
            display: block;
        }}

        .help-modal h2 {{
            margin-top: 0;
            color: #333;
        }}

        .help-modal ul {{
            list-style: none;
            padding: 0;
        }}

        .help-modal li {{
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}

        .help-close {{
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 15px;
        }}

        .thumbnails-panel.hidden {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="flipbook-container">
        <div class="header">
            <div class="title">{metadata['filename']}</div>
            <div class="page-info">
                pages: <span id="currentPage">1</span> / <span id="totalPages">{metadata['total_pages']}</span>
            </div>
        </div>
        
        <div class="main-content">
            <div class="thumbnails-panel">
                <div class="thumbnails-header">PAGES</div>
                <div class="thumbnails-list" id="thumbnailsList">
"""
    
    for page in metadata['pages']:
        page_num = page['page']
        img_path = os.path.basename(page['image'])
        html_content += f"""                    <div class="thumbnail-item" data-page="{page_num}">
                        <img src="{img_path}" alt="Page {page_num}">
                        <div class="thumbnail-number">{page_num:02d}</div>
                    </div>
"""
    
    html_content += """                </div>
            </div>
            
            <div class="flipbook-wrapper">
                <div id="flipbook">
"""
    
    for page in metadata['pages']:
        img_path = os.path.basename(page['image'])
        html_content += f"""                    <div class="page">
                        <img src="{img_path}" alt="Page {page['page']}">
                    </div>
"""
    
    html_content += f"""                </div>
            </div>
        </div>
        
        <div class="controls">
            <button id="prevBtn" class="control-btn">◀ Previous</button>
            <button id="singlePageBtn" class="control-btn" title="Single Page View">📄</button>
            <button id="gridViewBtn" class="control-btn" title="Grid View">🔲</button>
            <button id="helpBtn" class="control-btn" title="Help">❗</button>
            <button id="toggleThumbnailsBtn" class="control-btn" title="Toggle Thumbnails">🖼️</button>
            <button id="audioBtn" class="control-btn">🔊</button>
            <button id="zoomOutBtn" class="control-btn">Zoom −</button>
            <button id="zoomInBtn" class="control-btn">Zoom +</button>
            <button id="fullscreenBtn" class="control-btn">⛶ Fullscreen</button>
            <button id="printBtn" class="control-btn">🖨️ Print</button>
            <button id="nextBtn" class="control-btn">Next ▶</button>
        </div>
        
        <div class="page-curl right"></div>
        <div class="page-curl left"></div>
    </div>

    <div class="grid-modal" id="gridModal">
        <button class="grid-close" onclick="closeGridView()">✕ Close Grid View</button>
        <div class="grid-container" id="gridContainer"></div>
    </div>

    <div class="help-overlay" id="helpOverlay"></div>
    <div class="help-modal" id="helpModal">
        <h2>📖 Flipbook Controls</h2>
        <ul>
            <li><strong>◀ ▶ Buttons:</strong> Navigate between pages</li>
            <li><strong>📄 Single Page:</strong> View one page at a time</li>
            <li><strong>🔲 Grid View:</strong> See all pages at once</li>
            <li><strong>🖼️ Thumbnails:</strong> Toggle side panel</li>
            <li><strong>🔊 Audio:</strong> Toggle page flip sound</li>
            <li><strong>Zoom +/-:</strong> Adjust flipbook size</li>
            <li><strong>⛶ Fullscreen:</strong> Enter fullscreen mode</li>
            <li><strong>🖨️ Print:</strong> Print all pages</li>
            <li><strong>Arrow Keys:</strong> Navigate pages</li>
            <li><strong>Click Edges:</strong> Turn pages</li>
        </ul>
        <button class="help-close" onclick="closeHelp()">Got it!</button>
    </div>
    
    <script>
        const totalPages = {metadata['total_pages']};
        
        $(document).ready(function() {{
            let currentZoom = 1;
            let flipbookWidth = 800;
            let flipbookHeight = 600;
            
            // Page flip audio - preload to reduce latency
            let audioEnabled = true;
            const pageFlipSound = new Audio('page-flp.mp3');
            pageFlipSound.volume = 0.7;
            pageFlipSound.preload = 'auto';
            pageFlipSound.load(); // Force preload
            
            function initFlipbook() {{
                $('#flipbook').turn({{
                    width: flipbookWidth,
                    height: flipbookHeight,
                    elevation: 50,
                    gradients: true,
                    autoCenter: true,
                    duration: 1500,
                    acceleration: true,
                    pages: totalPages,
                    when: {{
                        turning: function(event, page, view) {{
                            updatePageInfo(page);
                            updateThumbnails(page);
                        }},
                        turned: function(event, page, view) {{
                            console.log('Current page:', page);
                        }}
                    }}
                }});
                
                addFlipAreas();
                
                updatePageInfo(1);
                updateThumbnails(1);
            }}
            
            function addFlipAreas() {{
                const flipbookContainer = $('.flipbook-wrapper');
                
                // Create left flip area
                const leftArea = $('<div class="page-flip-area left"></div>');
                leftArea.on('click', function(e) {{
                    $('#flipbook').turn('previous');
                }});
                
                // Create right flip area
                const rightArea = $('<div class="page-flip-area right"></div>');
                rightArea.on('click', function(e) {{
                    $('#flipbook').turn('next');
                }});
                
                flipbookContainer.append(leftArea);
                flipbookContainer.append(rightArea);
            }}
            
            function updatePageInfo(page) {{
                $('#currentPage').text(page);
            }}
            
            function updateThumbnails(page) {{
                $('.thumbnail-item').removeClass('active');
                $(`.thumbnail-item[data-page="${{page}}"]`).addClass('active');
                
                const thumbnail = $(`.thumbnail-item[data-page="${{page}}"]`)[0];
                if (thumbnail) {{
                    thumbnail.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                }}
            }}
            
            $('#prevBtn').click(function() {{
                $('#flipbook').turn('previous');
            }});
            
            $('#nextBtn').click(function() {{
                $('#flipbook').turn('next');
            }});
            
            $('.thumbnail-item').click(function() {{
                const page = parseInt($(this).data('page'));
                $('#flipbook').turn('page', page);
            }});
            
            $('#zoomInBtn').click(function() {{
                if (currentZoom < 1.5) {{
                    currentZoom += 0.1;
                    applyZoom();
                }}
            }});
            
            $('#zoomOutBtn').click(function() {{
                if (currentZoom > 0.6) {{
                    currentZoom -= 0.1;
                    applyZoom();
                }}
            }});
            
            function applyZoom() {{
                const newWidth = Math.floor(flipbookWidth * currentZoom);
                const newHeight = Math.floor(flipbookHeight * currentZoom);
                $('#flipbook').turn('size', newWidth, newHeight);
            }}
            
            $('#fullscreenBtn').click(function() {{
                const elem = document.querySelector('.flipbook-container');
                if (!document.fullscreenElement) {{
                    if (elem.requestFullscreen) elem.requestFullscreen();
                    else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
                }} else {{
                    if (document.exitFullscreen) document.exitFullscreen();
                    else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
                }}
            }});
            
            $('#printBtn').click(function() {{
                window.print();
            }});
            
            $('#audioBtn').html('🔊');
            $('#audioBtn').click(function() {{
                audioEnabled = !audioEnabled;
                $(this).html(audioEnabled ? '🔊' : '🔇');
            }});

            // Single page view
            let isDoublePageView = true;
            $('#singlePageBtn').click(function() {{
                isDoublePageView = !isDoublePageView;
                $('#flipbook').turn('display', isDoublePageView ? 'double' : 'single');
                $(this).html(isDoublePageView ? '📄' : '📖');
            }});

            // Grid view
            $('#gridViewBtn').click(function() {{
                openGridView();
            }});

            // Help modal
            $('#helpBtn').click(function() {{
                openHelp();
            }});

            // Toggle thumbnails
            $('#toggleThumbnailsBtn').click(function() {{
                $('.thumbnails-panel').toggleClass('hidden');
            }});
            
            // Play sound when page turns - use 'turning' event for immediate playback
            $('#flipbook').on('turning', function() {{
                if (audioEnabled) {{
                    pageFlipSound.currentTime = 0;
                    pageFlipSound.play().catch(e => console.log('Audio failed:', e));
                }}
            }});
            
            $(window).on('keydown', function(e) {{
                if (e.keyCode === 37) $('#flipbook').turn('previous');
                else if (e.keyCode === 39) $('#flipbook').turn('next');
            }});
            
            // Page curl drag effects
            const rightCurl = $('.page-curl.right');
            const leftCurl = $('.page-curl.left');
            let startX, currentX, dragDistance;
            let leftStartX, leftDragDistance;
            
            $('.flipbook-wrapper').on('mousedown touchstart', function(e) {{
                const x = e.pageX || e.originalEvent.touches[0].pageX;
                const containerWidth = $(this).width();
                const clickPosition = x - $(this).offset().left;
                
                if (clickPosition > containerWidth / 2) {{
                    startX = x;
                }} else {{
                    leftStartX = x;
                }}
            }});
            
            $('.flipbook-wrapper').on('mousemove touchmove', function(e) {{
                const x = e.pageX || e.originalEvent.touches[0].pageX;
                
                if (startX) {{
                    currentX = x;
                    dragDistance = startX - currentX;
                    
                    if (dragDistance > 0) {{
                        const curlSize = Math.min(dragDistance * 0.8, 200);
                        rightCurl.addClass('active').css({{
                            'border-bottom-width': curlSize + 'px',
                            'border-left-width': curlSize + 'px'
                        }});
                    }}
                }}
                
                if (leftStartX) {{
                    currentX = x;
                    leftDragDistance = currentX - leftStartX;
                    
                    if (leftDragDistance > 0) {{
                        const curlSize = Math.min(leftDragDistance * 0.8, 200);
                        leftCurl.addClass('active').css({{
                            'border-bottom-width': curlSize + 'px',
                            'border-right-width': curlSize + 'px'
                        }});
                    }}
                }}
            }});
            
            $('.flipbook-wrapper').on('mouseup mouseleave touchend', function() {{
                rightCurl.removeClass('active').css({{
                    'border-bottom-width': '0',
                    'border-left-width': '0'
                }});
                leftCurl.removeClass('active').css({{
                    'border-bottom-width': '0',
                    'border-right-width': '0'
                }});
                startX = null;
                leftStartX = null;
            }});
            
            initFlipbook();
        }});

        function openGridView() {{
            const gridContainer = $('#gridContainer');
            gridContainer.empty();

            for (let i = 1; i <= totalPages; i++) {{
                const thumbnail = $(`.thumbnail-item[data-page="${{i}}"] img`).attr('src');
                const gridItem = $(`
                    <div class="grid-item" onclick="goToPageFromGrid(${{i}})">
                        <img src="${{thumbnail}}" alt="Page ${{i}}">
                        <div class="grid-item-number">${{i}}</div>
                    </div>
                `);
                gridContainer.append(gridItem);
            }}

            $('#gridModal').addClass('active');
        }}

        function closeGridView() {{
            $('#gridModal').removeClass('active');
        }}

        function goToPageFromGrid(page) {{
            $('#flipbook').turn('page', page);
            closeGridView();
        }}

        function openHelp() {{
            $('#helpModal').addClass('active');
            $('#helpOverlay').addClass('active');
        }}

        function closeHelp() {{
            $('#helpModal').removeClass('active');
            $('#helpOverlay').removeClass('active');
        }}

        $('#helpOverlay').click(function() {{
            closeHelp();
        }});

        $(document).on('keydown', function(e) {{
            if (e.keyCode === 27) {{ // ESC key
                closeGridView();
                closeHelp();
            }}
        }});
    </script>
</body>
</html>"""
    
    viewer_path = os.path.join(output_dir, 'viewer.html')
    with open(viewer_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return viewer_path

def build_exe(flipbook_id, flipbook_dir):
    print(f"Building .exe for flipbook: {flipbook_id}")
    
    metadata_path = os.path.join(flipbook_dir, 'metadata.json')
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    build_dir = os.path.join('output_exe', flipbook_id)
    os.makedirs(build_dir, exist_ok=True)
    
    flipbook_data_dir = os.path.join(build_dir, 'flipbook_data')
    if os.path.exists(flipbook_data_dir):
        shutil.rmtree(flipbook_data_dir)
    
    shutil.copytree(flipbook_dir, flipbook_data_dir)
    
    create_standalone_viewer_html(metadata, flipbook_data_dir)
    
    launcher_path = os.path.abspath('flipbook_launcher.py')
    
    os.chdir(build_dir)
    
    pyinstaller_command = [
        sys.executable, '-m', 'PyInstaller',
        '--name', flipbook_id,
        '--onefile',
        '--windowed',
        '--add-data', f'flipbook_data{os.pathsep}flipbook_data',
        '--hidden-import', 'http.server',
        '--hidden-import', 'webbrowser',
        '--icon', 'NONE',
        launcher_path
    ]
    
    print("Running PyInstaller...")
    result = subprocess.run(pyinstaller_command, capture_output=True, text=True)
    
    os.chdir('../..')
    
    exe_path = os.path.join(build_dir, 'dist', f'{flipbook_id}.exe')
    if os.path.exists(exe_path):
        final_exe = os.path.join('output_exe', f'{flipbook_id}.exe')
        shutil.copy(exe_path, final_exe)
        
        if os.path.exists(os.path.join(build_dir, 'build')):
            shutil.rmtree(os.path.join(build_dir, 'build'))
        if os.path.exists(os.path.join(build_dir, 'dist')):
            shutil.rmtree(os.path.join(build_dir, 'dist'))
        if os.path.exists(os.path.join(build_dir, f'{flipbook_id}.spec')):
            os.remove(os.path.join(build_dir, f'{flipbook_id}.spec'))
        
        print(f"✓ .exe created successfully: {final_exe}")
        return final_exe
    else:
        print(f"Error: .exe file not found at {exe_path}")
        print("PyInstaller output:", result.stdout)
        print("PyInstaller errors:", result.stderr)
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python export_flipbook.py <flipbook_id>")
        sys.exit(1)
    
    flipbook_id = sys.argv[1]
    flipbook_dir = os.path.join('static', 'flipbooks', flipbook_id)
    
    if not os.path.exists(flipbook_dir):
        print(f"Error: Flipbook directory not found: {flipbook_dir}")
        sys.exit(1)
    
    exe_path = build_exe(flipbook_id, flipbook_dir)
    if exe_path:
        print(f"\nSuccess! Your flipbook .exe is ready:")
        print(f"  {exe_path}")
    else:
        print("\nFailed to create .exe")
        sys.exit(1)
