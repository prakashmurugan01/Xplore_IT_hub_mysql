(function(){
  // Read URLs and config from the root element's data attributes
  const root = document.getElementById('superadmin-dashboard-root');
  if(!root) return;
  const urls = {
    superUpdates: root.dataset.superUpdatesUrl,
    attendanceList: root.dataset.admin2AttendanceListUrl,
    attendanceExport: root.dataset.admin2ExportAttendanceUrl,
    oneClickAttendance: root.dataset.oneClickAttendanceUrl,
    downloadReportTemplate: root.dataset.reportUrlTemplate || '/superadmin/download-report/0/'
  };

  // helper
  function escapeHtml(s){ return String(s).replace(/[&<>"'`]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','`':'&#x60;'}[c])); }

  document.addEventListener('DOMContentLoaded', function(){
    // Chart
    const labelsEl = document.getElementById('signup-labels-json');
    const countsEl = document.getElementById('signup-counts-json');
    const labels = labelsEl ? JSON.parse(labelsEl.textContent || '[]') : [];
    const data = countsEl ? JSON.parse(countsEl.textContent || '[]') : [];

    const ctxEl = document.getElementById('signupsChart');
    let signupsChart = null;
    if(ctxEl && window.Chart){
      const ctx = ctxEl.getContext('2d');
      signupsChart = new Chart(ctx, {
        type: 'bar',
        data: { labels: labels, datasets: [{ label: 'Signups', data: data, backgroundColor: '#4F46E5', borderRadius: 6 }] },
        options: { responsive: true, plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } }, scales: { y: { beginAtZero: true } } }
      });
    }

    // polling for super updates
    async function fetchSuperUpdates(){
      try{
        if(!urls.superUpdates) return;
        const res = await fetch(urls.superUpdates);
        if(!res.ok) return;
        const j = await res.json();
        const setText = (id, value)=>{ const el = document.getElementById(id); if(el) el.textContent = value; };
        setText('su_total_students', j.total_students);
        setText('su_total_teachers', j.total_teachers);
        setText('su_total_courses', j.total_courses);
        setText('su_other_count', j.other_count);

        // recent users
        const tbody = document.getElementById('su_recent_users');
        if(tbody){
          tbody.innerHTML = '';
          const reportTemplate = tbody.dataset.reportUrlTemplate || urls.downloadReportTemplate;
          j.recent_users.forEach(u=>{
            const tr = document.createElement('tr');
            tr.setAttribute('data-user-id', u.id);
            const reportUrl = reportTemplate.replace('/0/', `/${u.id}/`);
            tr.innerHTML = `<td>${escapeHtml(u.username)}</td><td>${escapeHtml(u.email)}</td><td>${escapeHtml(u.role)}</td><td>${escapeHtml(u.joined)}</td><td><a class="btn btn-sm btn-light" href="${reportUrl}"><i class="fas fa-download"></i> Report</a></td>`;
            tbody.appendChild(tr);
          });
        }

        if(signupsChart){ signupsChart.data.labels = j.signup_labels; signupsChart.data.datasets[0].data = j.signup_counts; signupsChart.update(); }
      }catch(e){ console.warn('superadmin updates failed', e); }
    }

    fetchSuperUpdates();
    setInterval(fetchSuperUpdates, 10000);

    // Attendance
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
            tr.innerHTML = `<td>${photoHtml}<strong>${escapeHtml(r.full_name||r.username)}</strong><div class="small text-muted">${escapeHtml(r.username)}</div></td><td>${escapeHtml(r.department)}</td><td>${escapeHtml(r.position)}</td><td>${r.status}</td><td>${r.last_attendance?new Date(r.last_attendance).toLocaleString():'-'}</td><td><button class='btn btn-sm btn-light view-details' data-staff='${r.staff_id}'>Details</button></td>`;
            attendanceBody.appendChild(tr);
          });
        }

        if(attendanceExport) attendanceExport.href = urls.attendanceExport + '?' + params.toString();
      }catch(e){ console.warn('attendance fetch failed', e); }
    }

    fetchAttendance();
    const refreshBtn = document.getElementById('attendanceRefresh');
    if(refreshBtn) refreshBtn.addEventListener('click', fetchAttendance);

    // delegate details click
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

    // one-click attendance
    const oneClickBtn = document.getElementById('one-click-attendance');
    if(oneClickBtn){
      oneClickBtn.addEventListener('click', async function(e){
        if(!confirm('Mark attendance now for today using existing check-ins? This will update daily attendance for all staff. Proceed?')) return;
        try{
          const csrftoken = (document.cookie.split('; ').find(r=>r.startsWith('csrftoken='))||'').split('=')[1];
          if(!urls.oneClickAttendance) return alert('Endpoint not configured');
          const res = await fetch(urls.oneClickAttendance, {method: 'POST', headers: {'X-CSRFToken': csrftoken, 'Accept': 'application/json'}});
          if(!res.ok){ alert('Attendance marking failed'); return; }
          const j = await res.json();
          if(j.success){ alert('Attendance marked. Present: '+j.summary.present+' | Absent: '+j.summary.absent); if(typeof fetchSuperUpdates==='function') fetchSuperUpdates(); }
          else { alert('Attendance endpoint returned an error'); }
        }catch(err){ console.error(err); alert('Failed to mark attendance'); }
      });
    }
  });
})();