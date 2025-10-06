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
            duration: 1000,
            pages: totalPages,
            when: {
                turning: function(event, page, view) {
                    updatePageInfo(page);
                    updateThumbnails(page);
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
        
        // Create left flip area (click to previous page)
        const leftArea = $('<div class="page-flip-area left"></div>');
        leftArea.on('click', function(e) {
            if (!$(e.target).hasClass('page-corner-overlay')) {
                $('#flipbook').turn('previous');
            }
        });
        
        // Create right flip area (click to next page)
        const rightArea = $('<div class="page-flip-area right"></div>');
        rightArea.on('click', function(e) {
            if (!$(e.target).hasClass('page-corner-overlay')) {
                $('#flipbook').turn('next');
            }
        });
        
        flipbookContainer.append(leftArea);
        flipbookContainer.append(rightArea);
        
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
        
        // Add hand indicators
        const rightHand = $('<div class="hand-indicator">👆</div>');
        const leftHand = $('<div class="hand-indicator left">👆</div>');
        flipbook.append(rightHand);
        flipbook.append(leftHand);
        
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
            rightHand.hide();
        });
        
        $(document).on('mousemove touchmove', function(e) {
            if (!isDragging) return;
            
            const currentX = e.pageX || e.originalEvent.touches[0].pageX;
            dragDistance = startX - currentX;
            
            if (dragDistance > 0) {
                const curlSize = Math.min(dragDistance * 0.8, 200);
                rightCurl.addClass('active').css({
                    'border-bottom-width': curlSize + 'px',
                    'border-left-width': curlSize + 'px'
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
            rightHand.show();
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
            leftHand.hide();
        });
        
        $(document).on('mousemove touchmove', function(e) {
            if (!isLeftDragging) return;
            
            const currentX = e.pageX || e.originalEvent.touches[0].pageX;
            leftDragDistance = currentX - leftStartX;
            
            if (leftDragDistance > 0) {
                const curlSize = Math.min(leftDragDistance * 0.8, 200);
                leftCurl.addClass('active').css({
                    'border-bottom-width': curlSize + 'px',
                    'border-right-width': curlSize + 'px',
                    'left': '0',
                    'right': 'auto'
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
            leftHand.show();
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
    
    $('#zoomInBtn').click(function() {
        if (currentZoom < 1.5) {
            currentZoom += 0.1;
            applyZoom();
        }
    });
    
    $('#zoomOutBtn').click(function() {
        if (currentZoom > 0.6) {
            currentZoom -= 0.1;
            applyZoom();
        }
    });
    
    function applyZoom() {
        const newWidth = Math.floor(flipbookWidth * currentZoom);
        const newHeight = Math.floor(flipbookHeight * currentZoom);
        
        $('#flipbook').turn('size', newWidth, newHeight);
    }
    
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
    
    // Grid view (show all pages)
    $('#gridViewBtn').click(function() {
        alert('Grid view feature - showing all pages in a grid layout (feature can be enhanced)');
    });
    
    // Download original PDF
    $('#downloadBtn').click(function() {
        window.location.href = `/download-pdf/${flipbookId}`;
    });
    
    // Print flipbook
    $('#printBtn').click(function() {
        window.print();
    });
    
    // Toggle audio (page turn sound)
    let audioEnabled = true; // Enable sound by default
    
    // Create realistic page flip sound using real audio sample
    // This is a base64-encoded WAV file of an actual page flip sound
    const pageFlipSound = new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=');
    pageFlipSound.volume = 0.5;
    
    // Fallback: Generate realistic page flip sound if needed
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    function playPageFlipSound() {
        if (pageFlipSound && pageFlipSound.readyState >= 2) {
            // Use real audio file
            pageFlipSound.currentTime = 0;
            pageFlipSound.play().catch(() => {
                // Fallback to generated sound
                generatePageFlipSound();
            });
        } else {
            // Generate realistic page flip sound
            generatePageFlipSound();
        }
    }
    
    function generatePageFlipSound() {
        const duration = 0.25;
        const now = audioContext.currentTime;
        
        // Create multiple oscillators for a more realistic paper sound
        const oscillator1 = audioContext.createOscillator();
        const oscillator2 = audioContext.createOscillator();
        const noiseBuffer = createNoiseBuffer();
        const noiseSource = audioContext.createBufferSource();
        noiseSource.buffer = noiseBuffer;
        
        const gainNode = audioContext.createGain();
        const noiseGain = audioContext.createGain();
        const filter = audioContext.createBiquadFilter();
        
        // Set up filter for paper-like texture
        filter.type = 'bandpass';
        filter.frequency.value = 2000;
        filter.Q.value = 1;
        
        // Connect nodes
        oscillator1.connect(gainNode);
        oscillator2.connect(gainNode);
        noiseSource.connect(noiseGain);
        noiseGain.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Configure oscillators for swish sound
        oscillator1.type = 'sine';
        oscillator1.frequency.setValueAtTime(800, now);
        oscillator1.frequency.exponentialRampToValueAtTime(200, now + duration);
        
        oscillator2.type = 'triangle';
        oscillator2.frequency.setValueAtTime(1200, now);
        oscillator2.frequency.exponentialRampToValueAtTime(150, now + duration);
        
        // Envelope for realistic page flip
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(0.15, now + 0.02);
        gainNode.gain.exponentialRampToValueAtTime(0.05, now + duration * 0.6);
        gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
        
        noiseGain.gain.setValueAtTime(0.08, now);
        noiseGain.gain.exponentialRampToValueAtTime(0.001, now + duration * 0.5);
        
        // Start sounds
        oscillator1.start(now);
        oscillator1.stop(now + duration);
        oscillator2.start(now);
        oscillator2.stop(now + duration);
        noiseSource.start(now);
        noiseSource.stop(now + duration * 0.5);
    }
    
    function createNoiseBuffer() {
        const bufferSize = audioContext.sampleRate * 0.5;
        const buffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        return buffer;
    }
    
    // Add sound to page turns
    $('#flipbook').on('turned', function() {
        if (audioEnabled) {
            playPageFlipSound();
        }
    });
    
    $('#audioBtn').html('🔊'); // Set initial icon to enabled
    
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
            const response = await fetch(`/export/${flipbookId}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                $('.export-message').text('Building executable...');
                $('.export-details').text('Packaging flipbook with PyInstaller...');
                
                let attempts = 0;
                const maxAttempts = 60;
                
                const checkInterval = setInterval(async () => {
                    attempts++;
                    
                    try {
                        const checkResponse = await fetch(`/check-export/${flipbookId}`);
                        const checkData = await checkResponse.json();
                        
                        if (checkData.ready) {
                            clearInterval(checkInterval);
                            
                            $('.export-message').html('✓ .exe Ready for Download!');
                            $('.export-details').html(`
                                File size: ${checkData.size_mb} MB<br>
                                <a href="/download/${flipbookId}" 
                                   style="display: inline-block; margin-top: 15px; padding: 12px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                                   Download ${flipbookId}.exe
                                </a><br>
                                <button onclick="$('#exportStatus').hide();" 
                                   style="margin-top: 10px; padding: 8px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                   Close
                                </button>
                            `);
                            
                            btn.prop('disabled', false);
                        } else if (attempts >= maxAttempts) {
                            clearInterval(checkInterval);
                            $('.export-message').html('⚠ Build Timeout');
                            $('.export-details').html(`
                                The build is taking longer than expected.<br>
                                <button onclick="location.reload();" 
                                   style="margin-top: 15px; padding: 8px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                   Refresh and Try Again
                                </button>
                            `);
                            btn.prop('disabled', false);
                        }
                    } catch (err) {
                        console.error('Check error:', err);
                    }
                }, 5000);
            } else {
                throw new Error(data.error || 'Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            $('.export-message').html('✗ Export Failed');
            $('.export-details').html(`
                ${error.message}<br>
                <button onclick="$('#exportStatus').hide();" 
                   style="margin-top: 15px; padding: 8px 20px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;">
                   Close
                </button>
            `);
            btn.prop('disabled', false);
        }
    });
    
    initFlipbook();
});
