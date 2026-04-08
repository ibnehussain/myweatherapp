const form        = document.getElementById('search-form');
const cityInput   = document.getElementById('city-input');
const errorMsg    = document.getElementById('error-message');
const resultCard  = document.getElementById('weather-result');
const loading     = document.getElementById('loading');

const cityName    = document.getElementById('city-name');
const icon        = document.getElementById('weather-icon');
const condition   = document.getElementById('weather-condition');
const temperature = document.getElementById('temperature');
const humidity    = document.getElementById('humidity');
const windSpeed   = document.getElementById('wind-speed');
const unitRadios  = document.querySelectorAll('input[name="unit"]');

let lastCity = '';
let lastUnit = 'metric';

// ── Fetch weather from Flask backend ──────────────────────────
async function fetchWeather(city, unit = 'metric') {
  const params = new URLSearchParams({ city: city.trim(), units: unit });
  const response = await fetch(`/api/weather?${params}`);

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || `Request failed (${response.status})`);
  }

  return response.json();
}

// ── Update the DOM with weather data ──────────────────────────
function renderWeather(data, unit) {
  const unitLabel    = unit === 'metric' ? '°C' : '°F';
  const windUnitLabel = unit === 'metric' ? 'm/s' : 'mph';

  cityName.textContent  = data.city;
  condition.textContent = data.condition;
  temperature.textContent = `${data.temperature} ${unitLabel}`;
  humidity.textContent    = `${data.humidity}%`;
  windSpeed.textContent   = `${data.wind_speed} ${windUnitLabel}`;

  icon.src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
  icon.alt = data.condition;

  resultCard.hidden = false;
}

// ── Show / hide helpers ───────────────────────────────────────
function showError(message) {
  errorMsg.textContent = message;
  errorMsg.hidden = false;
  resultCard.hidden = true;
}

function clearError() {
  errorMsg.hidden = true;
  errorMsg.textContent = '';
}

function setLoading(active) {
  loading.hidden = !active;
  if (active) resultCard.hidden = true;
}

// ── Main search handler ───────────────────────────────────────
async function handleSearch(city, unit) {
  clearError();
  setLoading(true);

  try {
    const data = await fetchWeather(city, unit);
    renderWeather(data, unit);
  } catch (err) {
    showError(err.message || 'Could not retrieve weather data. Please try again.');
  } finally {
    setLoading(false);
  }
}

// ── Form submit ───────────────────────────────────────────────
form.addEventListener('submit', (e) => {
  e.preventDefault();
  const city = cityInput.value.trim();

  if (!city) {
    showError('Please enter a city name.');
    return;
  }

  lastCity = city;
  lastUnit = document.querySelector('input[name="unit"]:checked').value;
  handleSearch(lastCity, lastUnit);
});

// ── Unit toggle — re-fetch with new unit ──────────────────────
unitRadios.forEach((radio) => {
  radio.addEventListener('change', () => {
    if (!lastCity) return;
    lastUnit = radio.value;
    handleSearch(lastCity, lastUnit);
  });
});
