// This is some silly and very old code don't take it seriously

function makeDivs(num) {
    for (let i = 0; i < num * num; i++) {
        const div = document.createElement('div');
        div.textContent = "";//(i+1).toString();
        let divID = String(i + 1)
        div.setAttribute('id', divID);
        div.classList.add('etch-div');
        container.appendChild(div);
        const currentDiv = document.getElementById(String(i + 1));
        currentDiv.addEventListener("mouseover", function (event) {
            if (checkbox.checked == true) {
                event.target.style.backgroundColor = getRandomColor();
            }
            else {
                event.target.style.backgroundColor = initialColor;
            }
            setTimeout(function () {
                if (checkbox.checked == true) {
                    event.target.style.backgroundColor = getRandomColor();// fadedColor;
                }
                else {
                    event.target.style.backgroundColor = fadedColor;
                }
            }, 500);
        }, false);

    }
}

function logSubmit(event) {
    let val = document.getElementById("reset-input").value;
    let etchDivs = document.getElementsByClassName('etch-div');
    //this is useless now right?
    for (var i = 0; i < etchDivs.length; i++) {
        etchDivs[i].style.backgroundColor = 'red';
    }
    // ^^^
    container.innerHTML = '';
    if (val == '') {
        makeGrid(defaultDiv)
    }
    else {
        makeGrid(val);
    }
    event.preventDefault();
}

function makeGrid(divInput = defaultDiv) {
    let numberDivs = divInput;
    let gridSizePx = 500;
    let gridSizeGap = 5;
    let widthSquare = gridSizePx / numberDivs;
    let newWidthSquare = (gridSizePx - (gridSizeGap * (numberDivs - 1))) / numberDivs;
    let newGridSizePx = gridSizePx + (gridSizeGap * (numberDivs - 1));
    widthSquare = newWidthSquare;
    newGridSizePx = gridSizePx;

    container.setAttribute('style', `display: grid; grid-template-columns: repeat(${numberDivs}, ${widthSquare}px); grid-template-rows: repeat(${numberDivs}, ${widthSquare}px); grid-gap: 0; height: ${newGridSizePx}px; width: ${newGridSizePx}px;  grid-gap: ${gridSizeGap}px ${gridSizeGap}px; border-style: solid; border-color: darkgray; margin-top: 50px;`);
    makeDivs(numberDivs);
}

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function init() {
    document.getElementById("reset-input").value = "";
}

window.onload = init;

const checkbox = document.querySelector("input[name=fun-check]");
const defaultDiv = 15;
const container = document.querySelector('#container');
const form = document.getElementById('form');

var initialColor = "gray";
var fadedColor = "darkgray";

makeGrid();
form.addEventListener('submit', logSubmit);
