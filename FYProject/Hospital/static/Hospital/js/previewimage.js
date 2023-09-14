photo = document.getElementById("logo");
photolabel = photo.nextSibling.nextSibling;

photo.addEventListener("change", ({ target }) => {
  console.log("changed ");
  const file = target.files[0];
  let loadedimg = document.getElementById("loadedimg");
  if (file && file.type.substr(0, 5) === "image") {
    const reader = new FileReader();
    loadedimg.parentNode.removeChild(loadedimg);
    reader.onloadend = () => {
      img = document.createElement("img");
      img.id = "loadedimg";
      img.src = reader.result;
      img.style.width = "100%";
      img.style.height = "100%";
      photolabel.appendChild(img);
    };
    reader.readAsDataURL(file);
  } else {
    loadedimg.parentNode.removeChild(loadedimg);
    img = document.createElement("img");
    img.id = "loadedimg";
    img.src = "{% static 'mkulima/images/error.png' %}";
    img.style.width = "100%";
    img.style.height = "100%";
    photolabel.appendChild(img);
  }
});
