
function menuSelect(event)
{
    let selectElement = event.target;
    let selectedOption = selectElement.selectedOptions[0];
    let href = selectedOption.getAttribute('data-href');
    if(href)
    {
        window.location = href;
    }
}


function search(event)
{
    console.debug('search');
    let searchInput = event.target;
    if(!searchInput)
        return;
    
    let searchDiv = searchInput.parentElement;
    console.debug(searchDiv);
    console.log(searchInput.value);
}


function setup()
{
    let menus = document.querySelectorAll('select.menu');
    for(const menu of menus)
    {
        menu.addEventListener('change', menuSelect);
    }

    let searchInputs = document.querySelectorAll('input.search');
    for(const searchInput of searchInputs)
    {
        searchInput.addEventListener('input', search);
    }
}

setup();

