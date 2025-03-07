// Assume jQuery is loaded

notes = [
    "c0",
    "d0", "e0", "f0",
    "g0", "a1", "b1", "c1",
    "d1", "e1", "f1", "g1",
    "a2"
]

function playNote(note) {
    $(".note").removeClass("active");
    $(".line-dangle").removeClass("active");
    setTimeout(function(){
        $("." + note).addClass("active");
    }, 100);
}

function newNote(note_) {
    if (state.current_note && state.current_time) {
        time_diff = (new Date()).getTime() - state.current_time;
        state.total_duration += time_diff;
        obj = {note: state.current_note, duration: time_diff}
        state.previous_notes.push(obj);
        element = createLabel(obj);
        $("#labels").append(element);
    }
    state.current_note = note_;
    state.current_time = new Date().getTime();
    updateUI();
}

function playRandomNotes(){
    setInterval(function(){
        // Select a random note
        var note = notes[Math.floor(Math.random() * notes.length)];
        newNote(note);
    }, 900);
}

function updateAverage() {
    average_duration = (state.total_duration || 0)/ (state.previous_notes.length || 1);
    average_duration = average_duration / 1000;
    console.log(average_duration);
    $("#average").text(average_duration.toFixed(3) + "s");
}

function createLabel(content) {
    // Create a new DOM element
    var label = document.createElement("div");
    label.className = "label-note";
    label.innerHTML = content.note.toUpperCase();

    // Create duration
    var duration = document.createElement("duration");
    duration.className = "label-duration";
    duration.innerHTML = (content.duration / 1000).toFixed(3) + "s";

    // Create a grouped element
    var group = document.createElement("div");
    group.className = "label-group";
    group.appendChild(label);
    group.appendChild(duration);

    return group;
}

function updateUI() {
    playNote(state.current_note);
    updateAverage();
}

function playIntervalNotes(){
    let i = 0;
    setInterval(function(){
        if (i >= notes.length) {
          i = 0;
        }
        newNote(notes[i]);
        i++;
    }, 900);
}


$(document).ready(function(){
//    playIntervalNotes();
//    playNote("a2")
});

function changeFadeIn() {
    input_dom = $("#fade-in")
    value = input_dom.val()
    $(":root").css("--in-duration", `${value}s`)
    console.log($(":root").css("--in-duration"))
}

function changeFadeOut() {
    input_dom = $("#fade-out")
    value = input_dom.val()
    $(":root").css("--out-duration", `${value}s`)
    console.log($(":root").css("--out-duration"))
}

var state = {
    current_note: null,
    current_time: null,
    total_duration: 0,
    previous_notes: [],
    session: null,
}

function connect() {
    state = {
        current_note: null,
        current_time: null,
        total_duration: 0,
        previous_notes: [],
        session: null,
    }
    $("#labels").empty();
    state.session = new WebSocket("ws://localhost:8080/");
    state.session.addEventListener("message", function(event){
        newNote(event.data);
    });

}
