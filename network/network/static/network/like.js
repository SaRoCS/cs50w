document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll("img").forEach( function(item) {
        item.addEventListener('click', () => {
            let parent = item.parentElement;
            parent = parent.parentElement;
            parent = parent.parentElement;
            parent = parent.firstElementChild;
            const id = parent.id;
            if (item.src === "http://127.0.0.1:8000/static/network/heartO.jpg"){
                let csrftoken = Cookies.get('csrftoken');
                fetch('/like', {
                    method: "POST",
                    body: JSON.stringify({
                        post: id,
                        unlike: false,
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
            } else if (item.src === "http://127.0.0.1:8000/static/network/heart.jpg"){
                let csrftoken = Cookies.get('csrftoken');
                fetch('/like', {
                    method: "POST",
                    body: JSON.stringify({
                        post: id,
                        unlike: true,
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

});