// Toggle for showing the menu on a mobile device
function mobile_toggle() {
    var x = document.getElementById("mobile-nav-content");

    if (x.style.display === "none") {
        x.style.display = "flex";
    } else {
        x.style.display = "none";
    }
}


// Recipe Search (text input on nav bar)
var search_query = document.getElementById("search_query");

search_query.onkeyup = function (event) {
    if (event.key === 'Enter') {
        if (search_query.value) {
            window.location.href = "/search/" + search_query.value;
        }
    }
}

// Recipe deletion functions
function delete_recipe(recipe_id) {
    fetch("/delete_recipe", {
        method: "POST",
        body: JSON.stringify({ recipe_id: recipe_id }),
    }).then((_res) => {
        var currentScrollPosition = $(window).scrollTop();
        location.reload();
        setTimeout(function () {
            $(window).scrollTop(currentScrollPosition);
        }, 100);
    });
}

function delete_recipe_go_home(recipe_id) {
    fetch("/delete_recipe_go_home", {
        method: "POST",
        body: JSON.stringify({ recipe_id: recipe_id }),
    }).then((_res) => {
        // window.location.href = "/";
        console.log(_res);
    });
}

//Cart clearing and cart item deletion
function clear_cart(user_id) {
    fetch("/clear_cart", {
        method: "POST",
        body: JSON.stringify({ user_id: user_id }),
    }).then((_res) => {
        window.location.href = "/cart";
    });
}

function delete_shopping_item(item_id) {
    fetch("/delete_item", {
        method: "POST",
        body: JSON.stringify({ item_id: item_id }),
    }).then((_res) => {
        var currentScrollPosition = $(window).scrollTop();
        location.reload();
        setTimeout(function () {
            $(window).scrollTop(currentScrollPosition);
        }, 100);
    });
}

const clearCartModal = document.getElementById("modal-container-cart");
const clearCartButton = document.getElementById("clear-cart-button");
const closeCartModalButton = document.getElementById("close-cart-modal");
const confirmClearCartButton = document.getElementById("confirm-clear-cart");

if (clearCartButton) {
    const userID = clearCartModal.dataset.userId;
    clearCartButton.addEventListener("click", () => {
        clearCartModal.style.display = "block";
        console.log("Hello")
    });
    
    closeCartModalButton.addEventListener("click", () => {
        clearCartModal.style.display = "none";
    })
    
    confirmClearCartButton.addEventListener("click", () => {
        clear_cart(userID)
    })
}



// Add and remove favorite recipes
function add_favorite(recipe_id) {
    fetch("/add_favorite", {
        method: "POST",
        body: JSON.stringify({ recipe_id: recipe_id }),
    }).then((_res) => {
        var currentScrollPosition = $(window).scrollTop();
        location.reload();
        setTimeout(function () {
            $(window).scrollTop(currentScrollPosition);
        }, 100);
    });
}

function remove_favorite(recipe_id) {
    fetch("/remove_favorite", {
        method: "POST",
        body: JSON.stringify({ recipe_id: recipe_id }),
    }).then((_res) => {
        var currentScrollPosition = $(window).scrollTop();
        location.reload();
        setTimeout(function () {
            $(window).scrollTop(currentScrollPosition);
        }, 100);
    });
}

// Everything to do with recipe tags
function delete_tag(tag_id, view_id, recipe_id) {
    var recipe_url = view_id;
    fetch("/delete_tag", {
        method: "POST",
        body: JSON.stringify({ tag_id: tag_id, recipe_id: recipe_id }),
    }).then((_res) => {
        var currentScrollPosition = $(window).scrollTop();
        location.reload();
        setTimeout(function () {
            $(window).scrollTop(currentScrollPosition);
        }, 100);
    });
}

var add_button = document.getElementById("add_tag");
var delete_button = document.getElementsByClassName("delete_tag");
var tag_lister = document.getElementById("list_all_tags");
var all_tags = document.querySelector(".tag-text");
var input_text_key_press = document.getElementById("new_tag");

// if (document.getElementById("ing")) {
//     const ing = document.getElementById.addEventListener("keypress",  (e) => {
//         var key = e.charCode || e.keyCode || 0;
//         if (key == 13) {
//             e.preventDefault();
//         }})
//     }

if (input_text_key_press) {
input_text_key_press.onkeydown = function (e) {
    if (e.key === 'Enter') {
        
        e.preventDefault();
       
        var tag_input = document.getElementById("new_tag");
        var tag_list = document.getElementById("tag_list");
        var tag_to_add = document.createElement("li");
        var text_to_add = document.createTextNode(tag_input.value);
        var hidden_input = document.createElement("input");
        hidden_input.setAttribute("type", "hidden");
        hidden_input.setAttribute("name", "new_tag");

        tag_to_add.appendChild(text_to_add);
        tag_list.appendChild(tag_to_add);
        tag_to_add.innerHTML = "<span class='tag-text'>" + tag_input.value + '</span>' + " <span class='delete_tag' onclick='delete_tag(this)'><i class='fa-solid fa-circle-xmark fa-lg'></i></span><input type='hidden' name='new_tag' value='" + tag_input.value + "'>";
        tag_input.value = "";
    }
}}

if (tag_lister) {
tag_lister.onclick = function () {
    var all_tags = document.querySelectorAll(".tag-text");

    for (i = 0; i < all_tags.length; i++) {
        console.log(all_tags[i].textContent);
    }

}}


