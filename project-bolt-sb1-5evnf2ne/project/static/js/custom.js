document.addEventListener('DOMContentLoaded', function() {
    // Initialize all audio players
    const players = Plyr.setup('.audio-player', {
        controls: [
            'play',
            'progress',
            'current-time',
            'mute',
            'volume',
            'download'
        ]
    });

    // Animate elements when they enter viewport
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.card');
        elements.forEach(element => {
            const position = element.getBoundingClientRect();
            if(position.top < window.innerHeight && position.bottom > 0) {
                element.classList.add('slide-up');
            }
        });
    };

    window.addEventListener('scroll', animateOnScroll);
    // Initial animation call
    animateOnScroll();

    // Add to playlist functionality
    const addToPlaylistForm = document.getElementById('addToPlaylistForm');
    if (addToPlaylistForm) {
        addToPlaylistForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const playlistId = formData.get('playlist_id');
            const musicId = formData.get('music_id');
            
            if (!playlistId) {
                alert('Please select a playlist.');
                return;
            }
            
            // Here you'd typically send an AJAX request to update the playlist
            // For demonstration, we'll show a success message
            const modal = bootstrap.Modal.getInstance(document.getElementById('addToPlaylistModal'));
            modal.hide();
            
            // Show success message
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                Added to playlist successfully!
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // Insert alert before the first child of the main content
            const mainContent = document.querySelector('main');
            mainContent.insertBefore(alertDiv, mainContent.firstChild);
            
            // Auto-dismiss after 3 seconds
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }, 3000);
        });
    }

    // Implement search functionality
    const searchForm = document.querySelector('form[action="/music/"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="search"]');
        const resultsContainer = document.getElementById('searchResults');
        
        if (searchInput && resultsContainer) {
            searchInput.addEventListener('input', function(e) {
                const query = e.target.value.trim();
                
                if (query.length < 2) {
                    resultsContainer.innerHTML = '';
                    resultsContainer.classList.add('d-none');
                    return;
                }
                
                // In a real application, you'd send an AJAX request to search for music
                // For this example, we'll simulate results
                const mockResults = [
                    { id: 1, title: 'Sample Song 1', artist: 'Artist 1' },
                    { id: 2, title: 'Another Track', artist: 'Artist 2' },
                    { id: 3, title: 'My Favorite', artist: 'Artist 3' }
                ].filter(item => 
                    item.title.toLowerCase().includes(query.toLowerCase()) || 
                    item.artist.toLowerCase().includes(query.toLowerCase())
                );
                
                if (mockResults.length > 0) {
                    resultsContainer.innerHTML = mockResults.map(result => `
                        <a href="/music/${result.id}/" class="list-group-item list-group-item-action">
                            <div class="d-flex justify-content-between">
                                <h6 class="mb-0">${result.title}</h6>
                                <small>${result.artist}</small>
                            </div>
                        </a>
                    `).join('');
                    resultsContainer.classList.remove('d-none');
                } else {
                    resultsContainer.innerHTML = `
                        <div class="list-group-item">No results found</div>
                    `;
                    resultsContainer.classList.remove('d-none');
                }
            });
            
            // Hide results when clicking outside
            document.addEventListener('click', function(e) {
                if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
                    resultsContainer.classList.add('d-none');
                }
            });
        }
    }

    // Initialize tabs if they exist
    const tabElems = document.querySelectorAll('[data-bs-toggle="tab"]');
    if (tabElems.length > 0) {
        tabElems.forEach(tabEl => {
            tabEl.addEventListener('shown.bs.tab', function (event) {
                // Store the active tab in local storage
                localStorage.setItem('activeTab', event.target.id);
            });
        });
        
        // Restore active tab
        const activeTab = localStorage.getItem('activeTab');
        if (activeTab) {
            const tab = document.getElementById(activeTab);
            if (tab) {
                const bsTab = new bootstrap.Tab(tab);
                bsTab.show();
            }
        }
    }
});