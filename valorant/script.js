function toggleNav() { 
    const nav = document.getElementById('navOverlay');
    const btn = document.querySelector('.nav-toggle');
    nav.classList.toggle('active'); 
    btn.classList.toggle('open'); 
} 

function reveal() {
    var reveals = document.querySelectorAll(".reveal");
    for (var i = 0; i < reveals.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 150;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
    }
}

window.addEventListener("scroll", reveal);
window.onload = reveal;
