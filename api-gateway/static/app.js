const sections = ['dashboard', 'guests', 'rooms', 'bookings', 'payments', 'staff', 'feedbacks'];
const API_BASE = 'http://localhost:8000';
const content = document.getElementById('content');
const pageTitle = document.getElementById('pageTitle');
const pageSubtitle = document.getElementById('pageSubtitle');
const pageActions = document.getElementById('pageActions');
const toastWrap = document.getElementById('toastWrap');
const sidebarToggle = document.getElementById('sidebarToggle');

const serviceConfig = {
  guests: {
    labels: ['id','first_name','last_name','email','phone','nationality','created_at'],
    createFields: ['first_name','last_name','email','phone','nationality'],
    updateFields: ['first_name','last_name','email','phone','nationality'],
    path:`${API_BASE}/api/guests`,
    supportsDelete:true,
    supportsPut:true
  },
  rooms: {
    labels:['id','room_number','room_type','price_per_night','floor','is_available','amenities'],
    createFields:['room_number','room_type','price_per_night','floor','amenities'],
    updateFields:['room_type','price_per_night','is_available','amenities'],
    path:`${API_BASE}/api/rooms`,
    supportsDelete:true,
    supportsPut:true
  },
  bookings: {
    labels:['id','guest_id','room_id','check_in_date','check_out_date','status','total_price','created_at'],
    createFields:['guest_id','room_id','check_in_date','check_out_date','total_price'],
    updateFields:['check_in_date','check_out_date','status','total_price'],
    path:`${API_BASE}/api/bookings`,
    supportsDelete:true,
    supportsPut:true
  },
  payments: {
    labels:['id','booking_id','amount','payment_method','status','transaction_id','created_at'],
    createFields:['booking_id','amount','payment_method'],
    updateFields:['status'],
    path:`${API_BASE}/api/payments`,
    supportsDelete:false,
    supportsPut:true
  },
  staff: {
    labels:['id','first_name','last_name','role','department','email','phone'],
    createFields:['first_name','last_name','role','department','email','phone'],
    updateFields:['role','department','email','phone'],
    path:`${API_BASE}/api/staff`,
    supportsDelete:true,
    supportsPut:true
  },
  feedbacks: {
    labels:['id','guest_id','booking_id','rating','comment','created_at'],
    createFields:['guest_id','booking_id','rating','comment'],
    updateFields:['rating','comment'],
    path:`${API_BASE}/api/feedbacks`,
    supportsDelete:true,
    supportsPut:true
  },
};

function prettyTitle(name) {
  if (name === 'dashboard') return 'Dashboard';
  if (name === 'staff') return 'Staff';
  if (name === 'feedbacks') return 'Feedback';
  return name.charAt(0).toUpperCase() + name.slice(1);
}

function prettyEntity(name) {
  if (name === 'dashboard') return 'Dashboard';
  if (name === 'guests') return 'Guest';
  if (name === 'rooms') return 'Room';
  if (name === 'bookings') return 'Booking';
  if (name === 'payments') return 'Payment';
  if (name === 'staff') return 'Staff member';
  if (name === 'feedbacks') return 'Feedback';
  return name;
}

function showToast(kind, title, msg, timeoutMs = 2600) {
  if (!toastWrap) return;
  const el = document.createElement('div');
  el.className = `toast ${kind}`;
  el.innerHTML = `
    <div class="toast-dot" aria-hidden="true"></div>
    <div>
      <p class="toast-title"></p>
      <p class="toast-msg"></p>
    </div>
  `;
  el.querySelector('.toast-title').textContent = title;
  el.querySelector('.toast-msg').textContent = msg;
  toastWrap.appendChild(el);
  window.setTimeout(() => {
    if (el.parentNode === toastWrap) toastWrap.removeChild(el);
  }, timeoutMs);
}

