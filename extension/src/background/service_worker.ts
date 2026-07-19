// Local Ingestion Endpoint Configuration
const API_INGEST_URL = "http://localhost:8000/api/v1/capture/ingest";

// Store metrics for active tabs
interface TabTelemetry {
  startTime: number;
  lastActiveTime: number;
  scrollDepth: number;
}

const activeTabs: Record<number, TabTelemetry> = {};

// Listen for tab activation changes
chrome.tabs.onActivated.addListener((activeInfo) => {
  const tabId = activeInfo.tabId;
  const now = Date.now();
  
  // Track dwell time transitions
  activeTabs[tabId] = {
    startTime: now,
    lastActiveTime: now,
    scrollDepth: 0
  };
});

// Listen for messages from content scripts (e.g. scroll updates or selections)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SCROLL_UPDATE") {
    const tabId = sender.tab?.id;
    if (tabId && activeTabs[tabId]) {
      activeTabs[tabId].scrollDepth = Math.max(activeTabs[tabId].scrollDepth, message.depth);
    }
  }
  
  if (message.type === "PAGE_VISITED") {
    const tabId = sender.tab?.id;
    const now = Date.now();
    const metrics = activeTabs[tabId || 0] || { startTime: now, scrollDepth: 0 };
    const dwellTime = Math.round((now - metrics.startTime) / 1000);
    
    const payload = {
      url: message.url,
      title: message.title,
      cleaned_text: message.text,
      metrics: {
        scroll_depth_percent: metrics.scrollDepth,
        dwell_time_seconds: dwellTime
      }
    };
    
    // Post captured data to local memory layer ingest server
    sendToMemoryLayer(payload);
  }
});

async function sendToMemoryLayer(payload: any) {
  try {
    const response = await fetch(API_INGEST_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });
    
    if (response.ok) {
      console.log(`Successfully ingested memory: ${payload.url}`);
    } else {
      console.error(`Memory ingestion failed for ${payload.url}: Status ${response.status}`);
    }
  } catch (error) {
    console.error(`Could not connect to local Internet Memory Layer service: ${error}`);
  }
}
