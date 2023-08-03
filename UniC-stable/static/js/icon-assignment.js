let icons = {
    "Books": "&#128218;",
    "Stationary": "&#128207; &#9999;",
    "Clothing": "&#128087; &#128085;",
    "Household": "&#127968;",
    "Sports": "&#127951; &#127934; &#9917;",
    "Electronics": "&#128267;",
    "Toys": "&#127922;",
    "Decorations": "&#127882; &#10024;",
}
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("#category").forEach((icon) => {
        icon.innerHTML = icons[icon.className];
    })
})