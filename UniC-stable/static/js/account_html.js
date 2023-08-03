let info;
let info_change;
let mentorships;
let listings;
let username_input;
let bio_input;
let phonenum_input;
let location_input;

document.addEventListener("DOMContentLoaded", () => {
    info = document.querySelector("#account_info");
    info_change = document.querySelector("#change_info");
    mentorships = document.querySelector("#mentorships");
    listings = document.querySelector("#listings");
    listings.style.display = "none";
    mentorships.style.display = "none";
    info_change.style.display = "none";
    username_input = document.querySelector("#username");
    bio_input = document.querySelector("#bio");
    phonenum_input = document.querySelector("#phonenum");
    location_input = document.querySelector("#location");
    

    document.querySelector("#submit").addEventListener("click", () => {
        if (username_input.value !== "" && bio_input.value !== "" && phonenum_input.value !== "" && location_input.value !== "") {
            document.querySelector("form").submit();
        }
        else {
            alert("Please fill in all the fields");
        }
    })
    document.querySelector("#back").addEventListener("click", () => {
        info_change.style.display = "none";
        listings.style.display = "none";
        mentorships.style.display = "none";
        info.style.display = "block";
    })
    document.querySelector("#change").addEventListener("click", () => {
        info_change.style.display = "block";
        info.style.display = "none";
        listings.style.display = "none";
        mentorships.style.display = "none";
    })
    document.querySelector("#show_listings").addEventListener("click", () => {
        info_change.style.display = "none";
        info.style.display = "block";
        listings.style.display = "block";
        mentorships.style.display = "none";
    })
    document.querySelector("#show_mentorships").addEventListener("click", () => {
        info_change.style.display = "none";
        info.style.display = "block";
        listings.style.display = "none";
        mentorships.style.display = "block";
    })

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            let buyerlat = position.coords.latitude;
            let buyerlong = position.coords.longitude;
            let positionInfo = `Your current position is (Latitude: ${buyerlat}, Longitude: ${buyerlong})`;
            console.log(positionInfo);
            document.querySelector("#lat").value = buyerlat;
            document.querySelector("#long").value = buyerlong;
            return true;
            });
        } 
        else {
            alert("Sorry, your browser does not support HTML5 geolocation. Please update your browser, or try a different browser");
            return false;
        }
})