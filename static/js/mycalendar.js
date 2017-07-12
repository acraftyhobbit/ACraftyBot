 function updateDates() {
        var url = window.location.pathname;
        var info = url.split("/");
        var user_id = info[2];
    $.get('/user/' + user_id +'/due-at.json',{'user_id': user_id}, showProjectDates);
}
var settings = {Color: '#999',                //(string - color) font color of whole calendar.
    LinkColor: '#333',            //(string - color) font color of event titles.
    NavShow: true,                //(bool) show navigation arrows.
    NavVertical: false,           //(bool) show previous and coming months.
    NavLocation: '#foo',          //(string - element) where to display navigation, if not in default position.
    DateTimeShow: true,           //(bool) show current date.
    DateTimeFormat: 'mmm, yyyy',  //(string - dateformat) format previously mentioned date is shown in.
    DatetimeLocation: '',         //(string - element) where to display previously mentioned date, if not in default position.
    EventClick: '',               //(function) a function that should instantiate on the click of any event. parameters passed in via data link attribute.
    EventTargetWholeDay: false,   //(bool) clicking on the whole date will trigger event action, as opposed to just clicking on the title.
    DisabledDays: [],             //(array of numbers) days of the week to be slightly transparent. ie: [1,6] to fade Sunday and Saturday.
    }
var element = document.getElementById('caleandar');
updateDates();
 

function showProjectDates(results) {
        events = results
         var dates = events.map(function(element){
    element['Date'] = new Date (element['Date'])
return element}) 
         console.log(dates)
// var dates = [
//   {'Date': new Date(2017, 6, 7), 'Title': 'Doctor appointment at 3:25pm.'},
//   {'Date7': new Date(2017, 6, 18), 'Title': 'New Garfield movie comes out!', 'Link': 'https://garfield.com'},
//   {'Date': new Date(201, 6, 27), 'Title': '25 year anniversary', 'Link': 'https://www.google.com.au/#q=anniversary+gifts'},
// ];
         caleandar(element, dates, settings); 
    }
   