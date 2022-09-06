document.addEventListener("DOMContentLoaded", function() {

    document.querySelector("#post").addEventListener("keyup", () => {
        let post = document.querySelector("#post").value;
        if (post !== ''){
            document.querySelector("#submit").disabled = false;
        } else {
            document.querySelector("#submit").disabled = true;
        }
    });

});