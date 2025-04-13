chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "captureVisibleTab") {
        chrome.tabs.captureVisibleTab({ format: "png", quality: 100 }, (dataUrl) => {
            if (chrome.runtime.lastError) {
                console.error("Background: Error capturing tab:", chrome.runtime.lastError.message);
                sendResponse(null); 
            } else {
                sendResponse(dataUrl);
                console.log("Background: DataURL sent!", dataUrl ? dataUrl.substring(0, 50) + "..." : null);
            }
        });
        return true; 
    }
});