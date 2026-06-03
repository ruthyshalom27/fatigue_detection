# Fatigue Detection System - Mobile App

React Native mobile application for real-time fatigue detection via camera feed streaming from the backend API.

## Features
- Real-time video streaming from backend
- Fatigue status monitoring
- Blink rate tracking
- Eye Aspect Ratio (EAR) visualization
- Responsive UI for Android and iOS

## Prerequisites
- Node.js 14+ and npm/yarn
- React Native CLI: `npm install -g react-native-cli`
- Android SDK (for Android) or Xcode (for iOS)
- Python backend running on `http://localhost:5000` (or configure API_URL)

## Installation

### Setup React Native Project
```bash
npx react-native init FatigueDetectionApp
cd FatigueDetectionApp
npm install
```

### Install Dependencies
```bash
npm install axios react-native-svg react-native-gesture-handler
```

### Configure API Connection
Edit `src/config.js`:
```javascript
export const API_URL = 'http://YOUR_BACKEND_IP:5000/api';
```

## Project Structure
```
fatigue-detection-app/
├── src/
│   ├── screens/
│   │   ├── HomeScreen.js      # Main monitoring screen
│   │   └── StatsScreen.js     # Detailed statistics
│   ├── components/
│   │   ├── VideoStream.js     # Streaming video display
│   │   ├── FatigueGauge.js    # Circular gauge visualization
│   │   └── StatCard.js        # Metric cards
│   ├── config.js              # API configuration
│   └── App.js                 # App entry point
├── package.json
└── README.md
```

## Running

### Android
```bash
npm run android
```

### iOS
```bash
npm run ios
```

## API Integration

The mobile app connects to the backend at `/api/video` and `/api/stats`:

- **`GET /api/video`** - MJPEG video stream
- **`GET /api/stats`** - Current fatigue metrics (JSON)

Example stats response:
```json
{
  "status": "Awake",
  "fatigue_score": 25,
  "ear": 0.35,
  "blink_rate": 18.5,
  "blink_count": 12,
  "face_detected": true,
  "closed_frames": 0
}
```

## Build for Production

### Android APK
```bash
cd android && ./gradlew assembleRelease
```

### iOS App
```bash
xcodebuild -workspace ios/FatigueDetectionApp.xcworkspace -scheme FatigueDetectionApp -configuration Release
```

## Troubleshooting

- **Cannot connect to API**: Ensure backend is running and firewall allows connections
- **Video not streaming**: Check backend video endpoint is accessible
- **Build errors**: Clear caches with `npm install --legacy-peer-deps`

## Future Enhancements
- Local ML model inference (TensorFlow Lite)
- Offline detection capability
- Push notifications for drowsiness alerts
- Session logging and history
