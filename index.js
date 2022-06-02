
function menuSelect(selectElement)
{
    let selectedOption = selectElement.selectedOptions[0];
    let href = selectedOption.getAttribute('data-href');
    if(href)
    {
        window.location = href;
    }
}


function search(searchInput)
{
    let searchDiv = searchInput.parentElement;
    console.log('foo');
}