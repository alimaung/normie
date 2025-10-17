# 🚀 Stoplight API Documentation Offline Mirror Server

## 📋 Overview

This Flask server provides a **fully interactive offline mirror** of Stoplight-based API documentation. It solves the problem of broken JavaScript functionality in offline Stoplight web component documentation by injecting custom JavaScript that recreates all interactive features.

### 🎯 Problem Statement

- **Stoplight Web Components** rely on a 2MB+ JavaScript framework (`web-components.min.js`)
- **Offline mirrors** have broken functionality (no tabs, no expansion, no interactivity)
- **Standard HTML serving** doesn't handle Stoplight's custom elements
- **661+ pages** need consistent interactive functionality

### ✅ Solution

**Flask server** that:
1. **Serves HTML files** from the mirrored content directory
2. **Automatically injects custom JavaScript** into every HTML page
3. **Recreates all Stoplight functionality** with framework-independent JavaScript
4. **Provides enhanced offline experience** with additional user controls

---

## 🏗️ Architecture

### Core Components

```
Flask Server
├── HTML File Serving (with JS injection)
├── Asset Management (CSS, JS, images)
├── Custom JavaScript Engine
└── Enhanced User Controls
```

### Request Flow

```
User Request → Flask Router → Load HTML → Inject Custom JS → Enhanced HTML Response
```

---

## 🎮 Interactive Elements Specification

### 1. **HTTP Status Code Tabs**
```html
<div role="tablist">
  <div role="tab" aria-selected="true" data-key="200">200</div>
  <div role="tab" aria-selected="false" data-key="400">400</div>
  <!-- 401, 403, 429, 500, 503, etc. -->
</div>
```

**Functionality:**
- ✅ Tab switching between status codes
- ✅ Content panel updates per status
- ✅ Visual state management (selected/unselected)
- ✅ Coordinated updates with right panel

### 2. **Schema Tree Navigation**
```html
<div class="sl-flex sl-justify-center sl-w-8" role="button">
  <svg data-icon="chevron-down" class="fa-chevron-down">
</div>
```

**Functionality:**
- ✅ Expand/collapse object properties
- ✅ Nested tree structure support
- ✅ Multi-level hierarchy (data-level="0", data-level="1")
- ✅ Chevron icon rotation
- ✅ Parent-child relationship management

### 3. **Content-Type Dropdown**
```html
<button aria-label="Response Body Content Type" aria-haspopup="listbox">
  <div>application/json</div>
  <svg data-icon="chevron-down">
</button>
```

**Functionality:**
- ✅ Dropdown menu display
- ✅ Option selection (application/json, application/xml, etc.)
- ✅ Content updates based on selection
- ✅ Visual state updates

### 4. **Collapsible Panels System**

#### Auth Panel
```html
<div class="sl-panel" data-test="try-it-auth">
  <div aria-expanded="true" role="button" class="sl-panel__titlebar">
    <svg data-icon="caret-down">
    Auth
  </div>
  <div class="sl-panel__content-wrapper">
    <!-- API key input -->
  </div>
</div>
```

#### Parameters Panel
```html
<div class="sl-panel">
  <div aria-expanded="true" role="button" class="sl-panel__titlebar">
    Parameters
  </div>
  <div class="sl-panel__content-wrapper">
    <!-- Parameter inputs: from, from_date, methods, page, per_page, etc. -->
  </div>
</div>
```

#### Security Panel
```html
<div class="sl-panel">
  <div aria-expanded="true" role="button" class="sl-panel__titlebar">
    Security: API Key
  </div>
  <div class="sl-panel__content-wrapper">
    <!-- Security documentation -->
  </div>
</div>
```

**Functionality:**
- ✅ Individual panel expand/collapse
- ✅ Caret icon rotation
- ✅ Content visibility toggle
- ✅ aria-expanded state management

### 5. **Try It Panel Functionality**

#### Form Management
```html
<input id="id_auth_apikey_XXX" aria-label="apikey" type="password" placeholder="123">
<!-- Multiple parameter inputs -->
<input aria-label="from" placeholder="example: 2025-01-01 00:00:00">
<input aria-label="methods" placeholder="example: get,put">
```

#### Send API Request
```html
<button type="button" class="sl-button sl-bg-primary">Send API Request</button>
```

**Functionality:**
- ✅ Form input validation
- ✅ Parameter collection
- ✅ Offline mode handling
- ✅ Simulated API responses
- ✅ Response example highlighting

### 6. **Code Sample Management**

#### Request Sample Panel
```html
<button aria-label="Request Sample Language" aria-haspopup="true">
  Request Sample: Shell / cURL
  <svg data-icon="chevron-down">
</button>
```

#### Copy Functionality
```html
<button type="button" class="sl-button">
  <svg data-icon="copy" class="fa-copy">
</button>
```

