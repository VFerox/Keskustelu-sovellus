function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/";
    });
}

function likeNote(noteId) {
    fetch("/like-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}

function dislikeNote(noteId) {
    fetch("/dislike-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}

function addComment(noteId) {
    const commentText = document.getElementById(`comment-${noteId}`).value;
    fetch("/add-comment", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId, comment: commentText }),
    }).then((_res) => {
        window.location.href = "/";
    });
}

function deleteComment(commentId) {
    fetch("/delete-comment", {
        method: "POST",
        body: JSON.stringify({ commentId: commentId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}

document.getElementById("profileForm").onsubmit = function (e) {
    e.preventDefault();
    const bio = document.getElementById("bio").value;
    const profileImage = document.getElementById("profile_image").value;

    fetch("/update-profile", {
        method: "POST",
        body: new URLSearchParams({
            bio: bio,
            profile_image: profileImage
        })
    }).then(response => {
        if (response.ok) {
            document.getElementById("updatedBio").innerText = bio;
            document.getElementById("successMessage").style.display = "block";
        }
    });
};

document.getElementById("profileForm").onsubmit = function (e) {
    e.preventDefault();
    
    const bio = document.getElementById("bio").value;
    const profileImage = document.getElementById("profile_image").value;

    fetch("/update-profile", {
        method: "POST",
        body: new URLSearchParams({
            bio: bio,
            profile_image: profileImage
        })
    }).then(response => response.json())
      .then(data => {
        if (data.success) {
            document.getElementById("updatedBio").innerText = bio ? bio : "No bio available.";
            document.getElementById("bio").value = "";
            document.getElementById("successMessage").style.display = "block";
        }
    });
};



