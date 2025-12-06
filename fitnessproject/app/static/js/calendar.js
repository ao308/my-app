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
      right: 'next'
    },
    dayCellContent: function(arg) {
      if (arg.isOther) {
        return '';
      }
      return arg.date.getDate();
    },
    events: window.exerciseEvents || [],

    // ✅ 修正済み：/exercise/new に飛ぶように変更
    dateClick: function(info) {
      const clickedDate = info.dateStr;
      window.location.href = `/exercise/new/?date=${clickedDate}`;
    }
  });

  calendar.render();

  // 曜日クリック → 運動予定画面へ
  document.querySelectorAll('.fc-col-header-cell').forEach(cell => {
    cell.addEventListener('click', function() {
      const weekdayText = cell.innerText.trim();
      window.location.href = `/exercise/schedule/?weekday=${weekdayText}`;
    });
  });
});