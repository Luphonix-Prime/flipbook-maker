$(document).ready(function() {
    let currentZoom = 1;
    let flipbookWidth = 800;
    let flipbookHeight = 600;
    
    function initFlipbook() {
        $('#flipbook').turn({
            width: flipbookWidth,
            height: flipbookHeight,
            elevation: 50,
            gradients: true,
            autoCenter: true,
            duration: 1500,
            acceleration: true,
            easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
            pages: totalPages,
            when: {
                turning: function(event, page, view) {
                    updatePageInfo(page);
                    updateThumbnails(page);
                    // Play sound immediately when page starts turning
                    if (audioEnabled) {
                        pageFlipSound.currentTime = 0;
                        pageFlipSound.play().catch(e => console.log('Audio playback failed:', e));
                    }
                },
                turned: function(event, page, view) {
                    console.log('Current page:', page);
                }
            }
        });
        
        // Add hand cursor flip areas
        addFlipAreas();
        
        updatePageInfo(1);
        updateThumbnails(1);
    }
    
    function addFlipAreas() {
        const flipbookContainer = $('.flipbook-wrapper');
        
        // Remove existing areas if any
        $('.page-flip-area, .page-corner-overlay, .hand-indicator, .page-curl').remove();
        
        // Add interactive page corners for dragging
        addDraggableCorners();
    }
    
    function addDraggableCorners() {
        const flipbook = $('#flipbook');
        
        // Add page curl effect elements
        const rightCurl = $('<div class="page-curl"></div>');
        const leftCurl = $('<div class="page-curl left-curl"></div>');
        flipbook.append(rightCurl);
        flipbook.append(leftCurl);
        
        // Right corner for next page
        const rightCorner = $('<div class="page-corner-overlay"></div>');
        let isDragging = false;
        let startX = 0;
        let dragDistance = 0;
        
        rightCorner.on('mousedown touchstart', function(e) {
            e.preventDefault();
            isDragging = true;
            startX = e.pageX || e.originalEvent.touches[0].pageX;
            rightCorner.addClass('dragging');
            rightCurl.addClass('dragging');
        });
        
        $(document).on('mousemove touchmove', function(e) {
            if (!isDragging) return;
            
            const currentX = e.pageX || e.originalEvent.touches[0].pageX;
            dragDistance = startX - currentX;
            
            if (dragDistance > 0) {
                requestAnimationFrame(() => {
                    const curlSize = Math.min(dragDistance * 0.8, 200);
                    rightCurl.addClass('active').css({
                        'border-bottom-width': curlSize + 'px',
                        'border-left-width': curlSize + 'px'
                    });
                });
            }
        });
        
        $(document).on('mouseup touchend', function() {
            if (!isDragging) return;
            
            isDragging = false;
            rightCorner.removeClass('dragging');
            rightCurl.removeClass('dragging active').css({
                'border-bottom-width': '0',
                'border-left-width': '0'
            });
            
            // If dragged enough, flip the page
            if (dragDistance > 100) {
                flipbook.turn('next');
            }
            
            dragDistance = 0;
        });
        
        // Left corner for previous page
        const leftCorner = $('<div class="page-corner-overlay left-corner"></div>');
        let isLeftDragging = false;
        let leftStartX = 0;
        let leftDragDistance = 0;
        
        leftCorner.on('mousedown touchstart', function(e) {
            e.preventDefault();
            isLeftDragging = true;
            leftStartX = e.pageX || e.originalEvent.touches[0].pageX;
            leftCorner.addClass('dragging');
            leftCurl.addClass('dragging');
        });
        
        $(document).on('mousemove touchmove', function(e) {
            if (!isLeftDragging) return;
            
            const currentX = e.pageX || e.originalEvent.touches[0].pageX;
            leftDragDistance = currentX - leftStartX;
            
            if (leftDragDistance > 0) {
                requestAnimationFrame(() => {
                    const curlSize = Math.min(leftDragDistance * 0.8, 200);
                    leftCurl.addClass('active').css({
                        'border-bottom-width': curlSize + 'px',
                        'border-right-width': curlSize + 'px',
                        'left': '0',
                        'right': 'auto'
                    });
                });
            }
        });
        
        $(document).on('mouseup touchend', function() {
            if (!isLeftDragging) return;
            
            isLeftDragging = false;
            leftCorner.removeClass('dragging');
            leftCurl.removeClass('dragging active').css({
                'border-bottom-width': '0',
                'border-right-width': '0'
            });
            
            // If dragged enough, flip to previous page
            if (leftDragDistance > 100) {
                flipbook.turn('previous');
            }
            
            leftDragDistance = 0;
        });
        
        flipbook.append(rightCorner);
        flipbook.append(leftCorner);
    }
    
    function updatePageInfo(page) {
        $('#currentPage').text(page);
        $('#totalPages').text(totalPages);
    }
    
    function updateThumbnails(page) {
        $('.thumbnail-item').removeClass('active');
        $(`.thumbnail-item[data-page="${page}"]`).addClass('active');
        
        const thumbnail = $(`.thumbnail-item[data-page="${page}"]`)[0];
        if (thumbnail) {
            thumbnail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
    
    $('#prevBtn').click(function() {
        $('#flipbook').turn('previous');
    });
    
    $('#nextBtn').click(function() {
        $('#flipbook').turn('next');
    });
    
    $('.thumbnail-item').click(function() {
        const page = parseInt($(this).data('page'));
        $('#flipbook').turn('page', page);
    });
    
    function applyZoom() {
        const newWidth = Math.floor(flipbookWidth * currentZoom);
        const newHeight = Math.floor(flipbookHeight * currentZoom);
        
        $('#flipbook').turn('size', newWidth, newHeight);
        
        // Update container size
        $('.flipbook-wrapper').css({
            width: newWidth + 100,
            height: newHeight + 100
        });
    }
    
    // Add zoom controls
    $('#zoomInBtn').on('click', function() {
        if (currentZoom < 2.0) {
            currentZoom += 0.2;
            applyZoom();
        }
    });
    
    $('#zoomOutBtn').on('click', function() {
        if (currentZoom > 0.5) {
            currentZoom -= 0.2;
            applyZoom();
        }
    });
    
    $('#fullscreenBtn').click(function() {
        const elem = document.querySelector('.flipbook-container');
        
        if (!document.fullscreenElement) {
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) {
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                elem.msRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }
    });
    
    $(window).on('keydown', function(e) {
        if (e.keyCode === 37) {
            $('#flipbook').turn('previous');
        } else if (e.keyCode === 39) {
            $('#flipbook').turn('next');
        }
    });
    
    $(window).on('resize', function() {
        setTimeout(function() {
            $('#flipbook').turn('resize');
        }, 100);
    });
    
    // Toggle thumbnails panel
    $('#toggleThumbnailsBtn').click(function() {
        $('.thumbnails-panel').toggle();
        $('#flipbook').turn('resize');
    });
    
    // Single page view toggle
    let isDoublePageView = true;
    $('#singlePageBtn').click(function() {
        isDoublePageView = !isDoublePageView;
        $('#flipbook').turn('display', isDoublePageView ? 'double' : 'single');
        $(this).html(isDoublePageView ? '📄' : '📖');
    });
    
    // Grid view (show all pages)
    $('#gridViewBtn').click(function() {
        openGridView();
    });
    
    // Download original PDF
    $('#downloadBtn').click(function() {
        window.location.href = `/download-pdf/${flipbookId}`;
    });
    
    // Print flipbook
    $('#printBtn').click(function() {
        window.print();
    });
    
    // Page flip sound - preload to reduce latency
    let audioEnabled = true;
    const pageFlipSound = new Audio('/static/audio/page-flp.mp3');
    pageFlipSound.volume = 0.7;
    pageFlipSound.preload = 'auto';
    pageFlipSound.load(); // Force preload
    
    // Toggle sound on/off
    $('#audioBtn').html('🔊');
    $('#audioBtn').click(function() {
        audioEnabled = !audioEnabled;
        $(this).html(audioEnabled ? '🔊' : '🔇');
    });
    
    $('#exportBtn').click(async function() {
        const btn = $(this);
        btn.prop('disabled', true);
        
        $('#exportStatus').show();
        $('.export-message').text('Creating standalone .exe file...');
        $('.export-details').text('This may take a few minutes. Please wait...');
        
        try {
            const response = await window.electronAPI.exportFlipbook(flipbookId);
            
            if (response.success) {
                $('.export-message').text('Building executable...');
                $('.export-details').text('Packaging flipbook with PyInstaller...');
                
                let attempts = 0;
                const maxAttempts = 60;
                
                const checkInterval = setInterval(async () => {
                    attempts++;
                    
                    try {
                        const checkResponse = await window.electronAPI.checkExport(flipbookId);
                        
                        if (checkResponse.ready) {
                            clearInterval(checkInterval);
                            
                            $('.export-message').html('✓ .exe Ready for Download!');
                            $('.export-details').html(`
                                File size: ${checkResponse.size_mb} MB<br>
                                <button id="downloadExeBtn" class="download-exe-btn">
                                    Download ${flipbookId}.exe
                                </button><br>
                                <button class="close-export-btn">Close</button>
                            `);
                            
                            $('#downloadExeBtn').click(async () => {
                                try {
                                    await window.electronAPI.downloadExe(flipbookId);
                                } catch (error) {
                                    console.error('Download error:', error);
                                    alert('Failed to download executable. Please try again.');
                                }
                            });
                            
                            $('.close-export-btn').click(() => {
                                $('#exportStatus').hide();
                            });
                            
                            btn.prop('disabled', false);
                        } else if (attempts >= maxAttempts) {
                            clearInterval(checkInterval);
                            $('.export-message').html('⚠ Build Timeout');
                            $('.export-details').html(`
                                The build is taking longer than expected.<br>
                                <button onclick="location.reload();">Refresh and Try Again</button>
                            `);
                            btn.prop('disabled', false);
                        }
                    } catch (err) {
                        console.error('Check error:', err);
                    }
                }, 5000);
            } else {
                throw new Error(response.error || 'Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            $('.export-message').html('✗ Export Failed');
            $('.export-details').html(`
                ${error.message}<br>
                <button onclick="$('#exportStatus').hide();">Close</button>
            `);
            btn.prop('disabled', false);
        }
    });
    
    // Grid view modal
    function openGridView() {
        const gridModal = $('<div class="grid-modal"></div>');
        const closeBtn = $('<button class="grid-close">✕ Close Grid View</button>');
        const gridContainer = $('<div class="grid-container"></div>');
        
        for (let i = 1; i <= totalPages; i++) {
            const thumbnail = $(`.thumbnail-item[data-page="${i}"] img`).attr('src');
            const gridItem = $(`
                <div class="grid-item" data-page="${i}">
                    <img src="${thumbnail}" alt="Page ${i}">
                    <div class="grid-item-number">${i}</div>
                </div>
            `);
            gridItem.on('click', function() {
                const page = $(this).data('page');
                $('#flipbook').turn('page', page);
                gridModal.remove();
            });
            gridContainer.append(gridItem);
        }
        
        closeBtn.on('click', function() {
            gridModal.remove();
        });
        
        gridModal.append(closeBtn);
        gridModal.append(gridContainer);
        $('body').append(gridModal);
        
        setTimeout(() => gridModal.addClass('active'), 10);
    }
    
    // Help modal
    $('#helpBtn').click(function() {
        openHelp();
    });
    
    function openHelp() {
        const helpOverlay = $('<div class="help-overlay"></div>');
        const helpModal = $(`
            <div class="help-modal">
                <h2>📖 Flipbook Controls</h2>
                <ul>
                    <li><strong>◀ ▶ Buttons:</strong> Navigate between pages</li>
                    <li><strong>📄 Single Page:</strong> Toggle single/double page view</li>
                    <li><strong>⊞ Grid View:</strong> See all pages at once</li>
                    <li><strong>⬇ Download:</strong> Download original PDF</li>
                    <li><strong>🖨️ Print:</strong> Print all pages</li>
                    <li><strong>🔊 Audio:</strong> Toggle page flip sound</li>
                    <li><strong>Zoom +/-:</strong> Adjust flipbook size</li>
                    <li><strong>⛶ Fullscreen:</strong> Enter fullscreen mode</li>
                    <li><strong>💾 Export:</strong> Create standalone .exe</li>
                    <li><strong>Arrow Keys:</strong> Navigate pages</li>
                    <li><strong>Click Edges:</strong> Turn pages</li>
                </ul>
                <button class="help-close">Got it!</button>
            </div>
        `);
        
        helpOverlay.on('click', function() {
            helpOverlay.remove();
            helpModal.remove();
        });
        
        helpModal.find('.help-close').on('click', function() {
            helpOverlay.remove();
            helpModal.remove();
        });
        
        $('body').append(helpOverlay);
        $('body').append(helpModal);
        
        setTimeout(() => {
            helpOverlay.addClass('active');
            helpModal.addClass('active');
        }, 10);
    }
    
    initFlipbook();
});
