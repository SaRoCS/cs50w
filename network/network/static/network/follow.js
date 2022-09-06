document.addEventListener("DOMContentLoaded", () => {

    const btn = document.querySelector("#follow");

    if (document.querySelector("#following")) {
        btn.innerHTML = "Unfollow";
    } else {
        btn.innerHTML = "Follow";
    }

    const profile = document.querySelector("h2").innerHTML;
    btn.addEventListener('click', () => {
        if (btn.innerHTML === "Follow"){
            let csrftoken = Cookies.get('csrftoken');
            fetch('/follow', {
                method: "POST",
                body: JSON.stringify({
                    profile: profile,
                    unfollow: false,
                }),
                headers: { "X-CSRFToken": csrftoken },
            })
            .then((res) => res.json())
            .then((res) => {
                if (res.status === 201){
                    location.reload();
                    return false;
                }
            });
        } else if (btn.innerHTML === "Unfollow"){
            let csrftoken = Cookies.get('csrftoken');
            fetch('/follow', {
                method: "POST",
                body: JSON.stringify({
                    profile: profile,
                    unfollow: true,
                }),
                headers: { "X-CSRFToken": csrftoken },
            })
            .then((res) => res.json())
            .then((res) => {
                if (res.status === 201) {
                    location.reload();
                    return false;
                }
            });
        }
    });

});