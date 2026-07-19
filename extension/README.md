# Internet Memory Layer: Browser Ingestion Extension

This extension captures browsing context passively, filters noisy layouts, and sends telemetry metadata payloads directly to the local backend memory engines.

## Core Features
1. **Passive Scraper** ([content.ts](src/content/content.ts)): Clean text visible regions, removing advertising elements, structural scripts, styles, and navigations.
2. **Telemetry Heartbeat** ([service_worker.ts](src/background/service_worker.ts)): Periodically captures scroll offsets, page focus duration parameters, and title changes.
3. **Popup Panel** ([popup.html](popup.html)): Allows toggling active capture trackers and shows server connection checks.

## Quick Install (Developer Mode)
1. Go to Chrome settings -> Extensions (`chrome://extensions/`).
2. Turn on **Developer Mode** (top right toggle).
3. Click **Load unpacked** and select the `/extension` directory in this workspace.