**Functionality:**
- ✅ Language selection dropdown (Shell/cURL, JavaScript, Python, etc.)
- ✅ Code sample updates per language
- ✅ Copy to clipboard simulation
- ✅ Visual feedback for copy actions

### 7. **Navigation Enhancement**
```html
<a href="#/operations/getApiRequestHistory" class="ElementsTableOfContentsItem">
```

**Functionality:**
- ✅ Hash-based navigation
- ✅ Cross-page navigation
- ✅ Breadcrumb management
- ✅ Deep linking support

---

## 🛠️ Technical Implementation

### Flask Server Structure

```python
from flask import Flask, send_from_directory
from pathlib import Path

app = Flask(__name__)
MIRROR_DIR = Path("expand_mirror_optimized")

@app.route('/')
def index():
    return serve_enhanced_html("index.html")

@app.route('/<path:filename>')
def serve_file(filename):
    if filename.endswith('.html'):
        return serve_enhanced_html(filename)
    else:
        return send_from_directory(MIRROR_DIR, filename)

def serve_enhanced_html(filename):
    # Load HTML file
    # Inject custom JavaScript
    # Return enhanced HTML
```

### Custom JavaScript Architecture

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive systems
    initializeTabs();
    initializePanels();
    initializeTreeNavigation();
    initializeDropdowns();
    initializeCopyButtons();
    initializeForms();
    initializeNavigation();
    addUserControls();
    
    // Auto-expand functionality
    setTimeout(autoExpandAll, 1000);
});
```

### JavaScript Modules

#### 1. Tab System Manager
```javascript
function initializeTabs() {
    const tabLists = document.querySelectorAll('[role="tablist"]');
    // Handle tab switching, content updates, visual states
}
```

#### 2. Panel System Manager
```javascript
function initializePanels() {
    const panels = document.querySelectorAll('.sl-panel__titlebar[role="button"]');
    // Handle expand/collapse, icon rotation, content visibility
}
```

#### 3. Tree Navigation Manager
```javascript
function initializeTreeNavigation() {
    const treeToggles = document.querySelectorAll('[data-icon="chevron-down"]');
    // Handle schema tree expansion, nested relationships
}
```

#### 4. Dropdown System Manager
```javascript
function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('[aria-haspopup="listbox"]');
    // Handle dropdown menus, option selection, content updates
}
```

#### 5. Copy Button Manager
```javascript
function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('[data-icon="copy"]');
    // Handle clipboard simulation, visual feedback
}
```

#### 6. Form System Manager
```javascript
function initializeForms() {
    const sendButtons = document.querySelectorAll('button:contains("Send API Request")');
    // Handle form validation, offline responses, example highlighting
}
```

---

## 🎨 Enhanced User Experience

### Additional Controls

#### Expand/Collapse All Button
```javascript
function addUserControls() {
    const controlsDiv = document.createElement('div');
    controlsDiv.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 9999;';
    
    // Expand All button
    const expandBtn = document.createElement('button');
    expandBtn.innerHTML = '🔍 Expand All';
    expandBtn.addEventListener('click', expandAllSections);
    
    // Collapse All button
    const collapseBtn = document.createElement('button');
    collapseBtn.innerHTML = '📁 Collapse All';
    collapseBtn.addEventListener('click', collapseAllSections);
}
```

### Offline API Testing Simulation
```javascript
function handleApiRequest(formData) {
    // Validate inputs
    const apiKey = formData.get('apikey');
    const parameters = collectParameters();
    
    // Show appropriate response example
    if (!apiKey) {
        highlightStatusTab('401');
        showMessage('API key required');
    } else {
        highlightStatusTab('200');
        showMessage('Example response shown below');
    }
    
    // Scroll to response section
    scrollToResponseExamples();
}
```

---

## 📂 Directory Structure

```
flask_mirror_server/
├── app.py                          # Main Flask application
├── templates/
│   └── enhanced_template.html      # Optional: template for common elements
├── static/
│   └── custom_stoplight.js         # Custom JavaScript engine
├── mirror_content/                 # Mirrored HTML files directory
│   ├── index.html
│   ├── operation_*.html
│   ├── path_*.html
│   └── assets/                     # CSS, JS, images
├── config.py                       # Configuration settings
└── README.md                       # This file
```

---

## 🚀 Usage Instructions

### Development Setup

1. **Install Flask**
```bash
pip install flask
```

2. **Place mirrored content**
```bash
# Copy your mirrored files to mirror_content/
cp -r expand_mirror_optimized/ ./mirror_content/
```

3. **Run the server**
```bash
python app.py
```

4. **Access enhanced documentation**
```
http://localhost:8000
```

### Production Deployment

```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Using Docker
docker build -t api-docs-mirror .
docker run -p 8000:8000 api-docs-mirror
```

---

## ⚙️ Configuration Options

### Environment Variables

```bash
# Server configuration
FLASK_ENV=production
FLASK_PORT=8000
FLASK_HOST=0.0.0.0

