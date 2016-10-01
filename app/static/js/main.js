// Matches clickthrough
window.onload = function() {
    var matches = document.getElementsByClassName('match')
    for(var i = 0; i < matches.length; i++) {
        var match = matches[i];
        match.addEventListener("click", match_clickthrough, false);
    }
}

function match_clickthrough() {
  var destination = '/match/';
  if(event.target.dataset.matchid !== undefined) {
    destination += event.target.dataset.matchid;
  } else {
    console.log(event.target);
    var parent = event.target.parentElement;
    while(parent.dataset.matchid === undefined) {
      parent = parent.parentElement;
    }
    destination += parent.dataset.matchid;
  }

  if (destination) {
    window.location = destination;
  }
}
