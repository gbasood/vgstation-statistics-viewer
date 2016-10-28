// Matches clickthrough
window.onload = function() {
    var matches = document.getElementsByClassName('match')
    for(var i = 0; i < matches.length; i++) {
        var match = matches[i];
        match.onclick=match_clickthrough, match
    }
}

function match_clickthrough(match) {
  var destination = '/match/';
  if(match.target.dataset.matchid !== undefined) {
    destination += match.target.dataset.matchid;
  } else {
    console.log(match.target);
    var parent = match.target.parentElement;
    while(parent.dataset.matchid === undefined) {
      parent = parent.parentElement;
    }
    destination += parent.dataset.matchid;
  }

  if (destination) {
    window.location = destination;
  }
}
