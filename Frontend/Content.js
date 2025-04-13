console.log("Is this working?!");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Content Script: Received message:", message);

    if (message.action === "takeScreenshot") {
        const { scrollHeight, clientHeight } = document.documentElement;
        const devicePixelRatio = window.devicePixelRatio || 1;

        let capturedHeight = 0;
        let capturedImages = [];

        const captureAndScroll = () => {
            const scrollAmount = clientHeight * devicePixelRatio;

            chrome.runtime.sendMessage({ action: "captureVisibleTab" }, (dataUrl) => {
                console.log("Content Script: Got dataUrl:", dataUrl ? dataUrl.substring(0, 50) + "..." : null);
                if (dataUrl) {
                    capturedImages.push(dataUrl);
                } else {
                    console.error("Content Script: Received empty dataUrl");
                    sendResponse({ dataUrl: [] }); 
                    return;
                }

                capturedHeight += scrollAmount;
                console.log("Content Script: Captured Height:", capturedHeight, "Total Height:", scrollHeight * devicePixelRatio);
                console.log("Content Script: Captured Images Array:", capturedImages.length);

                if (capturedHeight < scrollHeight * devicePixelRatio + 10) { 
                    window.scrollTo(0, capturedHeight);
                    setTimeout(captureAndScroll, 500); 
                } else {
                    console.log("Content Script: Sending final response", capturedImages.length);
                    sendResponse({ dataUrl: capturedImages });
                }
            });
        };

        window.scrollTo(0, 0); 
        setTimeout(captureAndScroll, 200); 
        return true; 
    }
});