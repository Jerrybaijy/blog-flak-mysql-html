document.addEventListener('DOMContentLoaded', function() {
    const audio = document.getElementById('bgMusic');
    
    function tryAutoPlay() {
        audio.play().catch(function(error) {
            console.log("自动播放失败，等待用户交互:", error);
            document.addEventListener('click', function playOnClick() {
                audio.play();
                document.removeEventListener('click', playOnClick);
            }, { once: true });
        });
    }
    
    if (localStorage.getItem('musicPlaying') !== 'false') {
        tryAutoPlay();
    }
    
    audio.addEventListener('play', function() {
        localStorage.setItem('musicPlaying', 'true');
    });
    
    audio.addEventListener('pause', function() {
        localStorage.setItem('musicPlaying', 'false');
    });
}); 