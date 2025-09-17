# Live Status Indicator

The directory page now has a **real-time live status indicator** that shows the current state of the background update service.

## Features

### 🔴 Status States

- **🟢 Live**: Service running, data updated within last 5 minutes (green, pulsing)
- **🔵 Updating**: Currently processing Excel file (blue, spinning)  
- **🟡 Starting**: Service initializing (orange, blinking)
- **🟡 Stale**: No updates in >5 minutes (orange, warning)
- **⚫ Offline**: Background service not running (gray)

### 📊 What It Shows

- **Status Text**: Current state (Live, Updating, Starting, etc.)
- **Last Update Time**: When data was last refreshed (e.g., "Last: 14:32")
- **Hover Info**: Next update time, minutes since last update, compression status

### 🔄 Auto-Updates

- **Polls every 10 seconds** to check service status
- **Updates instantly** when status changes
- **Shows visual animations** for different states

## API Endpoints

### GET `/directory/status/`
Returns current service status:
```json
{
    "status": "live",
    "status_text": "Live", 
    "status_class": "live",
    "is_running": true,
    "last_update": 1725908315,
    "time_since_update": 45,
    "has_compressed": true,
    "update_interval": 120,
    "next_update_in": 75
}
```

### POST `/directory/trigger-update/`
Manually trigger an update:
```json
{
    "success": true,
    "message": "Update triggered successfully"
}
```

## Fixed Statistics

The stat cards now show **accurate real-time counts**:

- **All**: Total entries
- **Approved**: Fully approved items
- **First Use**: Approved for first order only
- **Processing**: Currently being processed
- **Rejected**: Not approved
- **Aircraft Relevant**: Relevant for aviation

All counts update automatically when data refreshes!

## Visual Design

- **Apple-style design** with smooth animations
- **Color-coded status** with meaningful animations:
  - Green pulse = healthy and live
  - Blue spin = actively updating  
  - Orange blink = starting up
  - Gray = offline/problems
- **Hover effects** for additional information
- **Responsive** layout that works on all screen sizes

The live status indicator provides **instant feedback** on your data freshness and service health!

