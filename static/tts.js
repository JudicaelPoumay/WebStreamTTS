async function toggleSpeak() {
    const speakButton = document.getElementById("speakButton");
    const audio = document.getElementById("audio");

    const isSpeaking = speakButton.getAttribute("data-speaking") === "true";

    if (isSpeaking) {
        try {
            await fetch('/stop', { method: 'POST' });
        } catch (error) {
            console.error('Error stopping TTS:', error);
        }
        audio.pause();
        audio.src = '';
        audio.load(); // This helps in releasing the resources
        speakButton.textContent = "Speak";
        speakButton.setAttribute("data-speaking", "false");
    } else {
        const text = document.getElementById("text").value;
        const speed = document.getElementById("speed").value;

        if (!text.trim()) return;

        try {
            const url = '/tts?text=' + encodeURIComponent(text) + '&speed=' + speed;
            audio.src = url;
            audio.play();
            speakButton.textContent = "Stop";
            speakButton.setAttribute("data-speaking", "true");
        } catch (error) {
            console.error('Error during fetch or audio playback:', error);
            speakButton.textContent = "Speak";
            speakButton.setAttribute("data-speaking", "false");
        }
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById("text").value = "This is a text to speech demo text";
    document.getElementById("speakButton").addEventListener("click", toggleSpeak);
    document.getElementById("speed").addEventListener("input", function() {
        document.getElementById("speed-value").textContent = this.value + "x";
    });

    const audio = document.getElementById("audio");
    audio.addEventListener('ended', () => {
        const speakButton = document.getElementById("speakButton");
        speakButton.textContent = "Speak";
        speakButton.setAttribute("data-speaking", "false");
    });

    document.getElementById('text').addEventListener('paste', async (e) => {
        e.preventDefault();
        const clipboardData = e.clipboardData || window.clipboardData;
        const html = clipboardData.getData('text/html');

        if (html) {
            try {
                const response = await fetch('/html_to_markdown', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ html }),
                });
                const data = await response.json();
                if (data.markdown) {
                    document.execCommand('insertText', false, data.markdown);
                }
            } catch (error) {
                console.error('Error converting HTML to Markdown:', error);
                const text = clipboardData.getData('text/plain');
                document.execCommand('insertText', false, text);
            }
        } else {
            const text = clipboardData.getData('text/plain');
            document.execCommand('insertText', false, text);
        }
    });
});
