// Ingestion and Snapshot API Configurations
const API_INGEST_URL = "http://localhost:8000/api/v1/capture/ingest";
const API_SNAPSHOT_URL = "http://localhost:8000/api/v1/timeline/snapshot";

interface TabTelemetry {
  startTime: number;
  lastActiveTime: number;
  scrollDepth: number;
  title: string;
  url: string;
}

const activeTabs: Record<number, TabTelemetry> = {};

// Listen for tab activation changes
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  const tabId = activeInfo.tabId;
  const now = Date.now();
  
  try {
    const tab = await chrome.tabs.get(tabId);
    activeTabs[tabId] = {
      startTime: now,
      lastActiveTime: now,
      scrollDepth: 0,
      title: tab.title || "",
      url: tab.url || ""
    };
    
    // Post initial focus snapshot to timeline
    sendSnapshot(tabId, "focus");
  } catch (err) {
    console.error(`Failed to get tab info: ${err}`);
  }
});

// Periodic heartbeat monitoring active scroll depths and state snapshots
setInterval(() => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length > 0 && tabs[0].id) {
      const activeTabId = tabs[0].id;
      if (activeTabs[activeTabId]) {
        sendSnapshot(activeTabId, "heartbeat");
      }
    }
  });
}, 10000); // Trigger snapshot updates every 10 seconds

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
    const metrics = activeTabs[tabId || 0] || { startTime: now, scrollDepth: 0, title: "", url: "" };
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
    
    sendToMemoryLayer(payload);
  }
});

async function sendSnapshot(tabId: number, triggerType: string) {
  const metrics = activeTabs[tabId];
  if (!metrics || !metrics.url || metrics.url.startsWith("chrome://")) return;

  const payload = {
    url: metrics.url,
    title: metrics.title,
    scroll_depth_percent: metrics.scrollDepth,
    trigger_event: triggerType,
    timestamp: new Date().toISOString()
  };

  try {
    await fetch(API_SNAPSHOT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (error) {
    console.error(`Timeline snapshot capture failed: ${error}`);
  }
}

async function sendToMemoryLayer(payload: any) {
  try {
    const response = await fetch(API_INGEST_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