// Recipe creator functions
function add_ingredient() {
    var ingredient_container = document.getElementById("ingredient_list");
    var new_ingredient = document.createElement("div");
    new_ingredient.setAttribute("class", "cr-ingredient-wrapper");

    var new_ingredient_textbox = document.createElement("input");
    new_ingredient_textbox.setAttribute("class", "text-input");
    new_ingredient_textbox.setAttribute("name", "ingredients");
    new_ingredient_textbox.setAttribute("placeholder", "Enter ingredient.");

    var new_ingredient_select = document.createElement("select");
    new_ingredient_select.setAttribute("class", "cr-ing-preview");
    new_ingredient_select.setAttribute("name", "ing_type")

    var ing_type = document.createElement("option");
    ing_type.value = "misc";
    ing_type.text = "Misc.";
    new_ingredient_select.appendChild(ing_type);

    var ing_type = document.createElement("option");
    ing_type.value = "produce";
    ing_type.text = "Produce";
    new_ingredient_select.appendChild(ing_type);

    var ing_type = document.createElement("option");
    ing_type.value = "meat";
    ing_type.text = "Meat";
    new_ingredient_select.appendChild(ing_type);

    var ing_type = document.createElement("option");
    ing_type.value = "coffee_tea";
    ing_type.text = "Coffee and Tea";
    new_ingredient_select.appendChild(ing_type);

    var ing_type = document.createElement("option");
    ing_type.value = "pasta";
    ing_type.text = "Pasta";
    new_ingredient_select.appendChild(ing_type);

    var ing_type = document.createElement("option");
    ing_type.value = "frozen";
    ing_type.text = "Frozen Food";
    new_ingredient_select.appendChild(ing_type);

    var ing_type = document.createElement("option");
    ing_type.value = "dairy_bread";
    ing_type.text = "Dairy";
    new_ingredient_select.appendChild(ing_type);

    var new_ingredient_delete = document.createElement("div");
    new_ingredient_delete.setAttribute("class", "cr-delete");

    var new_delete_button = document.createElement("i");
    new_delete_button.setAttribute("class", "fa-solid fa-square-xmark fa-lg");
    new_delete_button.setAttribute("onclick", "remove_added_ingredient(this)");

    new_ingredient_delete.appendChild(new_delete_button);


    new_ingredient.appendChild(new_ingredient_textbox);
    new_ingredient.appendChild(new_ingredient_select);
    new_ingredient.appendChild(new_ingredient_delete);
    ingredient_container.appendChild(new_ingredient);
}

function add_recipe_step() {
    var instructions = document.getElementById("instruction-container");
    var new_instruction = document.createElement("div");
    new_instruction.setAttribute("style", "margin-top: .5rem;")

    new_instruction.innerHTML = '<div class="cr-step"><div><textarea class="text-area" id="instructions" name="instructions" rows="3" placeholder="Enter recipe step."></textarea></div><div><i class="fa-solid fa-square-xmark fa-lg" onclick="remove_added_step(this)"></i></div></div>'

    instructions.appendChild(new_instruction);
}

function remove_added_ingredient(ing) {
    ing.parentElement.parentElement.remove();
}

function remove_added_step(step) {
    step.parentElement.parentElement.remove();
}

// Modal functions
var modal = document.getElementById("modal-container");

var close_btn = document.getElementById("close");

function close_modal() {
    document.preventDefault;
    modal.style.display = "none";
}

// Recipe deletion
function delete_recipe(e) {
    var modal = document.getElementById("modal-container");
    modal.style.display = "block";
    var recipe_title = e.dataset.recipeTitle;
    var modal_text = document.getElementById("modal-inner-text");
    modal_text.innerText = "Are you sure you want to delete " + recipe_title + "?";
    
    var recipe_id = e.dataset.recipeId;
    var delete_link = document.getElementById("delete-link");
    delete_link.setAttribute("href", "/delete_recipe_go_home/" + recipe_id)
    
};

function new_delete(e) {
    var modal = document.getElementById("modal-container");
    var recipe_id = e.dataset.recipeId;
    var delete_link = document.getElementById("delete-link")
    var modal_text = document.getElementById("modal-inner-text");
    var recipe_title = e.dataset.recipeTitle;
    modal.style.display = "block";
    modal_text.innerText = "Are you sure you want to delete " + recipe_title + "?";

    delete_link.setAttribute("href", "/delete_recipe_go_home/" + recipe_id)
};

// Flask flashed message handling
const flashAlert = document.getElementById("alert");
const flashMessage = document.getElementById("alert-close");

if (flashMessage) {
flashMessage.addEventListener("click", () => {
    console.log("Alert close pressed");
    flashAlert.style.display = "none";
})};

const editCartItem = (item) => {
    let currentItemContent = item.innerHTML
    let textBox = item.nextElementSibling
    let itemID = item.dataset.itemNumber
    
    textBox.style.display = "block"
    textBox.setAttribute("value", currentItemContent)
    textBox.setAttribute("class", "cart-text-input")
    item.style.display = "none"

    textBox.addEventListener("keydown", (e) => {
        if (e.key == 'Enter') {
            console.log("enter")
            e.preventDefault();
            fetch('/update_cart/' + itemID + '/' + textBox.value).then((_res) => {
                var currentScrollPosition = $(window).scrollTop();
                location.reload();
                setTimeout(function () {
                    $(window).scrollTop(currentScrollPosition);
                }, 100);
            });
        }
    })
}