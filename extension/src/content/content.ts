// Track scroll depth percent
let maxScrollDepth = 0;

function calculateScrollDepth() {
  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
  if (scrollHeight > 0) {
    const percent = Math.round((scrollTop / scrollHeight) * 100);
    maxScrollDepth = Math.max(maxScrollDepth, percent);
    
    // Notify background script of scroll progression
    chrome.runtime.sendMessage({
      type: "SCROLL_UPDATE",
      depth: maxScrollDepth
    });
  }
}

// Throttle scroll checks
let scrollTimeout: any = null;
window.addEventListener("scroll", () => {
  if (!scrollTimeout) {
    scrollTimeout = setTimeout(() => {
      calculateScrollDepth();
      scrollTimeout = null;
    }, 1000);
  }
});

// Helper to strip scripts and extract raw visible text
function extractCleanText(): string {
  const bodyClone = document.body.cloneNode(true) as HTMLElement;
  
  // Remove non-content elements
  const tagsToRemove = ["script", "style", "noscript", "iframe", "header", "footer", "nav", "ads"];
  tagsToRemove.forEach(tag => {
    const elements = bodyClone.getElementsByTagName(tag);
    while (elements.length > 0) {
      elements[0].parentNode?.removeChild(elements[0]);
    }
  });

  return bodyClone.innerText || bodyClone.textContent || "";
}

// Trigger capture on load once document is settled
window.addEventListener("load", () => {
  setTimeout(() => {
    const pageText = extractCleanText();
    
    chrome.runtime.sendMessage({
      type: "PAGE_VISITED",
      url: window.location.href,
      title: document.title,
      text: pageText
    });
  }, 2000); // 2-second grace period for dynamic contents to render
});
