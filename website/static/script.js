const wrapper = document.querySelector(".select-box-wrapper"),
      selectBtn = wrapper.querySelector(".select-btn"),
      input = wrapper.querySelector("#input"),
      content = wrapper.querySelector(".content"),
      options = wrapper.querySelector(".options");

function filterFunction() {
    var filter = input.value.toUpperCase();
    var li = options.getElementsByTagName("li");

    for (var i = 0; i < li.length; i++) {
        var txtValue = li[i].textContent || li[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function selectAnime(animeName) {
    input.value = animeName;
    // wrapper.classList.remove("active"); // Don't remove "active" class here
}

options.addEventListener("click", function (event) {
    if (event.target.tagName === "LI") {
        selectAnime(event.target.textContent || event.target.innerText);
        // Prevent hiding content when an anime is selected
        event.preventDefault();
        event.stopPropagation();
    }
});

selectBtn.addEventListener("click", function () {
    wrapper.classList.toggle("active");
});

// Close dropdown when clicking outside the wrapper
document.addEventListener("click", function (event) {
    if (!wrapper.contains(event.target)) {
        wrapper.classList.remove("active");
    }
});
