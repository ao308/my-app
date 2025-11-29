/* global FullCalendar */
document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');

  if (!calendarEl) {
    console.warn('calendarEl is null');
    return;
  }

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: window.innerWidth < 576 ? 'listWeek' : 'dayGridMonth',
    locale: 'ja',
    contentHeight: 'auto',
    showNonCurrentDates: false,
    headerToolbar: {
      left: 'prev',
      center: 'title',
      right: 'next'                // 右は空
    },
    dayCellContent: function(arg) {
      if (arg.isOther) {
        return '';
      }
      return arg.date.getDate();
    },
    events: window.exerciseEvents || [],
  
    dateClick: function(info) {
      const clickedDate = info.dateStr; // 例: "2025-11-29"
      // 入力画面に遷移（GETパラメータで日付を渡す）
      window.location.href = `/event/new?date=${clickedDate}`;
    }
  });

  calendar.render();
});