function confirmDialog({
  title = 'Confirm action',
  message = 'Are you sure?',
  dangerHint = '',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
} = {}) {
  return new Promise((resolve) => {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');

    const card = document.createElement('div');
    card.className = 'modal-card';

    const header = document.createElement('div');
    header.className = 'modal-header';

    const t = document.createElement('div');
    t.className = 'modal-title';
    t.textContent = title;

    const closeX = document.createElement('button');
    closeX.className = 'btn btn-ghost';
    closeX.type = 'button';
    closeX.textContent = 'Close';

    header.append(t, closeX);

    const body = document.createElement('div');
    body.className = 'modal-body';

    const p = document.createElement('p');
    p.className = 'confirm-text';
    p.textContent = message;
    body.appendChild(p);

    if (dangerHint) {
      const hint = document.createElement('div');
      hint.className = 'confirm-danger';
      hint.innerHTML = `<span class="dot" aria-hidden="true"></span><span></span>`;
      hint.querySelector('span:last-child').textContent = dangerHint;
      body.appendChild(hint);
    }

    const footer = document.createElement('div');
    footer.className = 'actions';
    footer.style.justifyContent = 'flex-end';
    footer.style.marginTop = '14px';

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn btn-ghost';
    cancelBtn.type = 'button';
    cancelBtn.textContent = cancelText;

    const okBtn = document.createElement('button');
    okBtn.className = 'btn btn-danger';
    okBtn.type = 'button';
    okBtn.textContent = confirmText;

    footer.append(cancelBtn, okBtn);
    body.appendChild(footer);

    card.append(header, body);
    modal.appendChild(card);
    document.body.appendChild(modal);

    const cleanup = () => {
      document.removeEventListener('keydown', onKeyDown);
      if (modal.parentNode) document.body.removeChild(modal);
    };
    const finish = (value) => {
      cleanup();
      resolve(value);
    };
    const onKeyDown = (ev) => {
      if (ev.key === 'Escape') finish(false);
    };

    document.addEventListener('keydown', onKeyDown);
    modal.addEventListener('click', (ev) => {
      if (ev.target === modal) finish(false);
    });
    closeX.addEventListener('click', () => finish(false));
    cancelBtn.addEventListener('click', () => finish(false));
    okBtn.addEventListener('click', () => finish(true));

    window.setTimeout(() => okBtn.focus(), 0);
  });
}

function setActive(name) {
  document.querySelectorAll('button[data-section]').forEach(b => {
    const selected = b.dataset.section === name;
    b.setAttribute('aria-selected', selected ? 'true' : 'false');
  });
}

function _normalizeDateForInput(value) {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) {
    const s = String(value).slice(0, 10);
    return s.match(/^\d{4}-\d{2}-\d{2}$/) ? s : '';
  }
  return d.toISOString().slice(0, 10);
}

function _getInputValue(input) {
  if (!input) return '';
  if (input.tagName === 'INPUT' && input.type === 'checkbox') {
    return input.checked;
  }
  if (input.tagName === 'INPUT' && input.type === 'number') {
    return input.value === '' ? null : Number(input.value);
  }
  return input.value;
}

function createFieldInput(field, value = '') {
  const wrap = document.createElement('div');
  wrap.className = 'field';
  const lbl = document.createElement('label');
  lbl.textContent = field.replace(/_/g, ' ');

  const lower = field.toLowerCase();

  const selectOptions = {
    room_type: ['single', 'double', 'suite', 'deluxe'],
    payment_method: ['card', 'cash', 'transfer', 'other'],
    status: ['pending', 'confirmed', 'checked-in', 'checked-out', 'cancelled', 'completed'],
    role: ['receptionist', 'manager', 'housekeeping', 'maintenance', 'other'],
    nationality: ['American', 'British', 'Canadian', 'Australian', 'Other']
  };

  let inputElement;

  if (lower === 'is_available') {
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.className = 'input';
    input.name = field;
    input.checked = Boolean(value);
    inputElement = input;
  } else if (Object.prototype.hasOwnProperty.call(selectOptions, lower)) {
    const select = document.createElement('select');
    select.className = 'input';
    select.name = field;
    const options = selectOptions[lower];
    select.appendChild(new Option(`Select ${field.replace(/_/g, ' ')}`, ''));
    options.forEach((o) => {
      const option = new Option(o.charAt(0).toUpperCase() + o.slice(1), o);
      if (String(value).toLowerCase() === String(o).toLowerCase()) option.selected = true;
      select.appendChild(option);
    });
    inputElement = select;
  } else {
    const input = document.createElement('input');
    input.className = 'input';
    input.name = field;

    if (lower.includes('date')) {
      input.type = 'date';
      input.value = _normalizeDateForInput(value);
      input.addEventListener('focus', () => {
        if (typeof input.showPicker === 'function') {
          input.showPicker();
        }
      });
    } else if (lower.includes('email')) {
      input.type = 'email';
      input.value = value;
    } else if (lower.includes('phone')) {
      input.type = 'tel';
      input.value = value;
    } else if (['id', 'guest_id', 'room_id', 'booking_id', 'floor'].includes(lower)) {
      input.type = 'number';
      input.value = value || '';
      input.step = '1';
    } else if (['price_per_night', 'total_price', 'amount', 'rating'].includes(lower)) {
      input.type = 'number';
      input.value = value || '';
      input.step = '0.01';
    } else {
      input.type = 'text';
      input.value = value;
    }

    input.placeholder = field.replace(/_/g, ' ');
    input.autocomplete = 'off';

    inputElement = input;
  }

  wrap.append(lbl, inputElement);
  return {wrap, input: inputElement};
}

