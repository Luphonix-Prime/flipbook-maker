import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def create_standalone_viewer_html(metadata, output_dir):
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
    
    <script>
        const totalPages = {metadata['total_pages']};
        
        $(document).ready(function() {{
            let currentZoom = 1;
            let flipbookWidth = 800;
            let flipbookHeight = 600;
            
            // Page flip audio
            let audioEnabled = true;
            const pageFlipSound = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIGGi78OScTgwNUrDn77ZiGwU4k9n0y3krBSl+zPLaizsKF2S36OSXUAoJQ6Hn8bllHgU1jdXzzn0pBSuBzvLZiTYIGGi78OScTgwNUrDn77ZiGwU4k9n0y3krBSl+zPLaizsKF2S36OSXUAoJQ6Hn8bllHgU1jdXzzn0pBSuBzvLZiTYIGGi78OScTgwNUrDn77ZiGwU4k9n0y3krBSl+zPLaizsKF2S36OSXUAoJQ6Hn8bllHgU1jdXzzn0pBSuBzvLZiTYIGGi78OScTgwNUrDn77ZiGwU4k9n0y3krBSl+zPLaizsKF2S36OSXUAoJQ6Hn8bllHgU1jdXzzn0pBSuBzvLZiTYIGGi78OScTgwNUrDn77ZiGwU4k9n0y3krBSl+zPLaizsKF2S36OSXUAoJQ6Hn8bllHgU1jdXzzn0pBSuBzvLZiTYIGGi78OScTgwNUrDn77ZiGwU4k9n0y3krBSl+zPLaizsKF2S36OSXUAoJQ6Hn8bllHgU1jdXzzn0pBSuBzvLZiTYIGGi78OScTgwNU==');
            pageFlipSound.volume = 0.7;
            
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
                            if (audioEnabled) {{
                                pageFlipSound.currentTime = 0;
                                pageFlipSound.play().catch(e => console.log('Audio failed:', e));
                            }}
                        }}
                    }}
                }});
                
                updatePageInfo(1);
                updateThumbnails(1);
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
