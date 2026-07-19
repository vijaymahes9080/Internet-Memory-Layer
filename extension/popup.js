const API_BASE = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  checkBackendStatus();
  
  // Handle Dashboard Click
  document.getElementById("open-dashboard").addEventListener("click", () => {
    chrome.tabs.create({ url: `${API_BASE}/docs` });
  });

  // Handle Ingest Toggle change
  const toggle = document.getElementById("ingest-toggle");
  toggle.addEventListener("change", (e) => {
    chrome.storage.local.set({ ingestEnabled: e.target.checked }, () => {
      console.log(`Ingestion set to: ${e.target.checked}`);
    });
  });

  // Retrieve current toggle state
  chrome.storage.local.get("ingestEnabled", (data) => {
    if (data.ingestEnabled !== undefined) {
      toggle.checked = data.ingestEnabled;
    }
  });
});

async function checkBackendStatus() {
  const dot = document.getElementById("status-dot");
  const txt = document.getElementById("status-text");
  
  try {
    const res = await fetch(API_BASE);
    if (res.ok) {
      dot.classList.remove("offline");
      txt.innerText = "Online";
    } else {
      setOffline(dot, txt);
    }
  } catch (err) {
    setOffline(dot, txt);
  }
}

function setOffline(dot, txt) {
  dot.classList.add("offline");
  txt.innerText = "Offline";
  document.getElementById("memories-count").innerText = "0";
}
