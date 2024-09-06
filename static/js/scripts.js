let menu_list = document.getElementById("navbar-list")
        menu_list.style.maxHeight = "0px";

        function toggleMenu() {
            if (menu_list.style.maxHeight == "0px") {
                menu_list.style.maxHeight = "300px";
            } else {
                menu_list.style.maxHeight = "0px";
            }
        }
