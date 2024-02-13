let sidebar = document.querySelector(".sidebar");
let sidebarButton = document.querySelector(".sidebarButton");
sidebar.classList.toggle("active");
sidebarButton.onclick = function() {
    sidebar.classList.toggle("active");
}