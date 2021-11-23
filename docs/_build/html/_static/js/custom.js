console.log('Yo')

$(function() {
    // add V-Profiles in top right icon links
    var addInList = '<li class="nav-item">'
        addInList += '<a class="nav-link" href="https://vprofiles.met.no" rel="noopener" target="_blank" title="V-Profiles">'
            addInList += '<span><img src="_images/vprofiles.ico" height="20" width="20"></span>'
        addInList += '</a>'
    addInList += '</li>'
    document.getElementById('navbar-icon-links').innerHTML += addInList
})