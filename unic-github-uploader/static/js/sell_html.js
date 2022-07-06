document.addEventListener("DOMContentLoaded", () => {
    let price = document.querySelector("#price");
    let item_name = document.querySelector("#prodname");
    let descr = document.querySelector("textarea");
    let item_img = document.querySelector("#item_img");
    let msg_div = document.querySelector("#form-checking");
    let msg;
    document.querySelector("#submit").addEventListener("click", () => {
        if (item_name.value !== "" && price.value !== "" && descr.value !== "") {
            if (descr.value !== "Write the description here" && descr.value.length <= 500) {
                if (!isNaN(price.value)) {
                    if (price.value >= 0) {
                        if (item_img.value.slice(-4) === ".png" || item_img.value.slice(-4) === ".jpg" || item_img.value.slice(-4) === ".gif" || item_img.value.slice(-5) === ".jpeg") {
                            document.querySelector("form").submit();
                        }
                        else {
                            msg = "Only .png, .jpeg/.jpg, or .gif files are allowed. Please upload a different image";
                        }
                    }
                    else {
                        msg = "Price cannot be negative";
                    }
                }
                else {
                    msg = "Price has to be a number";
                }
            }
            else {
                msg = "Please fill in a description, and ensure the description is no more than 500 characters"
            }
        }
        else {
            msg = "No field can be left blank. Please fill in all fields"
        }
        msg_div.hidden = false;
        msg_div.innerHTML = msg;
        return false;
    })
})