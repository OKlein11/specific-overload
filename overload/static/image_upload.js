function uploadFile(input) { // Thiss function takes the uploaded file and puts out the preview image
    var num = input.id.split("_")[1];
    num = parseInt(num);
    var image = document.getElementById("preview_"+String(num));
    if (!image.hasAttribute("src")) {
        addNewImageUpload(num);
    }
    var imageURL = input.files[0];
    image.src = URL.createObjectURL(imageURL);

}

function addNewImageUpload(previous) { // This function takes the previous number of the last uploaded image and dds the div for the next image upload
    var num = String(previous + 1);
    var uploadForm = document.getElementById("uploadForm");

    var div = document.createElement("div");
    div.id = "div_" + num;

    var imageInput = document.createElement("input");
    imageInput.type = "file";
    imageInput.id = "image_" + num;
    imageInput.name = "image_" + num;
    imageInput.setAttribute("onchange","uploadFile(this)");
    div.appendChild(imageInput);

    var nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.id = "name_" + num;
    nameInput.name = "name_" + num;
    div.appendChild(nameInput);

    var altInput = document.createElement("input");
    altInput.type = "text";
    altInput.id = "alt_" + num;
    altInput.name = "alt_" + num;
    div.appendChild(altInput);

    var preview = document.createElement("img");
    preview.id = "preview_" + num;
    preview.width = 200;
    div.appendChild(preview);

    uploadForm.insertBefore(div, document.getElementById("submitButton"))
}