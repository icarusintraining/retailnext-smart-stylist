// ============================================================================
// RetailNext Smart Stylist V2 - Complete Application
// Real data integration with live microphone recording
// ============================================================================

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const ENABLE_AUDIO_RESPONSES = true;

// ============================================================================
// State Management
// ============================================================================

const state = {
    conversationHistory: [],
    currentImage: null,
    recommendedItems: [],
    isConnected: false,
    isProcessing: false,

    // Microphone recording state
    isRecording: false,
    mediaRecorder: null,
    audioChunks: [],
    recordingStartTime: null,
    recordingTimer: null,
    audioStream: null
};

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('%c🛍️ RetailNext Smart Stylist V2', 'color: #667eea; font-size: 20px; font-weight: bold;');
    console.log('%cUsing real clothing data with RAG implementation', 'color: #10b981; font-size: 14px;');

    initializeApp();
    checkAPIConnection();
    setupEventListeners();
    addWelcomeMessage();
});

async function initializeApp() {
    // Check browser support for MediaRecorder
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('MediaRecorder API not supported in this browser');
        showNotification('Live microphone not supported in this browser. Please use Chrome, Firefox, or Edge.', 'warning');
    }

    console.log('✅ Application initialized');
}

// ============================================================================
// API Connection
// ============================================================================

async function checkAPIConnection() {
    updateStatus('connecting', 'Connecting...');

    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            state.isConnected = true;
            updateStatus('online', 'Connected');
            console.log(`✅ Connected to API - ${data.dataset_size} products loaded`);

            if (data.demo_mode) {
                showNotification('Demo mode is active', 'info');
            }
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        console.error('❌ Connection failed:', error);
        state.isConnected = false;
        updateStatus('offline', 'Offline');
        showNotification('Cannot connect to backend. Please ensure server is running.', 'error');
    }
}

function updateStatus(status, text) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');

    statusDot.className = `status-dot ${status}`;
    statusText.textContent = text;
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Send message
    document.getElementById('sendBtn').addEventListener('click', sendMessage);

    // Message input
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    // Image upload
    document.getElementById('uploadBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', handleImageUpload);
    document.getElementById('removeImageBtn').addEventListener('click', removeImage);

    // Microphone recording
    document.getElementById('micBtn').addEventListener('click', toggleRecording);
    document.getElementById('cancelRecordingBtn').addEventListener('click', cancelRecording);

    // Clear recommendations
    document.getElementById('clearBtn').addEventListener('click', clearRecommendations);

    // Modal
    document.getElementById('modalOverlay').addEventListener('click', closeModal);
    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
}

// ============================================================================
// Message Handling
// ============================================================================

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message && !state.currentImage) {
        showNotification('Please enter a message or upload an image', 'warning');
        return;
    }

    if (state.isProcessing) {
        showNotification('Please wait for the current request to complete', 'warning');
        return;
    }

    if (!state.isConnected) {
        showNotification('Not connected to server. Please check your connection.', 'error');
        return;
    }

    // Hide welcome hero
    const welcomeHero = document.getElementById('welcomeHero');
    if (welcomeHero) {
        welcomeHero.style.display = 'none';
    }

    // Add user message
    addUserMessage(message, state.currentImage);

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Prepare request
    const requestPayload = {
        message: message || "What do you think about this item?",
        conversation_history: state.conversationHistory,
        image_base64: state.currentImage,
        return_audio: ENABLE_AUDIO_RESPONSES
    };

    // Store in conversation history
    state.conversationHistory.push({
        role: 'user',
        content: message
    });

    // Clear current image
    const hadImage = !!state.currentImage;
    state.currentImage = null;
    removeImage();

    // Show typing indicator
    const typingId = addTypingIndicator();

    // Set processing state
    state.isProcessing = true;
    showLoading('Finding perfect items for you...');

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestPayload)
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Add assistant response
        addAssistantMessage(data.text_response);

        // Store in conversation history
        state.conversationHistory.push({
            role: 'assistant',
            content: data.text_response
        });

        // Display event context
        if (data.event_context) {
            displayEventContext(data.event_context);
        }

        // Display recommended items with REAL IMAGES
        if (data.recommended_items && data.recommended_items.length > 0) {
            displayRecommendedItems(data.recommended_items);
        }

        // Play audio response
        if (data.audio_response_base64 && ENABLE_AUDIO_RESPONSES) {
            playAudioResponse(data.audio_response_base64);
        }

        console.log('✅ Chat response received:', {
            items: data.recommended_items?.length || 0,
            apis: data.apis_used
        });

    } catch (error) {
        console.error('❌ Chat error:', error);
        removeTypingIndicator(typingId);

        addAssistantMessage(
            "I apologize, but I encountered an error. Please ensure the backend server is running and try again."
        );

        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        state.isProcessing = false;
        hideLoading();
    }
}

