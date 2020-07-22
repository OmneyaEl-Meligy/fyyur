window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

function changeLabelVenu(selected){
  
  if(selected.value == "city"){
    document.getElementById('search_venue').setAttribute('placeholder', " City, State");
  }else{
    document.getElementById('search_venue').setAttribute('placeholder', "Venue name");
  }
}

function changeLabelArtist(selected){
  
  if(selected.value == "city"){
    document.getElementById('search_artist').setAttribute('placeholder', " City, State");
  }else{
    document.getElementById('search_artist').setAttribute('placeholder', "Artist name");
  }
}