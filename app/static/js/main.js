// Matches clickthrough
window.onload = function() {
    var matches = document.getElementsByClassName('match')
    for(var i = 0; i < matches.length; i++) {
        var match = matches[i];
        match.onclick = function() {
            window.location = '/match/' + match.dataset.matchid;
        }
    }
}
