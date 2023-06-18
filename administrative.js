let sidebar = document.querySelector(".sidebar");
let sidebarButton = document.querySelector(".sidebarButton");

sidebarButton.onclick = function() {
    sidebar.classList.toggle("active");
}