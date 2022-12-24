
var bo = true;
var menuIcon = document.getElementById("menu-icon");
var menu = document.getElementById("menu");
var menuMain = document.getElementById("menu-main");
var menuExit = document.getElementById("menu-exit");
var iconExit = document.getElementById("icon-exit");
var root = document.getElementById("root");
var menuOut = document.getElementById("menu-out");
menuIcon.onclick = function () {
  menu.style.visibility = "visible";
  menu.style.opacity = "1";
  menuMain.style.transform = "translateX(0)";
  menuExit.style.visibility = "visible";
  menuExit.style.opacity = "1";
  iconExit.style.width = "4.8rem";
  iconExit.style.height = "4.8rem";
  root.style.overflowY = "hidden";
};
menuOut.onclick = function () {
  menu.style.visibility = "hidden";
  menu.style.opacity = "0";
  menuMain.style.transform = "translateX(-280px)";
  root.style.overflowY = "scroll";
};

iconExit.onclick = function () {
  menu.style.visibility = "hidden";
  menu.style.opacity = "0";
  menuMain.style.transform = "translateX(-280px)";
  root.style.overflowY = "scroll";
};

var subItem = document.querySelectorAll("div#subitem");
var subMenu = document.querySelectorAll("div#submenu");
var subMenuOut = document.querySelectorAll("div#submenuout");

for (let i = 0; i < subItem.length; i++) {
  subItem[i].onclick = () => {
    subMenu[i].style.transform = "translateX(0px)";
  };
  subMenuOut[i].onclick = () => {
    subMenu[i].style.transform = "translateX(280px)";
  };
}