function statusPill(value) {
  const v = String(value ?? '').toLowerCase();
  const span = document.createElement('span');
  span.className = 'pill neutral';
  span.textContent = value ?? '';
  if (!value && value !== 0) return span;

  if (v.includes('active') || v.includes('on duty') || v.includes('available') || v === 'true') {
    span.className = 'pill success';
  } else if (v.includes('confirmed') || v.includes('paid')) {
    span.className = 'pill info';
  } else if (v.includes('pending') || v.includes('partial') || v.includes('reserved') || v.includes('maintenance')) {
    span.className = 'pill warn';
  } else if (v.includes('completed') || v.includes('off duty')) {
    span.className = 'pill neutral';
  }
  return span;
}

function formatCell(section, label, value) {
  if (label === 'is_available') return statusPill(value ? 'Available' : 'Occupied');
  if (label === 'status') return statusPill(value || '');
  if (label === 'rating') {
    const n = Number(value);
    if (!Number.isFinite(n)) return document.createTextNode(String(value ?? ''));
    const stars = '★★★★★'.slice(0, Math.max(0, Math.min(5, Math.round(n)))) +
      '☆☆☆☆☆'.slice(0, Math.max(0, 5 - Math.round(n)));
    const span = document.createElement('span');
    span.textContent = `${stars} (${n})`;
    return span;
  }
  return document.createTextNode(String(value ?? ''));
}

