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
        
        updatePageInfo(1);
        updateThumbnails(1);
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
