
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


function getSearchButton(searchInput)
{
    let searchDiv = searchInput.parentElement.parentElement;
    return searchDiv.querySelector('a.search');
}


function search(event)
{
    let searchInput = event.target;
    if(!searchInput)
        return;

    let searchUrl = searchInput.getAttribute('data-href');
    searchUrl = searchUrl.replace('SEARCH_STRING', searchInput.value);

    let searchButton = getSearchButton(searchInput);
    searchButton.setAttribute('href', searchUrl);
}


function handleKeyUp(event)
{
    if(event.key !== 'Enter')
        return;

    if(!document.hasFocus())
        return;

    let activeElement = document.activeElement;
    if(!activeElement)
        return;

    if(activeElement.tagName !== 'INPUT')
        return;

    if(!activeElement.classList.contains('search'))
        return;

    let searchButton = getSearchButton(activeElement);
    let searchUrl = searchButton.href;
    if(searchUrl.indexOf('SEARCH_STRING') >= 0)
        return;
    document.location = searchUrl;
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

    let pageSwitchers = document.querySelector('div.page-switcher-button');

    document.addEventListener('keyup', handleKeyUp);
}

setup();

