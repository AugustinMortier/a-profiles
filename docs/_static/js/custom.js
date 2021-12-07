console.log('Yo')

$(function() {
    // add V-Profiles in top right icon links

    // get path
    if (window.location.href.includes('build')){
        // if local
        var url = window.location.href.split('_build')[0]
    } else if (window.location.href.includes('readthedocs.io')){
        // if readthedocs
        var url = window.location.href.split('latest')[0]+'latest/'
    }

    var addInList = '<li class="nav-item">'
        addInList += '<a class="nav-link" href="https://vprofiles.met.no" rel="noopener" target="_blank" title="V-Profiles">'
            addInList += '<span><img src="'+url+'_static/images/vprofiles-bold.ico" height="20" width="20"></span>'
        addInList += '</a>'
    addInList += '</li>'
    document.getElementById('navbar-icon-links').innerHTML += addInList
})