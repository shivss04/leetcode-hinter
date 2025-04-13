document.getElementById("takeScreenshotBtn").addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];
        chrome.tabs.sendMessage(activeTab.id, { action: "takeScreenshot" }, (response) => {
            if (!response || !response.dataUrl || response.dataUrl.length === 0) {
                displayError("No images captured or invalid response.");
                return;
            }

            const images = response.dataUrl;
            const base64Image = images[0]; 

            const apiUrl = "<LAMBDA ENDPOINT URL>";
            const imageData = JSON.stringify({ 'image': base64Image });

            fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: imageData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(`HTTP error! status: ${response.status}, body: ${JSON.stringify(err)}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data && data.body) {
                    const hintText = data.body.replace(/^"|"$/g, '');
                    displayHint(hintText);
                } else {
                    displayError("Invalid response format from the API.");
                }
            })
            .catch(error => {
                displayError(`Error sending/receiving data: ${error.message}`);
            });
        });
    });
});

function displayHint(hint) {
    document.getElementById('response-text').textContent = hint;
    document.getElementById('response-container').style.display = 'block';
    document.getElementById('error-message').style.display = 'none';
}

function displayError(errorMessage) {
    document.getElementById('response-text').textContent = ''; 
    document.getElementById('error-message').textContent = errorMessage;
    document.getElementById('error-message').style.display = 'block';
    document.getElementById('response-container').style.display = 'none';
}