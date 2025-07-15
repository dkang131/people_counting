const webcam = document.getElementById('webcam');
const errorMsg = document.getElementById('error-message');
const startBtn = document.getElementById('startbtn');
const stopBtn = document.getElementById('stopbtn');

let countInterval = null;

function updateCounts() {
    fetch('/get_counts')
        .then(response => response.json())
        .then(data => {
            document.getElementById('in-count-value').textContent = data.in_count;
            document.getElementById('out-count-value').textContent = data.out_count;
        });
}

startBtn.onclick = async () => {
    try {
        await fetch('/start_stream', {method: 'POST'});
        webcam.src = '/video_feed';
        webcam.style.display = 'block';
        errorMsg.classList.add('hidden');
        countInterval = setInterval(updateCounts, 1000);
    } catch (e) {
        errorMsg.textContent = "Unable to start webcam stream.";
        errorMsg.classList.remove('hidden');
    }
};

stopBtn.onclick = async () => {
    try {
        await fetch('/stop_stream', {method: 'POST'});
        webcam.src = '';
        webcam.style.display = 'none';
        clearInterval(countInterval);
    } catch (e) {
        errorMsg.textContent = "Unable to stop webcam stream.";
        errorMsg.classList.remove('hidden');
    }
};
