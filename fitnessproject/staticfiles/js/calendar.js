/* global FullCalendar */
function getCookie(name) {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === name) return decodeURIComponent(value);
  }
  return null;
}

window.addEventListener('load', function () {
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) return;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: 'ja',

    contentHeight: 'auto',
    showNonCurrentDates: true,
    fixedWeekCount: false,

    headerToolbar: {
      left: 'prev',
      center: 'title',
      right: 'next'
    },

    dayCellContent: function(arg) {
      return arg.date.getDate();
    },

    dayCellDidMount: function(info) {
      const d = new Date(info.date.getTime() - info.date.getTimezoneOffset() * 60000);
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      const cellDateStr = `${y}-${m}-${day}`;
      const events = window.exerciseEvents || [];
      const todaysEvents = events.filter(ev => ev.date === cellDateStr);

      if (todaysEvents.length === 0) return;

      const hasRecord = todaysEvents.some(ev => ev.type === "record");

      const dot = document.createElement('div');
      dot.style.cssText = `
        width:13px; height:13px;
        background-color:${hasRecord ? 'orange' : 'blue'};
        border-radius:50%;
        position:absolute; bottom:2px;
        left:50%; transform:translateX(-50%);
        z-index:20;
      `;

      info.el.style.position = 'relative';
      info.el.appendChild(dot);
    },

    dateClick: function(info) {
  const d = new Date(info.date.getTime() - info.date.getTimezoneOffset() * 60000);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");

  window.selectedDate = `${y}-${m}-${day}`;
  showPlans();
}
  });

  calendar.render();
});