function renderTable(section, data, reloadFn) {
  const cfg = serviceConfig[section];
  const table = document.createElement('table');

  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  cfg.labels.forEach(label => {
    const th = document.createElement('th'); th.textContent = label; headerRow.appendChild(th);
  });
  const actionTh = document.createElement('th'); actionTh.textContent='Actions'; headerRow.appendChild(actionTh);
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  data.forEach(item => {
    const row = document.createElement('tr');
    cfg.labels.forEach(label => {
      const td = document.createElement('td');
      td.appendChild(formatCell(section, label, item[label]));
      row.appendChild(td);
    });

    const actions = document.createElement('td');
    const actionBar = document.createElement('div');
    actionBar.className = 'actions';
    const editBtn = document.createElement('button'); editBtn.textContent='Edit';
    editBtn.className = 'btn';
    editBtn.addEventListener('click', async ()=>{
      const updateFields = cfg.updateFields;
      let form = document.createElement('form');
      form.className = 'modal-form';
      const updateInputs = {};
      updateFields.forEach(field => {
        const {wrap,input} = createFieldInput(field, item[field] ?? '');
        form.appendChild(wrap);
        updateInputs[field] = input;
      });
      const save = document.createElement('button'); save.textContent='Save'; save.className = 'btn btn-primary';
      const cancel = document.createElement('button'); cancel.textContent='Cancel'; cancel.className = 'btn btn-ghost';
      cancel.type = 'button';
      const footer = document.createElement('div');
      footer.className = 'actions';
      footer.style.justifyContent = 'flex-end';
      footer.style.gridColumn = '1 / -1';
      footer.append(save, cancel);
      form.appendChild(footer);
      const modal = document.createElement('div');
      modal.className = 'modal';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');

      const card = document.createElement('div');
      card.className = 'modal-card';
      const header = document.createElement('div');
      header.className = 'modal-header';
      const title = document.createElement('div');
      title.className = 'modal-title';
      title.textContent = `Edit ${prettyEntity(section)} #${item.id ?? ''}`.trim();
      const closeX = document.createElement('button');
      closeX.className = 'btn btn-ghost';
      closeX.type = 'button';
      closeX.textContent = 'Close';
      header.append(title, closeX);

      const body = document.createElement('div');
      body.className = 'modal-body';
      body.appendChild(form);

      card.append(header, body);
      modal.appendChild(card);
      document.body.appendChild(modal);

      const close = () => {
        if (modal.parentNode) document.body.removeChild(modal);
        document.removeEventListener('keydown', onKeyDown);
      };
      const onKeyDown = (ev) => {
        if (ev.key === 'Escape') close();
      };
      document.addEventListener('keydown', onKeyDown);

      modal.addEventListener('click', (ev) => {
        if (ev.target === modal) close();
      });
      cancel.addEventListener('click', close);
      closeX.addEventListener('click', close);

      form.addEventListener('submit', async ev=>{
        ev.preventDefault();
        const payload = {};
        updateFields.forEach(field=>payload[field]=_getInputValue(updateInputs[field]));
        try {
          save.disabled = true;
          const r = await fetch(`${cfg.path}/${item.id}`, {
            method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)
          });
          if (!r.ok) throw new Error(await r.text());
          showToast('success', 'Updated', `${prettyEntity(section)} updated successfully.`);
          close();
          reloadFn();
        } catch(err){
          showToast('error', 'Update failed', String(err?.message ?? err));
        } finally {
          save.disabled = false;
        }
      });
    });

    actionBar.appendChild(editBtn);
    if (cfg.supportsDelete) {
      const delBtn = document.createElement('button'); delBtn.textContent='Delete';
      delBtn.className = 'btn btn-danger';
      delBtn.addEventListener('click', async ()=>{
        const ok = await confirmDialog({
          title: 'Delete record?',
          message: `This will permanently delete ${prettyEntity(section).toLowerCase()} #${item.id ?? ''}.`,
          dangerHint: 'This action cannot be undone.',
          confirmText: 'Delete',
          cancelText: 'Cancel',
        });
        if (!ok) return;
        try {
          const r = await fetch(`${cfg.path}/${item.id}`, {method:'DELETE'});
          if (!r.ok) throw new Error(await r.text());
          showToast('success', 'Deleted', `${prettyEntity(section)} deleted.`);
          reloadFn();
        } catch(err){
          showToast('error', 'Delete failed', String(err?.message ?? err));
        }
      });
      actionBar.appendChild(delBtn);
    }
    actions.appendChild(actionBar);
    row.appendChild(actions);
    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  const wrap = document.createElement('div');
  wrap.className = 'table-wrap';
  wrap.appendChild(table);
  return wrap;
}

function clearActions() {
  if (pageActions) pageActions.innerHTML = '';
}

function setPageHead(title, subtitle) {
  if (pageTitle) pageTitle.textContent = title;
  if (pageSubtitle) pageSubtitle.textContent = subtitle;
}

async function fetchJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Status ${res.status}`);
  return res.json();
}

function createAddButton(section, onClick) {
  const btn = document.createElement('button');
  btn.className = 'btn btn-primary';
  btn.type = 'button';
  btn.textContent = `+ Add ${prettyEntity(section)}`;
  btn.addEventListener('click', onClick);
  return btn;
}

function buildSearch(onInput) {
  const wrap = document.createElement('div');
  wrap.className = 'search';
  wrap.innerHTML = `<span class="sicon" aria-hidden="true">🔎</span>`;
  const input = document.createElement('input');
  input.className = 'control';
  input.type = 'search';
  input.placeholder = 'Search...';
  input.addEventListener('input', () => onInput(input.value));
  wrap.appendChild(input);
  return {wrap, input};
}

function openCreateModal(section, onCreated) {
  const cfg = serviceConfig[section];
  const form = document.createElement('form');
  form.className = 'modal-form';

  const inputs = {};
  cfg.createFields.forEach((field) => {
    const {wrap, input} = createFieldInput(field, '');
    inputs[field] = input;
    form.appendChild(wrap);
  });

  const save = document.createElement('button');
  save.className = 'btn btn-primary';
  save.type = 'submit';
  save.textContent = 'Create';

  const cancel = document.createElement('button');
  cancel.className = 'btn btn-ghost';
  cancel.type = 'button';
  cancel.textContent = 'Cancel';

  const footer = document.createElement('div');
  footer.className = 'actions';
  footer.style.justifyContent = 'flex-end';
  footer.style.gridColumn = '1 / -1';
  footer.append(save, cancel);
  form.appendChild(footer);

  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');

  const card = document.createElement('div');
  card.className = 'modal-card';

  const header = document.createElement('div');
  header.className = 'modal-header';
  const title = document.createElement('div');
  title.className = 'modal-title';
  title.textContent = `Add ${prettyEntity(section)}`;
  const closeX = document.createElement('button');
  closeX.className = 'btn btn-ghost';
  closeX.type = 'button';
  closeX.textContent = 'Close';
  header.append(title, closeX);

  const body = document.createElement('div');
  body.className = 'modal-body';
  body.appendChild(form);

  card.append(header, body);
  modal.appendChild(card);
  document.body.appendChild(modal);

  const close = () => {
    document.removeEventListener('keydown', onKeyDown);
    if (modal.parentNode) document.body.removeChild(modal);
  };
  const onKeyDown = (ev) => {
    if (ev.key === 'Escape') close();
  };
  document.addEventListener('keydown', onKeyDown);
  modal.addEventListener('click', (ev) => {
    if (ev.target === modal) close();
  });
  cancel.addEventListener('click', close);
  closeX.addEventListener('click', close);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {};
    cfg.createFields.forEach((field) => (payload[field] = _getInputValue(inputs[field])));
    try {
      save.disabled = true;
      const r = await fetch(cfg.path, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error(await r.text());
      showToast('success', 'Created', `${prettyEntity(section)} created successfully.`);
      close();
      onCreated?.();
    } catch (err) {
      showToast('error', 'Create failed', String(err?.message ?? err));
    } finally {
      save.disabled = false;
    }
  });

  window.setTimeout(() => {
    const first = cfg.createFields[0];
    if (first && inputs[first]) inputs[first].focus();
  }, 0);
}

function matchesQuery(item, query) {
  if (!query) return true;
  const q = query.toLowerCase();
  try {
    return JSON.stringify(item).toLowerCase().includes(q);
  } catch {
    return String(item).toLowerCase().includes(q);
  }
}

async function renderServicePage(section) {
  const cfg = serviceConfig[section];
  setPageHead(prettyTitle(section), `Manage hotel ${prettyTitle(section).toLowerCase()} and reservations`);
  clearActions();

  const addBtn = createAddButton(section, () => openCreateModal(section, () => load(section)));
  pageActions?.appendChild(addBtn);

  content.innerHTML = `<div class="empty">Loading...</div>`;
  const data = await fetchJson(cfg.path);
  const all = Array.isArray(data) ? data : [];

  content.innerHTML = '';

  const toolbar = document.createElement('div');
  toolbar.className = 'toolbar';
  const {wrap: searchWrap} = buildSearch((q) => {
    const filtered = all.filter((x) => matchesQuery(x, q));
    tableHost.replaceChildren(renderTable(section, filtered, () => load(section)));
    if (filtered.length === 0) tableHost.prepend(emptyRow());
  });
  toolbar.appendChild(searchWrap);
  content.appendChild(toolbar);

  const tableHost = document.createElement('div');
  content.appendChild(tableHost);

  const emptyRow = () => {
    const p = document.createElement('div');
    p.className = 'empty';
    p.textContent = 'No records found.';
    return p;
  };

  if (all.length === 0) {
    tableHost.appendChild(emptyRow());
    return;
  }

  tableHost.appendChild(renderTable(section, all, () => load(section)));
}

function money(n) {
  const x = Number(n);
  if (!Number.isFinite(x)) return '$0';
  return x.toLocaleString(undefined, {style: 'currency', currency: 'USD', maximumFractionDigits: 0});
}

function toDateOnly(s) {
  if (!s) return '';
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return String(s).slice(0, 10);
  return d.toISOString().slice(0, 10);
}

async function renderDashboard() {
  setPageHead('Dashboard', `Welcome back. Here's your hotel overview.`);
  clearActions();
  content.innerHTML = `<div class="empty">Loading overview...</div>`;

  const [guests, rooms, bookings, payments] = await Promise.all([
    fetchJson(serviceConfig.guests.path).catch(() => []),
    fetchJson(serviceConfig.rooms.path).catch(() => []),
    fetchJson(serviceConfig.bookings.path).catch(() => []),
    fetchJson(serviceConfig.payments.path).catch(() => []),
  ]);

  const guestCount = Array.isArray(guests) ? guests.length : 0;
  const roomList = Array.isArray(rooms) ? rooms : [];
  const totalRooms = roomList.length;
  const availableRooms = roomList.filter(r => !!r.is_available).length;
  const occupiedRooms = Math.max(0, totalRooms - availableRooms);
  const occupancy = totalRooms ? ((occupiedRooms / totalRooms) * 100) : 0;

  const paymentList = Array.isArray(payments) ? payments : [];
  const today = new Date().toISOString().slice(0, 10);
  const todaysRevenue = paymentList
    .filter(p => toDateOnly(p.created_at) === today || toDateOnly(p.date) === today)
    .reduce((sum, p) => sum + (Number(p.amount) || 0), 0);

  const bookingList = Array.isArray(bookings) ? bookings : [];
  const checkinsToday = bookingList.filter(b => toDateOnly(b.check_in_date) === today).length;

  content.innerHTML = '';

  const stats = document.createElement('div');
  stats.className = 'stats';
  const makeStat = (k, v, icon) => {
    const el = document.createElement('div');
    el.className = 'stat';
    el.innerHTML = `
      <div>
        <div class="k"></div>
        <div class="v"></div>
      </div>
      <div class="badge" aria-hidden="true"></div>
    `;
    el.querySelector('.k').textContent = k;
    el.querySelector('.v').textContent = v;
    el.querySelector('.badge').textContent = icon;
    return el;
  };
  stats.append(
    makeStat('Occupancy Rate', `${occupancy.toFixed(1)}%`, '📈'),
    makeStat('Total Guests', String(guestCount), '👥'),
    makeStat('Available Rooms', String(availableRooms), '🛏'),
    makeStat("Today's Revenue", money(todaysRevenue), '$'),
    makeStat('Check-ins Today', String(checkinsToday), '✅'),
    makeStat('Avg. Rating', (() => {
      const fb = fetchJson(serviceConfig.feedbacks.path).catch(() => []);
      // quick placeholder; will be replaced below
      return '—';
    })(), '⭐'),
  );
  content.appendChild(stats);

  // Replace avg rating stat with real value
  try {
    const feedbacks = await fetchJson(serviceConfig.feedbacks.path);
    const list = Array.isArray(feedbacks) ? feedbacks : [];
    const avg = list.length ? (list.reduce((s, f) => s + (Number(f.rating) || 0), 0) / list.length) : 0;
    stats.querySelectorAll('.stat .k').forEach((kEl) => {
      if (kEl.textContent === 'Avg. Rating') {
        kEl.parentElement.querySelector('.v').textContent = list.length ? avg.toFixed(1) : '—';
      }
    });
  } catch { /* ignore */ }

  const recent = document.createElement('div');
  recent.className = 'card';
  recent.style.marginTop = '16px';

  const head = document.createElement('div');
  head.className = 'card-pad';
  head.innerHTML = `<div style="font-weight:900; font-size:1.05rem;">Recent Bookings</div><div class="muted" style="margin-top:4px;">Latest reservations pulled from the booking service</div>`;
  recent.appendChild(head);

  const recentList = bookingList
    .slice()
    .sort((a, b) => (new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()) || (Number(b.id) - Number(a.id)))
    .slice(0, 8);

  const table = renderTable('bookings', recentList, () => load('dashboard'));
  table.style.borderTopLeftRadius = '0px';
  table.style.borderTopRightRadius = '0px';
  recent.appendChild(table);
  content.appendChild(recent);
}

async function load(name) {
  setActive(name);
  clearActions();
  try {
    if (name === 'dashboard') {
      await renderDashboard();
      return;
    }
    await renderServicePage(name);
  } catch (error) {
    setPageHead(prettyTitle(name), 'Could not load data from the service.');
    content.innerHTML = `<div class="empty">Error: ${error.message}</div>`;
  }
}

for (const btn of document.querySelectorAll('button[data-section]')) {
  btn.addEventListener('click', () => load(btn.dataset.section));
}

if (sidebarToggle) {
  const saved = localStorage.getItem('sidebarCollapsed');
  if (saved === '1') document.body.classList.add('sidebar-collapsed');
  sidebarToggle.addEventListener('click', () => {
    document.body.classList.toggle('sidebar-collapsed');
    localStorage.setItem('sidebarCollapsed', document.body.classList.contains('sidebar-collapsed') ? '1' : '0');
  });
}

load('dashboard');