# Mirror content directory
MIRROR_CONTENT_DIR=./mirror_content

# JavaScript injection settings
ENABLE_AUTO_EXPAND=true
ENABLE_USER_CONTROLS=true
ENABLE_OFFLINE_TESTING=true
```

### Customization Options

```python
# config.py
class Config:
    MIRROR_DIR = os.environ.get('MIRROR_CONTENT_DIR', './mirror_content')
    AUTO_EXPAND_DELAY = 1000  # milliseconds
    ENABLE_DEBUG_CONSOLE = False
    CUSTOM_CSS_INJECTION = True
    ENHANCED_COPY_FEEDBACK = True
```

---

## 🔧 Development Guidelines

### Adding New Interactive Elements

1. **Identify the element structure** in HTML
2. **Create JavaScript handler** in appropriate module
3. **Add to initialization sequence** in main function
4. **Test across multiple pages** to ensure consistency

### JavaScript Module Pattern

```javascript
// modules/tab_system.js
function TabSystemManager() {
    function initialize() {
        // Setup logic
    }
    
    function handleTabClick(event) {
        // Click handling
    }
    
    function updateTabContent(tabKey) {
        // Content updates
    }
    
    return {
        initialize,
        updateTabContent
    };
}
```

### Error Handling

```javascript
function safeInitialize(initFunction, componentName) {
    try {
        initFunction();
        console.log(`✅ ${componentName} initialized successfully`);
    } catch (error) {
        console.warn(`⚠️ ${componentName} initialization failed:`, error);
        // Graceful degradation
    }
}
```

---

## 📊 Performance Considerations

### JavaScript Optimization
- **Lazy loading** of complex functionality
- **Event delegation** for dynamic elements
- **Debounced** user interactions
- **Minimal DOM queries** with caching

### Server Optimization
- **File caching** for static assets
- **Gzip compression** for HTML/JS
- **CDN integration** for assets (optional)
- **Memory-efficient** file handling

### Browser Compatibility
- **ES6+ features** with fallbacks
- **Cross-browser** event handling
- **Mobile-responsive** interactions
- **Accessibility** compliance

---

## 🧪 Testing Strategy

### Functional Testing
```javascript
// Test tab switching
function testTabSystem() {
    const tabs = document.querySelectorAll('[role="tab"]');
    tabs[1].click();
    assert(tabs[1].getAttribute('aria-selected') === 'true');
}

// Test panel expansion
function testPanelExpansion() {
    const panel = document.querySelector('.sl-panel__titlebar');
    panel.click();
    assert(panel.getAttribute('aria-expanded') === 'false');
}
```

### Cross-Page Testing
- **Consistent behavior** across all 661 pages
- **State persistence** during navigation
- **Performance** with large numbers of interactive elements

### User Experience Testing
- **Mobile device** compatibility
- **Keyboard navigation** support
- **Screen reader** accessibility
- **Load time** optimization

---

## 🔮 Future Enhancements

### Advanced Features
- **Search functionality** across documentation
- **Bookmarking system** for favorite endpoints
- **Dark/Light theme** toggle
- **Export functionality** (PDF, print-friendly)

### API Testing Enhancements
- **Mock API responses** based on real data
- **Request/Response validation**
- **API key management** (local storage)
- **Request history** tracking

### Performance Improvements
- **Service Worker** for offline functionality
- **Progressive loading** of large documentation
- **Background updates** for dynamic content
- **Analytics** for usage tracking

---

## 📈 Success Metrics

### Functionality Coverage
- ✅ **100% interactive element** recreation
- ✅ **Cross-page consistency** maintained
- ✅ **Enhanced user controls** added
- ✅ **Offline API testing** simulation

### Performance Targets
- ⚡ **< 2 seconds** initial page load
- ⚡ **< 500ms** interaction response time
- ⚡ **< 100MB** total memory usage
- ⚡ **99%+ uptime** for local serving

### User Experience Goals
- 🎯 **Better than original** Stoplight experience
- 🎯 **Fully offline** functionality
- 🎯 **Enhanced navigation** with user controls
- 🎯 **Accessible** to all users

---

## 📞 Support and Contributing

### Issues and Questions
- Create GitHub issues for bugs or feature requests
- Use discussions for questions and improvements
- Follow code style guidelines for contributions

### Development Setup
```bash
git clone <repository>
cd flask-stoplight-mirror
pip install -r requirements.txt
python app.py
```

### Contributing Guidelines
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request with detailed description

---

**🎉 Result: A fully functional, enhanced offline API documentation experience that surpasses the original Stoplight web component functionality!**







