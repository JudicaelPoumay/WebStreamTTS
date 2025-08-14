async function speak() {
    var text = document.getElementById("text").value;
    var speed = document.getElementById("speed").value;
    try {
        var url = '/tts?text=' + encodeURIComponent(text) + '&speed=' + speed;
        var audio = document.getElementById("audio");
        audio.src = url;
        audio.play();
    } catch (error) {
        console.error('Error during fetch or audio playback:', error);
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById("text").value = "This is a text to speech demo text";
    document.getElementById("speakButton").addEventListener("click", speak);
    document.getElementById("speed").addEventListener("input", function() {
        document.getElementById("speed-value").textContent = this.value + "x";
    });
});
