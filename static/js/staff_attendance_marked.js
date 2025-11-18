(function(){
  const rootId = 'staff-attendance-root';
  const root = document.getElementById(rootId);
  if(!root) return;

  const urls = {
    attendanceList: root.dataset.attendanceListUrl,
    attendanceExport: root.dataset.attendanceExportUrl
  };

  function escapeHtml(s){ return String(s||'').replace(/[&<>"'`]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','`':'&#x60;'}[c])); }

  document.addEventListener('DOMContentLoaded', function(){
    const attendanceDate = document.getElementById('attendanceDate');
    const attendanceDept = document.getElementById('attendanceDept');
    const historyDays = document.getElementById('historyDays');
    const attendanceBody = document.getElementById('attendanceBody');
    const totalStaffCount = document.getElementById('totalStaffCount');
    const presentCountEl = document.getElementById('presentCount');
    const absentCountEl = document.getElementById('absentCount');
    const attendanceExport = document.getElementById('attendanceExport');

    if(attendanceDate) attendanceDate.value = new Date().toISOString().slice(0,10);

    async function fetchAttendance(){
      try{
        if(!urls.attendanceList) return;
        const date = attendanceDate ? attendanceDate.value : '';
        const dept = attendanceDept ? attendanceDept.value : '';
        const days = historyDays ? historyDays.value || 7 : 7;
        const params = new URLSearchParams();
        if(date) params.set('date', date);
        if(dept) params.set('department', dept);
        if(days) params.set('days', days);

        const res = await fetch(urls.attendanceList + '?' + params.toString());
        if(!res.ok) return;
        const j = await res.json();
        const recs = j.records || [];
        if(totalStaffCount) totalStaffCount.textContent = recs.length;
        if(presentCountEl) presentCountEl.textContent = recs.filter(r=>r.status==='present').length;
        if(absentCountEl) absentCountEl.textContent = recs.filter(r=>r.status==='absent').length;

        if(attendanceBody){
          attendanceBody.innerHTML = '';
          recs.forEach(r=>{
            const tr = document.createElement('tr');
            const photoHtml = r.photo_url ? `<img src="${r.photo_url}" class="staff-photo">` : '';
            tr.innerHTML = `<td>${photoHtml}<strong>${escapeHtml(r.full_name||r.username)}</strong><div class="small text-muted">${escapeHtml(r.username)}</div></td><td>${escapeHtml(r.department)}</td><td>${escapeHtml(r.position)}</td><td>${escapeHtml(r.status)}</td><td>${r.last_attendance?new Date(r.last_attendance).toLocaleString():'-'}</td><td><button class='btn btn-sm btn-light view-details' data-staff='${r.staff_id}'>Details</button></td>`;
            attendanceBody.appendChild(tr);
          });
        }

        if(attendanceExport) attendanceExport.href = urls.attendanceExport + '?' + params.toString();
      }catch(e){ console.warn('attendance fetch failed', e); }
    }

    fetchAttendance();
    const refresh = document.getElementById('attendanceRefresh');
    if(refresh) refresh.addEventListener('click', fetchAttendance);

    document.body.addEventListener('click', function(ev){
      if(ev.target && ev.target.matches('.view-details')){
        const staffId = ev.target.dataset.staff;
        (async ()=>{
          try{
            if(!urls.attendanceList) return;
            const date = attendanceDate ? attendanceDate.value : '';
            const days = historyDays ? historyDays.value || 7 : 7;
            const res = await fetch(urls.attendanceList + '?date=' + encodeURIComponent(date||'') + '&days=' + encodeURIComponent(days) + '&staff_id=' + encodeURIComponent(staffId));
            if(!res.ok) return;
            const j = await res.json();
            const rec = (j.records||[])[0];
            if(!rec) return alert('Details not found');
            let msg = `Name: ${rec.full_name || rec.username}\nDepartment: ${rec.department}\nPosition: ${rec.position}\nToday: ${rec.status}\nLast: ${rec.last_attendance || '-'}\n\nRecent History:\n`;
            for(let i=0;i<rec.history_dates.length;i++){ msg += `${rec.history_dates[i]}: ${rec.history[i] || '-'}\n`; }
            alert(msg);
          }catch(e){ console.error(e); }
        })();
      }
    });
  });
})();