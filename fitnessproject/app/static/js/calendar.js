/* global FullCalendar */
function getCookie(name) {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === name) return decodeURIComponent(value);
  }
  return null;
}

document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) return;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: window.innerWidth < 576 ? 'listWeek' : 'dayGridMonth',
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
      const cellDateStr = info.date.toLocaleDateString("sv-SE");
      const events = window.exerciseEvents || [];

      const todaysEvents = events.filter(ev => ev.date === cellDateStr);

  // ★ イベントがない日は dot を付けない
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
      window.selectedDate = info.dateStr;
      showPlans();
    }
  });

  calendar.render();
});

function goTo(action, id, date) {
  const url = action === "new"
    ? `/exercise/new/?date=${date}`
    : `/exercise/record/?id=${id}`;
  window.location.href = url;
}

function formatJapaneseDate(dateStr) {
  const d = new Date(dateStr);
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const weekday = ["日", "月", "火", "水", "木", "金", "土"][d.getDay()];
  return `${month}月${day}日(${weekday})`;
}

function showPlans() {
  const date = window.selectedDate;

  document.getElementById("plan-date").textContent = formatJapaneseDate(date);

  const planList = document.getElementById("plan-list");
  planList.innerHTML = "";

  const events = window.exerciseEvents || [];

  const schedules = events.filter(ev => ev.type === "schedule" && ev.date === date);
  const records = events.filter(ev => ev.type === "record" && ev.date === date);

  // ★ 記録済みの予定を除外
  const unrecordedSchedules = schedules.filter(s =>
    !records.some(r => r.title === s.title && r.date === s.date)
  );

  // ★ 予定セクション（未記録のみ）
  if (unrecordedSchedules.length > 0) {
    const header = document.createElement("div");
    header.className = "fw-bold mt-2 mb-1";
    header.textContent = "予定";
    planList.appendChild(header);

    unrecordedSchedules.forEach(ev => {
      const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-center";

      const span = document.createElement("span");
      span.textContent = ev.title;
      li.appendChild(span);

      const editBtn = document.createElement("button");
      editBtn.className = "btn btn-sm btn-secondary";
      editBtn.textContent = "編集";
      editBtn.onclick = () => window.location.href = `/exercise/edit/${ev.id}/`;

      const recordBtn = document.createElement("button");
      recordBtn.className = "btn btn-sm btn-primary";
      recordBtn.textContent = "記録";
      recordBtn.onclick = () => goTo("record", ev.id, date);

      const deleteBtn = document.createElement("button");
      deleteBtn.className = "btn btn-sm btn-danger";
      deleteBtn.textContent = "削除";
      deleteBtn.onclick = () => deletePlan(ev.id);

      const btnGroup = document.createElement("div");
      btnGroup.className = "d-flex align-items-center";

      const recordWrapper = document.createElement("div");
      recordWrapper.className = "me-3";
      recordWrapper.appendChild(recordBtn);
      btnGroup.appendChild(recordWrapper);

      const subGroup = document.createElement("div");
      subGroup.className = "d-flex gap-1";
      subGroup.appendChild(editBtn);
      subGroup.appendChild(deleteBtn);

      btnGroup.appendChild(subGroup);

      li.appendChild(btnGroup);
      planList.appendChild(li);
    });
  }

  // ★ 記録セクション（背景色つき）
  if (records.length > 0) {
    const header = document.createElement("div");
    header.className = "fw-bold mt-3 mb-1";
    header.textContent = "記録";
    planList.appendChild(header);

    records.forEach(ev => {
      const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-center bg-success-subtle";

      const span = document.createElement("span");
      span.textContent = ev.title;
      li.appendChild(span);

      const editBtn = document.createElement("button");
      editBtn.className = "btn btn-sm btn-secondary";
      editBtn.textContent = "編集";
      editBtn.onclick = () => window.location.href = `/exercise/record/edit/?id=${ev.id}`;

      const deleteBtn = document.createElement("button");
      deleteBtn.className = "btn btn-sm btn-danger";
      deleteBtn.textContent = "削除";
      deleteBtn.onclick = () => deleteRecord(ev.id);

      const btnGroup = document.createElement("div");
      btnGroup.className = "d-flex align-items-center";

      const spacer = document.createElement("div");
      spacer.className = "me-3";
      btnGroup.appendChild(spacer);

      const subGroup = document.createElement("div");
      subGroup.className = "d-flex gap-1";
      subGroup.appendChild(editBtn);
      subGroup.appendChild(deleteBtn);

      btnGroup.appendChild(subGroup);

      li.appendChild(btnGroup);
      planList.appendChild(li);
    });
  }

  // 予定も記録もない場合
  if (schedules.length === 0 && records.length === 0) {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.textContent = "登録している予定・記録はありません。";
    planList.appendChild(li);
  }

  document.getElementById("new-plan-btn").onclick = () => {
    window.location.href = `/exercise/new/?date=${date}`;
  };

  document.getElementById("new-record-btn").onclick = () => {
    window.location.href = `/exercise/record/new/?date=${date}`;
  };

  bootstrap.Modal.getOrCreateInstance(document.getElementById("plan-list-modal")).show();
}

function deletePlan(id) {
  if (!confirm("本当に削除しますか？")) return;

  fetch(`/exercise/delete/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken")
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const modalEl = document.getElementById("plan-list-modal");
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();

      document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
      document.body.classList.remove('modal-open');

      window.location.href = "/home";
    } else {
      alert("削除に失敗しました");
    }
  })
  .catch(error => console.error("削除エラー:", error));
}

function deleteRecord(id) {
  if (!confirm("本当に削除しますか？")) return;

  fetch(`/record/delete/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken")
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const modalEl = document.getElementById("plan-list-modal");
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();

      document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
      document.body.classList.remove('modal-open');

      window.location.href = "/home";
    } else {
      alert("削除に失敗しました");
    }
  })
  .catch(error => console.error("削除エラー:", error));
}