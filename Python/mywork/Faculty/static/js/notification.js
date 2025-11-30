document.getElementById("notifBell").onclick = function() {
    let dropdown = document.getElementById("notifDropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
};
document.addEventListener("click", function(e){
    let dropdown = document.getElementById("notifDropdown");
    if (!e.target.closest("#notifBell")) {
        dropdown.style.display = "none";
    }
});