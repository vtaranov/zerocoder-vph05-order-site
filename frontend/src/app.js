const $ = (id) => document.getElementById(id);
const form = $('application-form');
const serviceSelect = $('service');
const budget = $('budget');
const money = (value) => new Intl.NumberFormat('ru-RU').format(value) + ' ₽';
const startedAt = performance.now();
const clicks = [];
const pointerSamples = [];
let services = [];
let lastPointer = 0;
let visits = 1;
try {
  visits = Math.min(1000000, Number(localStorage.getItem('atelier-visits') || 0) + 1);
  if (!Number.isFinite(visits)) visits = 1;
  localStorage.setItem('atelier-visits', String(visits));
} catch { /* Browser storage may be unavailable. */ }
function showStatus(message, kind) {
  $('submit-status').textContent = message;
  $('submit-status').className = kind;
  $('submit-status').focus();
}
function updateBudget() { $('budget-value').textContent = money(Number(budget.value)); }
serviceSelect.addEventListener('change', () => {
  const service = services.find(item => item.id === Number(serviceSelect.value));
  if (!service) {
    budget.min = budget.max = budget.value = '0';
    $('budget-value').textContent = '-';
    $('budget-min').textContent = $('budget-max').textContent = '-';
    $('service-description').textContent = 'Выберите услугу из каталога.';
    return;
  }
  budget.min = service.budget_min;
  budget.max = service.budget_max;
  budget.value = Math.round((service.budget_min + service.budget_max) / 2);
  $('budget-min').textContent = money(service.budget_min);
  $('budget-max').textContent = money(service.budget_max);
  $('service-description').textContent = service.description;
  updateBudget();
});
budget.addEventListener('input', updateBudget);
document.addEventListener('click', event => {
  if (clicks.length >= 100) return;
  const control = event.target.closest('button, a, select, summary');
  if (control) clicks.push((control.id || control.getAttribute('href') || control.tagName).slice(0,80));
});
document.addEventListener('pointermove', event => {
  if (pointerSamples.length < 60 && performance.now() - lastPointer > 2000) {
    pointerSamples.push([Math.round(event.clientX), Math.round(event.clientY)]);
    lastPointer = performance.now();
  }
}, {passive:true});
async function loadServices() {
  try {
    const response = await fetch('/api/services');
    if (!response.ok) throw new Error('catalog');
    services = await response.json();
    if (!services.length) {
      $('load-status').textContent = 'Каталог пока пуст. Администратор скоро добавит услуги.';
      return;
    }
    for (const service of services) {
      const option = document.createElement('option');
      option.value = service.id;
      option.textContent = service.name;
      serviceSelect.append(option);
    }
    $('form-fields').disabled = false;
    $('load-status').textContent = '';
  } catch {
    $('load-status').textContent = 'Не удалось загрузить услуги. Обновите страницу, чтобы попробовать ещё раз.';
  }
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const data = Object.fromEntries(new FormData(form));
  data.service_id = Number(data.service_id);
  data.budget = Number(data.budget);
  data.consent = $('consent').checked;
  data.metrics = {
    time_on_page: Math.min(604800, Math.round((performance.now() - startedAt) / 1000)),
    visits, clicks, pointer_samples: pointerSamples,
    technical: {language: navigator.language, viewport: `${innerWidth}x${innerHeight}`, timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || '', user_agent: navigator.userAgent.slice(0,300)}
  };
  $('submit').disabled = true;
  $('submit').textContent = 'Отправляем…';
  $('submit-status').textContent = '';
  try {
    const response = await fetch('/api/applications', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
    const isJSON = (response.headers.get('content-type') || '').includes('application/json');
    if (!isJSON) throw new Error('Сервис временно недоступен. Ваши данные остались в форме - попробуйте ещё раз.');
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Проверьте заполнение формы.');
    showStatus(`${result.message} Номер: ${result.id}. Мы свяжемся с вами удобным способом.`, 'success');
    form.reset(); serviceSelect.dispatchEvent(new Event('change'));
  } catch (error) {
    showStatus(error.message === 'Failed to fetch' ? 'Нет связи с сервером. Ваши данные остались в форме - попробуйте ещё раз.' : error.message, 'error');
  } finally {
    $('submit').disabled = false;
    $('submit').innerHTML = 'Отправить заявку <span aria-hidden="true">↗</span>';
  }
});
loadServices();
