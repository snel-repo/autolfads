var coll = document.getElementsByClassName("stepContainer");
var i;

for (i=0;i<coll.length;i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight) {
      content.style.maxHeight=null;
      content.style.visibility="hidden";
    } else {
      content.style.visibility="visible";
      content.style.maxHeight = content.scrollHeight + "px";
    }
  });
}