function addUserMessage(text, imageBase64 = null) {
    const container = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';

    let imageHTML = '';
    if (imageBase64) {
        imageHTML = `
            <img src="data:image/jpeg;base64,${imageBase64}"
                 style="max-width: 200px; max-height: 200px; border-radius: 0.75rem; margin-top: 0.5rem; display: block;"
                 alt="Uploaded image">
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${text ? `<p>${escapeHtml(text)}</p>` : ''}
            ${imageHTML}
        </div>
    `;

    container.appendChild(messageDiv);
    scrollToBottom();
}

function addAssistantMessage(text) {
    const container = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';

    // Format text with markdown-like syntax
    const formattedText = formatText(text);

    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${formattedText}
        </div>
    `;

    container.appendChild(messageDiv);
    scrollToBottom();
}

function addTypingIndicator() {
    const container = document.getElementById('messagesContainer');
    const typingDiv = document.createElement('div');
    const id = `typing-${Date.now()}`;

    typingDiv.id = id;
    typingDiv.className = 'message assistant';
    typingDiv.innerHTML = `
        <div class="message-bubble">
            <div style="display: flex; gap: 6px; align-items: center;">
                <div style="width: 8px; height: 8px; background: var(--gray-400); border-radius: 50%; animation: typing 1.4s infinite;"></div>
                <div style="width: 8px; height: 8px; background: var(--gray-400); border-radius: 50%; animation: typing 1.4s infinite 0.2s;"></div>
                <div style="width: 8px; height: 8px; background: var(--gray-400); border-radius: 50%; animation: typing 1.4s infinite 0.4s;"></div>
            </div>
        </div>
    `;

    container.appendChild(typingDiv);
    scrollToBottom();

    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function addWelcomeMessage() {
    addAssistantMessage(
        "G'day! I'm your AI Fashion Stylist. Tell me about your event, show me what you're looking for, or use your voice - I'm here to help you find the perfect outfit!"
    );
}

function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    container.scrollTop = container.scrollHeight;
}

function formatText(text) {
    let formatted = escapeHtml(text);

    // Bold text **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    // Price formatting
    formatted = formatted.replace(/\$(\d+)/g, '<span style="color: var(--primary); font-weight: 700;">$$1</span>');

    return formatted;
}

// ============================================================================
// Image Handling
// ============================================================================

function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        showNotification('Please select an image file', 'error');
        return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
        const base64 = event.target.result.split(',')[1];
        state.currentImage = base64;

        // Show preview
        const preview = document.getElementById('imagePreview');
        const img = document.getElementById('previewImg');
        img.src = event.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    state.currentImage = null;
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('fileInput').value = '';
}

// ============================================================================
// Live Microphone Recording (MediaRecorder API)
// ============================================================================

async function toggleRecording() {
    if (state.isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

async function startRecording() {
    try {
        // Request microphone permission
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            }
        });

        state.audioStream = stream;
        state.audioChunks = [];

        // Create MediaRecorder
        const mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4';
        state.mediaRecorder = new MediaRecorder(stream, { mimeType });

        // Handle data available
        state.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                state.audioChunks.push(event.data);
            }
        };

        // Handle recording stop
        state.mediaRecorder.onstop = () => {
            processRecording();
        };

        // Start recording
        state.mediaRecorder.start();
        state.isRecording = true;
        state.recordingStartTime = Date.now();

        // Update UI
        const micBtn = document.getElementById('micBtn');
        micBtn.classList.add('recording');
        document.getElementById('recordingPulse').style.display = 'block';
        document.getElementById('recordingStatus').style.display = 'flex';

        // Start timer
        updateRecordingTimer();
        state.recordingTimer = setInterval(updateRecordingTimer, 1000);

        console.log('🎤 Recording started');

    } catch (error) {
        console.error('❌ Microphone access denied:', error);
        showNotification('Microphone access denied. Please allow microphone access to use voice input.', 'error');
    }
}

function stopRecording() {
    if (state.mediaRecorder && state.isRecording) {
        state.mediaRecorder.stop();
        state.isRecording = false;

        // Stop all tracks
        if (state.audioStream) {
            state.audioStream.getTracks().forEach(track => track.stop());
        }

        // Clear timer
        if (state.recordingTimer) {
            clearInterval(state.recordingTimer);
            state.recordingTimer = null;
        }

        // Update UI
        const micBtn = document.getElementById('micBtn');
        micBtn.classList.remove('recording');
        document.getElementById('recordingPulse').style.display = 'none';
        document.getElementById('recordingStatus').style.display = 'none';

        console.log('🎤 Recording stopped');
    }
}

function cancelRecording() {
    if (state.mediaRecorder && state.isRecording) {
        state.audioChunks = []; // Clear chunks
        stopRecording();
        showNotification('Recording cancelled', 'info');
    }
}

function updateRecordingTimer() {
    if (!state.recordingStartTime) return;

    const elapsed = Math.floor((Date.now() - state.recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const seconds = (elapsed % 60).toString().padStart(2, '0');

    const timer = document.getElementById('recordingTimer');
    timer.textContent = `${minutes}:${seconds}`;

    // Auto-stop after 60 seconds
    if (elapsed >= 60) {
        stopRecording();
        showNotification('Maximum recording time reached (60s)', 'info');
    }
}

async function processRecording() {
    if (state.audioChunks.length === 0) {
        showNotification('No audio recorded', 'warning');
        return;
    }

    showLoading('Transcribing your voice...');

    try {
        // Create blob from chunks
        const mimeType = state.mediaRecorder.mimeType;
        const audioBlob = new Blob(state.audioChunks, { type: mimeType });

        console.log('🎤 Audio recorded:', {
            size: audioBlob.size,
            type: mimeType,
            duration: (Date.now() - state.recordingStartTime) / 1000
        });

        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        // Send to backend for transcription
        const response = await fetch(`${API_BASE_URL}/api/transcribe`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Transcription failed');
        }

        const data = await response.json();
        const transcript = data.transcript;

        console.log('✅ Transcribed:', transcript);

        // Set transcribed text in input
        document.getElementById('messageInput').value = transcript;

        hideLoading();
        showNotification('Voice transcribed successfully!', 'success');

        // Auto-send after 1 second
        setTimeout(() => {
            sendMessage();
        }, 1000);

    } catch (error) {
        console.error('❌ Transcription error:', error);
        hideLoading();
        showNotification(`Transcription failed: ${error.message}`, 'error');
    }
}

// ============================================================================
// Audio Playback
// ============================================================================

function playAudioResponse(base64Audio) {
    try {
        const audioPlayer = document.getElementById('audioPlayer');
        audioPlayer.src = `data:audio/mp3;base64,${base64Audio}`;
        audioPlayer.play();
        console.log('🔊 Playing audio response');
    } catch (error) {
        console.error('❌ Audio playback error:', error);
    }
}

// ============================================================================
// Event Context Display
// ============================================================================

function displayEventContext(context) {
    const card = document.getElementById('eventContextCard');
    const content = document.getElementById('eventContextContent');

    let html = '<div style="display: grid; gap: 0.5rem;">';

    const fields = [
        { key: 'event_type', label: 'Event' },
        { key: 'formality_level', label: 'Formality' },
        { key: 'season', label: 'Season' },
        { key: 'venue_type', label: 'Venue' },
        { key: 'gender', label: 'Style' }
    ];

    fields.forEach(({ key, label }) => {
        if (context[key] && context[key] !== 'unknown') {
            html += `
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--gray-600); font-size: 0.875rem;">${label}:</span>
                    <span style="font-weight: 600; font-size: 0.875rem;">${escapeHtml(context[key])}</span>
                </div>
            `;
        }
    });

    html += '</div>';

    content.innerHTML = html;
    card.style.display = 'block';
}

// ============================================================================
// Product Display (REAL IMAGES)
// ============================================================================

function displayRecommendedItems(items) {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = ''; // Clear existing

    state.recommendedItems = items;

    items.forEach((item, index) => {
        const card = createProductCard(item, index);
        grid.appendChild(card);
    });

    updateOutfitSummary();
}

function createProductCard(item, index) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.style.animationDelay = `${index * 0.03}s`;

    // Get price from enriched data
    const price = item.price || 65;

    // Get real image URL
    const imageUrl = item.imageUrl ||
        `https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/data/sample_clothes/sample_images/${item.id}.jpg`;

    // Get location info
    const location = item.storeLocation?.display || 'Aisle A, Rack 1';

    // Get stock info
    const stock = item.stock || { status: 'in_stock', label: 'In Stock' };
    const stockClass = stock.status === 'in_stock' ? 'in-stock' :
                       stock.status === 'low_stock' ? 'low-stock' : 'out-of-stock';

    // Match score
    const matchPercent = item.similarity_score ? Math.round(item.similarity_score * 100) : null;

    card.innerHTML = `
        <div class="product-image-container">
            <img src="${imageUrl}"
                 alt="${escapeHtml(item.productDisplayName)}"
                 class="product-image"
                 onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 80 80%22><rect fill=%22%23f3f4f6%22 width=%2280%22 height=%2280%22/><text x=%2240%22 y=%2245%22 font-size=%2210%22 text-anchor=%22middle%22 fill=%22%239ca3af%22>No image</text></svg>'"
                 loading="lazy">
        </div>
        <div class="product-details">
            <div>
                <h4 class="product-name">${escapeHtml(item.productDisplayName)}</h4>
                <div class="product-meta">
                    <span class="product-price">$${price}</span>
                    <span class="product-category">${escapeHtml(item.articleType)}</span>
                </div>
            </div>
            <div>
                <div class="product-location">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                        <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    <span>${escapeHtml(location)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <span class="stock-indicator ${stockClass}">${escapeHtml(stock.label)}</span>
                    ${matchPercent ? `<span class="match-badge">${matchPercent}% match</span>` : ''}
                </div>
            </div>
        </div>
    `;

    card.addEventListener('click', () => showProductModal(item, price, imageUrl));

    return card;
}

function updateOutfitSummary() {
    const summary = document.getElementById('outfitSummary');

    if (state.recommendedItems.length === 0) {
        summary.style.display = 'none';
        return;
    }

    const totalItems = state.recommendedItems.length;
    const totalPrice = state.recommendedItems.reduce((sum, item) => {
        return sum + (item.price || 65);
    }, 0);

    // Count items in stock
    const inStockCount = state.recommendedItems.filter(item =>
        !item.stock || item.stock.status !== 'out_of_stock'
    ).length;

    document.getElementById('totalItems').textContent = totalItems;
    document.getElementById('totalPrice').textContent = `$${totalPrice}`;

    summary.style.display = 'block';
}

function clearRecommendations() {
    state.recommendedItems = [];

    const grid = document.getElementById('productsGrid');
    grid.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">
                <svg width="100" height="100" viewBox="0 0 100 100" fill="none">
                    <circle cx="50" cy="50" r="40" stroke="#E5E7EB" stroke-width="2"/>
                    <path d="M50 30v40M30 50h40" stroke="#E5E7EB" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <h3>Start Your Style Journey</h3>
            <p>Ask me about your event and I'll show you personalized recommendations with real product images</p>
        </div>
    `;

    document.getElementById('eventContextCard').style.display = 'none';
    updateOutfitSummary();
}

// ============================================================================
// Product Modal
// ============================================================================

function showProductModal(item, price, imageUrl) {
    const modal = document.getElementById('productModal');
    const content = document.getElementById('modalContent');

    // Extract location and stock info
    const location = item.storeLocation || { aisle: 'Aisle A', rack: 'Rack 1', display: 'Aisle A, Rack 1' };
    const stock = item.stock || { status: 'in_stock', label: 'In Stock', quantity: 10 };
    const stockClass = stock.status === 'in_stock' ? 'in-stock' :
                       stock.status === 'low_stock' ? 'low-stock' : 'out-of-stock';

    // Retail context
    const context = item.retailContext || { perfectFor: ['Various occasions'], pairsWellWith: ['Accessories'] };

    content.innerHTML = `
        <img src="${imageUrl}"
             alt="${escapeHtml(item.productDisplayName)}"
             class="modal-product-image"
             onerror="this.style.display='none';">

        <h2 class="modal-product-name">${escapeHtml(item.productDisplayName)}</h2>

        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div class="modal-product-price">$${price}</div>
            <span class="stock-indicator ${stockClass}" style="font-size: 0.75rem;">${escapeHtml(stock.label)}</span>
            ${item.similarity_score ? `<span class="match-badge" style="font-size: 0.75rem;">${Math.round(item.similarity_score * 100)}% match</span>` : ''}
        </div>

        <!-- Store Location - KEY VALUE PROPOSITION -->
        <div class="modal-location-card" style="margin-bottom: 1rem;">
            <div class="modal-location-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                    <circle cx="12" cy="10" r="3"></circle>
                </svg>
            </div>
            <div class="modal-location-text">
                <h4>Find it in store</h4>
                <p>${escapeHtml(location.aisle)} → ${escapeHtml(location.rack)}</p>
            </div>
        </div>

        <!-- Product Details Grid -->
        <div class="modal-info-grid">
            <div class="modal-info-item">
                <div class="modal-info-label">Category</div>
                <div class="modal-info-value">${escapeHtml(item.articleType)}</div>
            </div>
            <div class="modal-info-item">
                <div class="modal-info-label">Color</div>
                <div class="modal-info-value">${escapeHtml(item.baseColour)}</div>
            </div>
            <div class="modal-info-item">
                <div class="modal-info-label">Season</div>
                <div class="modal-info-value">${escapeHtml(item.season)}</div>
            </div>
            <div class="modal-info-item">
                <div class="modal-info-label">Style</div>
                <div class="modal-info-value">${escapeHtml(item.usage || 'Casual')}</div>
            </div>
        </div>

        <!-- Perfect For Section - UPSELLING CONTEXT -->
        <div style="margin-bottom: 1rem; padding: 0.75rem; background: var(--gray-50); border-radius: 0.5rem;">
            <div style="font-size: 0.6875rem; color: var(--gray-500); text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 0.5rem;">Perfect for</div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                ${context.perfectFor.map(occ => `<span style="padding: 0.25rem 0.5rem; background: var(--white); border: 1px solid var(--gray-200); border-radius: 0.25rem; font-size: 0.75rem; font-weight: 500;">${escapeHtml(occ)}</span>`).join('')}
            </div>
        </div>

        <!-- Pairs Well With - CROSS-SELL -->
        <div style="margin-bottom: 1.25rem; padding: 0.75rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%); border-radius: 0.5rem; border: 1px dashed var(--primary);">
            <div style="font-size: 0.6875rem; color: var(--primary); text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 0.5rem; font-weight: 600;">Complete the look</div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                ${context.pairsWellWith.map(pair => `<span style="padding: 0.25rem 0.5rem; background: var(--white); border: 1px solid var(--primary); border-radius: 0.25rem; font-size: 0.75rem; font-weight: 500; color: var(--primary);">+ ${escapeHtml(pair)}</span>`).join('')}
            </div>
        </div>

        <button style="width: 100%; padding: 0.875rem; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%); color: white; border: none; border-radius: 0.625rem; font-weight: 600; font-size: 0.9375rem; cursor: pointer; transition: all 0.2s;"
                onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)'"
                onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
                onclick="alert('Item added to cart! Continue shopping or proceed to checkout.')">
            Add to Cart - $${price}
        </button>
    `;

    modal.classList.add('show');
}

function closeModal() {
    const modal = document.getElementById('productModal');
    modal.classList.remove('show');
}

// ============================================================================
// UI Helpers
// ============================================================================

function showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    text.textContent = message;
    overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'none';
}

function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);

    // Simple notification - could be enhanced with a toast library
    if (type === 'error') {
        console.error('❌', message);
    } else if (type === 'success') {
        console.log('✅', message);
    } else if (type === 'warning') {
        console.warn('⚠️', message);
    } else {
        console.info('ℹ️', message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// ============================================================================
// Utility Functions
// ============================================================================

// Check API connection every 30 seconds
setInterval(() => {
    if (!state.isProcessing) {
        checkAPIConnection();
    }
}, 30000);

// Add CSS animation for typing indicator
const style = document.createElement('style');
style.textContent = `
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 1;
        }
        30% {
            transform: translateY(-8px);
            opacity: 0.7;
        }
    }
`;
document.head.appendChild(style);

console.log('✅ Application ready');
console.log('💡 Features: Live microphone recording, real product images, RAG search');
