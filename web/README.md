# Fatigue Detection System - Web App

Responsive web interface for real-time fatigue detection monitoring. Works with the Flask backend API.

## Features
- Real-time video streaming display
- Live fatigue metrics dashboard
- Interactive fatigue gauge visualization
- Eye metric tracking (EAR, blink rate)
- Event logging
- Connection status indicator
- Responsive design (desktop & tablet)
- No backend server needed - connects to remote API

## Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Fatigue Detection Backend API running

## Installation

### Option 1: Serve Locally
```bash
# Install Python (if not already installed)
python -m http.server 8000

# Navigate to http://localhost:8000/templates/index.html
```

### Option 2: Use Node.js
```bash
npm install -g http-server
http-server

# Navigate to http://localhost:8080/templates/index.html
```

### Option 3: Direct Open
Simply open `templates/index.html` in a browser (limited functionality without CORS proxy)

## Configuration

Edit `static/app.js` to set the backend API URL:

```javascript
const API_BASE = 'http://your-backend-ip:5000/api';
```

## Usage

1. Start the backend API:
   ```bash
   cd backend
   python app.py
   ```

2. Open the web app:
   ```bash
   http://localhost:8000/templates/index.html
   ```

3. Position camera in front of your face
4. Monitor live metrics and fatigue status

## UI Components

### Header
- Logo and title
- Live indicator dot
- Current time

### Main Video Area
- MJPEG video stream from camera
- Alert overlay when drowsiness detected
- Quick stats cards (Status, EAR, Blinks/min, Total Blinks)

### Sidebar
- **Fatigue Score Gauge**: Circular progress indicator
- **Eye Metrics**: Face detection, closed frames, EAR bar
- **Blink History**: 20-second rolling chart
- **Event Log**: Status change history
- **API Status**: Connection indicator

## API Connection

The web app connects to:
- `GET http://localhost:5000/api/video` - MJPEG stream
- `GET http://localhost:5000/api/stats` - JSON metrics (polls every 500ms)

### CORS Handling

If backend doesn't have CORS enabled, use a proxy:

```bash
npm install -g cors-anywhere
cors-anywhere

# Then set in app.js:
const API_BASE = 'http://localhost:8080/http://backend-ip:5000/api';
```

## Customization

### Theme Colors
Edit CSS variables in `static/styles.css`:

```css
:root {
  --bg: #050a10;        /* Background */
  --accent: #00d4ff;    /* Primary color */
  --green: #00ff88;     /* Success/Awake */
  --yellow: #ffcc00;    /* Warning/Tired */
  --red: #ff3366;       /* Alert/Drowsy */
}
```

### Polling Interval
Change in `static/app.js`:

```javascript
setInterval(async () => { /* ... */ }, 500); // Change 500 to desired ms
```

### Thresholds
Adjust status colors and alerts in `app.js` based on fatigue scores

## Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome  | ✓ Full support |
| Firefox | ✓ Full support |
| Safari  | ✓ Full support (iOS 13+) |
| Edge    | ✓ Full support |
| IE 11   | ✗ Not supported |

## Troubleshooting

### "Cannot connect to backend API"
- Verify backend is running: `http://backend-ip:5000/api/health`
- Check firewall allows connections to port 5000
- Ensure CORS is enabled on backend

### Video stream not showing
- Confirm camera is connected to backend machine
- Check `/api/video` endpoint directly in browser
- Verify video stream URL in `static/app.js`

### Metrics not updating
- Check browser console for errors (F12)
- Verify `/api/stats` returns valid JSON
- Check network tab for failed requests

## Performance

- Video stream size: ~1-2 Mbps
- API polling: 2 requests/second
- CPU usage: <5% (just UI updates, processing on backend)
- Memory usage: ~50MB (browser)

## Production Deployment

### Netlify
```bash
# Deploy static files to Netlify
netlify deploy --prod --dir=web
```

### GitHub Pages
```bash
# Copy to gh-pages branch
git subtree push --prefix web origin gh-pages
```

### Traditional Hosting
Upload `web/` directory to any static hosting service.

## Development

### File Structure
```
web/
├── templates/
│   └── index.html      # Main HTML
├── static/
│   ├── styles.css      # Styling
│   └── app.js          # JavaScript logic
└── README.md
```

### Building
No build step required - pure HTML, CSS, JavaScript.

## Security Notes

- Backend should validate all requests
- Use HTTPS in production
- Implement authentication if exposing publicly
- Rate limit API endpoints

## License
MIT
