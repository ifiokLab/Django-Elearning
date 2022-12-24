function Tab(item){
    var i;
    var x = document.getElementsByClassName('tab-text');
    for(i=0;i<x.length;i++){
        x[i].style.display = "none";
    }
    document.getElementById(item).style.display = "block";  
}

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    } 
  });
}