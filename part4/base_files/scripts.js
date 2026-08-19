/* HBnB web client: authentication, the place list, place details and reviews.
   Every page loads this one file; each section is guarded by an element that
   only exists on the page it belongs to. */

// On the academy sandbox the pages are served from a proxy host such as
// "web-8000-142-110.cod-eu-west-3.hbtn.io", where "localhost" would resolve to
// the browser's own machine rather than the server. Rewriting the port segment
// keeps the request on that host. Plain localhost testing is unaffected.
const API_BASE_URL = window.location.hostname.includes('.hbtn.io')
  ? `${window.location.protocol}//${window.location.hostname.replace(/^web-\d+-/, 'web-5000-')}/api/v1`
  : 'http://localhost:5000/api/v1';

const TOKEN_COOKIE = 'access_token';

document.addEventListener('DOMContentLoaded', () => {
  setupSessionLink();
  setupLoginForm();

  if (document.getElementById('places-list')) {
    initIndexPage();
  }
  if (document.getElementById('place-details')) {
    initPlacePage();
  }
  if (document.getElementById('review-form')) {
    initReviewPage();
  }
});

/* --- Session ------------------------------------------------------------- */

function getCookie (name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

function setToken (token) {
  document.cookie = `${TOKEN_COOKIE}=${token}; path=/`;
}

function clearToken () {
  document.cookie = `${TOKEN_COOKIE}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function getToken () {
  return getCookie(TOKEN_COOKIE);
}

function authHeaders (token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// A token that has expired still sits in the cookie, so the interface would go
// on looking signed in while every request fails. Dropping it here keeps what
// the page shows and what the API accepts in step.
function handleExpiredSession (response) {
  if (response.status !== 401) return false;
  clearToken();
  return true;
}

function setupSessionLink () {
  const loginLink = document.getElementById('login-link');
  if (!loginLink || !getToken()) return;

  loginLink.textContent = 'Log out';
  loginLink.href = '#';
  loginLink.addEventListener('click', (event) => {
    event.preventDefault();
    clearToken();
    window.location.href = 'index.html';
  });
}

/* --- Login --------------------------------------------------------------- */

function setupLoginForm () {
  const loginForm = document.getElementById('login-form');
  const loginError = document.getElementById('login-error');
  if (!loginForm) return;

  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();

      if (response.ok) {
        setToken(data.access_token);
        window.location.href = 'index.html';
      } else {
        showMessage(loginError, data.error || 'Login failed. Please try again.');
      }
    } catch (error) {
      showMessage(loginError, 'Unable to reach the server. Please try again.');
    }
  });
}

function showMessage (element, text) {
  if (!element) return;
  element.textContent = text;
  element.hidden = false;
}

/* --- Place list and price filter ----------------------------------------- */

async function initIndexPage () {
  const priceFilter = document.getElementById('price-filter');
  if (priceFilter) {
    priceFilter.addEventListener('change', applyPriceFilter);
  }

  const places = await loadPlaces();
  if (places) drawAtlas(places);
}

// The list and the atlas show the same catalogue, so it is requested once and
// handed to both.
async function loadPlaces () {
  try {
    const response = await fetch(`${API_BASE_URL}/places/`, {
      headers: authHeaders(getToken())
    });
    if (!response.ok) throw new Error(`Places request failed: ${response.status}`);

    const places = await response.json();
    displayPlaces(places);
    return places;
  } catch (error) {
    // The markup ships with sample cards so the page is never blank while it
    // loads. They would mislead once the request has failed, because their
    // links point at places this API does not have.
    const placesList = document.getElementById('places-list');
    if (placesList) placesList.innerHTML = '';

    const resultCount = document.getElementById('result-count');
    if (resultCount) {
      resultCount.textContent = 'Could not load stays. Is the API running?';
    }

    const status = document.getElementById('map-status');
    if (status) status.textContent = 'The atlas is unavailable right now.';
    return null;
  }
}

function displayPlaces (places) {
  const placesList = document.getElementById('places-list');
  if (!placesList) return;

  placesList.innerHTML = '';

  places.forEach((place) => {
    const card = document.createElement('li');
    card.className = 'place-card';
    card.dataset.price = place.price;

    const priceStamp = document.createElement('span');
    priceStamp.className = 'price-stamp';
    priceStamp.append(`SAR ${place.price}`, document.createElement('br'), '/night');
    card.appendChild(priceStamp);

    if (place.image_url) {
      card.appendChild(buildPlacePhoto(place));
    }

    const title = document.createElement('h2');
    title.textContent = place.title;

    const location = document.createElement('p');
    location.className = 'location';
    location.textContent = place.location || place.description;

    const detailsLink = document.createElement('a');
    detailsLink.className = 'details-button';
    detailsLink.href = `place.html?id=${encodeURIComponent(place.id)}`;
    detailsLink.textContent = 'View details';

    card.append(title, location, detailsLink);
    placesList.appendChild(card);
  });

  // The dropdown keeps its value across a reload, and the visitor may change
  // it while this request is still in flight, so re-apply it to the new cards.
  applyPriceFilter();

  // Re-run the decorative tilt and reveal effects, which ran once on load and
  // so never saw these cards. Both are no-ops if atlas.js is absent.
  if (window.__hbnbTilt) window.__hbnbTilt();
  if (window.__hbnbReveal) window.__hbnbReveal();
}

function buildPlacePhoto (place) {
  const photo = document.createElement('div');
  photo.className = 'place-photo';

  const img = document.createElement('img');
  img.src = place.image_url;
  img.alt = place.title;
  img.loading = 'lazy';
  photo.appendChild(img);

  if (place.location) {
    const tag = document.createElement('span');
    tag.textContent = place.location;
    photo.appendChild(tag);
  }
  return photo;
}

function applyPriceFilter () {
  const priceFilter = document.getElementById('price-filter');
  const maxPrice = priceFilter ? priceFilter.value : 'all';
  const cards = document.querySelectorAll('#places-list .place-card');
  let visible = 0;

  cards.forEach((card) => {
    const show = maxPrice === 'all' || Number(card.dataset.price) <= Number(maxPrice);
    card.style.display = show ? '' : 'none';
    if (show) visible += 1;
  });

  updateResultCount(visible, cards.length);
  if (window.__hbnbMapFilter) window.__hbnbMapFilter(visibleCardTitles());
}

function visibleCardTitles () {
  return Array.from(document.querySelectorAll('#places-list .place-card'))
    .filter((card) => card.style.display !== 'none')
    .map((card) => card.querySelector('h2').textContent);
}

function updateResultCount (visible, total) {
  const resultCount = document.getElementById('result-count');
  if (!resultCount) return;

  if (total === 0) {
    resultCount.textContent = 'No stays published yet.';
  } else if (visible === total) {
    resultCount.textContent = `${total} stay${total === 1 ? '' : 's'} available.`;
  } else {
    resultCount.textContent = `${visible} of ${total} stays match this price.`;
  }
}

/* --- Place details ------------------------------------------------------- */

function getPlaceIdFromURL () {
  return new URLSearchParams(window.location.search).get('id');
}

async function initPlacePage () {
  const placeId = getPlaceIdFromURL();
  const token = getToken();

  // The button is present in the markup so the page reads correctly without
  // scripting; it is hidden again here for anyone who is not signed in.
  const addReviewCta = document.getElementById('add-review-cta');
  if (addReviewCta) addReviewCta.hidden = !token;

  if (!placeId) {
    showPlaceNotFound('No place was requested.');
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/places/${placeId}`, {
      headers: authHeaders(token)
    });
    if (!response.ok) {
      showPlaceNotFound('This place could not be found.');
      return;
    }

    const place = await response.json();
    renderPlaceDetails(place);
    renderReviews(place.reviews || []);

    const addReviewLink = document.querySelector('#add-review-cta a');
    if (addReviewLink) {
      addReviewLink.href = `add_review.html?id=${encodeURIComponent(placeId)}`;
    }
  } catch (error) {
    showPlaceNotFound('Could not load this place. Is the API running?');
  }
}

// Without this the sample place written into the markup would stay on screen
// and read as though it were the place that was actually requested.
function showPlaceNotFound (message) {
  const details = document.getElementById('place-details');
  if (details) {
    details.innerHTML = '';
    const heading = document.createElement('h1');
    heading.textContent = message;
    const back = document.createElement('a');
    back.className = 'details-button';
    back.href = 'index.html';
    back.textContent = 'Back to all stays';
    details.append(heading, back);
  }

  const reviews = document.getElementById('reviews');
  if (reviews) reviews.hidden = true;

  const addReviewCta = document.getElementById('add-review-cta');
  if (addReviewCta) addReviewCta.hidden = true;
}

function renderPlaceDetails (place) {
  document.title = `HBnB - ${place.title}`;

  setText('.place-main .eyebrow', place.location || '');
  setText('.place-main h1', place.title);
  setText('#place-description', place.description || '');
  setText('#place-location', place.location || 'Not specified');
  setText('.breadcrumb [aria-current="page"]', place.title);
  setText('#place-coordinates', formatCoordinates(place));
  setText('#place-figcaption', place.location || '');

  const priceTag = document.querySelector('.price-tag');
  if (priceTag) {
    priceTag.textContent = `SAR ${place.price} `;
    const perNight = document.createElement('small');
    perNight.textContent = '/ night';
    priceTag.appendChild(perNight);
  }

  const figureImg = document.querySelector('.place-figure img');
  if (figureImg && place.image_url) {
    figureImg.src = place.image_url;
    figureImg.alt = place.title;
  }

  if (place.owner) {
    setText('#host-name', `Hosted by ${place.owner.first_name}`);
    setText('.host-avatar', place.owner.first_name.charAt(0));
  }

  renderAmenities(place.amenities || []);
}

function renderAmenities (amenities) {
  const list = document.querySelector('.amenities-list');
  if (!list) return;

  list.innerHTML = '';
  if (!amenities.length) {
    const item = document.createElement('li');
    item.textContent = 'None listed';
    list.appendChild(item);
    return;
  }

  amenities.forEach((amenity) => {
    const item = document.createElement('li');
    item.textContent = amenity.name;
    list.appendChild(item);
  });
}

function formatCoordinates (place) {
  if (typeof place.latitude !== 'number' || typeof place.longitude !== 'number') {
    return 'Not specified';
  }
  return `${place.latitude.toFixed(4)}° N, ${place.longitude.toFixed(4)}° E`;
}

function setText (selector, text) {
  const element = selector.startsWith('#') && !selector.includes(' ')
    ? document.getElementById(selector.slice(1))
    : document.querySelector(selector);
  if (element) element.textContent = text;
}

function renderReviews (reviews) {
  const list = document.querySelector('.reviews-list');
  const summary = document.getElementById('reviews-summary');
  if (!list) return;

  list.innerHTML = '';

  if (summary) {
    summary.textContent = reviews.length
      ? `${reviews.length} guest${reviews.length === 1 ? '' : 's'} shared what stood out.`
      : 'No reviews yet - be the first to share.';
  }

  reviews.forEach((review) => {
    const card = document.createElement('li');
    card.className = 'review-card';

    const head = document.createElement('div');
    head.className = 'review-head';

    const reviewer = document.createElement('span');
    reviewer.className = 'reviewer';
    // The API nests the author's name in the place response. Looking it up
    // through /users/<id> instead would need a token, so signed-out visitors
    // would see every review credited to nobody.
    reviewer.textContent = review.author || 'Guest';

    const rating = document.createElement('span');
    rating.className = 'rating';
    rating.textContent = formatRating(review.rating);

    head.append(reviewer, rating);

    const text = document.createElement('p');
    text.textContent = review.text;

    card.append(head, text);
    list.appendChild(card);
  });
}

function formatRating (rating) {
  const score = Number(rating) || 0;
  return `${'★'.repeat(score)}${'☆'.repeat(5 - score)} ${score}/5`;
}

/* --- Review form --------------------------------------------------------- */

async function initReviewPage () {
  const token = getToken();
  if (!token) {
    window.location.href = 'index.html';
    return;
  }

  const reviewForm = document.getElementById('review-form');
  const reviewError = document.getElementById('review-error');
  const reviewGate = document.getElementById('review-gate');
  const placeId = getPlaceIdFromURL();

  initStarPicker();
  initCharacterCount();

  if (!placeId) {
    showMessage(reviewGate, 'No place was specified. Go back and pick a place first.');
    if (reviewForm) reviewForm.hidden = true;
    return;
  }

  await showReviewContext(placeId, token);

  if (!reviewForm) return;
  reviewForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (reviewError) reviewError.hidden = true;

    const rating = document.getElementById('rating').value;
    const comment = document.getElementById('comment').value.trim();

    if (!rating || !comment) {
      showMessage(reviewError, 'Choose a rating and write a comment first.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/reviews/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders(token)
        },
        body: JSON.stringify({
          place_id: placeId,
          rating: Number(rating),
          text: comment
        })
      });

      if (response.ok) {
        onReviewAccepted(reviewForm, placeId);
        return;
      }

      if (handleExpiredSession(response)) {
        showMessage(reviewError, 'Your session expired. Please sign in again.');
        return;
      }

      const data = await response.json();
      showMessage(reviewError, data.message || data.error || 'Could not submit the review.');
    } catch (error) {
      showMessage(reviewError, 'Unable to reach the server. Please try again.');
    }
  });
}

function onReviewAccepted (reviewForm, placeId) {
  reviewForm.reset();
  resetStarPicker();

  const success = document.getElementById('review-success');
  showMessage(success, 'Review submitted. Taking you back to the place…');

  // The confirmation sits beside the button, at the foot of a long form, so it
  // is scrolled into view rather than left off-screen.
  if (success) success.scrollIntoView({ block: 'center', behavior: 'smooth' });

  // Long enough to read the confirmation before the place page replaces it,
  // where the new review appears among the others.
  window.setTimeout(() => {
    window.location.href = `place.html?id=${encodeURIComponent(placeId)}`;
  }, 2200);
}

async function showReviewContext (placeId, token) {
  try {
    const response = await fetch(`${API_BASE_URL}/places/${placeId}`, {
      headers: authHeaders(token)
    });
    if (!response.ok) return;

    const place = await response.json();
    setText('#ctx-place-name', place.title);
    setText('#ctx-loc', place.location || '');

    const cover = document.getElementById('review-cover');
    if (cover && place.image_url) {
      cover.src = place.image_url;
      cover.alt = place.title;
    }

    document.querySelectorAll('#ctx-back, #ctx-crumb').forEach((link) => {
      link.href = `place.html?id=${encodeURIComponent(placeId)}`;
    });
  } catch (error) {
    // Context is decorative; the form still works without it.
  }
}

function initCharacterCount () {
  const comment = document.getElementById('comment');
  const counter = document.getElementById('character-count');
  if (!comment || !counter) return;

  comment.addEventListener('input', () => {
    counter.textContent = `${comment.value.length} / 1200`;
  });
}

/* The rating is a group of buttons rather than a <select>, so the chosen value
   is mirrored into a hidden input and announced through aria-checked. */
function initStarPicker () {
  const picker = document.getElementById('star-picker');
  const ratingInput = document.getElementById('rating');
  if (!picker || !ratingInput) return;

  const buttons = Array.from(picker.querySelectorAll('.star-btn'));

  function select (value) {
    ratingInput.value = value ? String(value) : '';
    buttons.forEach((button) => {
      const starValue = Number(button.dataset.value);
      button.textContent = starValue <= value ? '★' : '☆';
      button.setAttribute('aria-checked', starValue === value ? 'true' : 'false');
      // Only the chosen star stays in the tab order, so the group is a single
      // stop and the arrow keys move within it, as a radio group behaves.
      button.tabIndex = starValue === (value || 1) ? 0 : -1;
    });
  }

  buttons.forEach((button, index) => {
    button.addEventListener('click', () => select(Number(button.dataset.value)));
    button.addEventListener('keydown', (event) => {
      const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[event.key];
      if (!step) return;
      event.preventDefault();
      const next = buttons[(index + step + buttons.length) % buttons.length];
      select(Number(next.dataset.value));
      next.focus();
    });
  });

  picker.__reset = () => select(0);
  select(0);
}

function resetStarPicker () {
  const picker = document.getElementById('star-picker');
  if (picker && picker.__reset) picker.__reset();
}

/* --- Decorative atlas ---------------------------------------------------- */

/* The map plots the same places the list below shows, so a pin leads to that
   place's real detail page. Only the regional colours and motifs come from the
   local file, and an unrecognised title simply falls back to a generic one. */
async function drawAtlas (places) {
  if (!document.getElementById('atlas-svg') || !window.__hbnbMap) return;

  let regions = {};
  try {
    const response = await fetch('data/regions.json');
    if (response.ok) regions = (await response.json()).regions || {};
  } catch (error) {
    // Motifs are decoration; the atlas still draws without them.
  }

  window.__hbnbMap(places.map((place) => ({
    id: place.id,
    name: place.title,
    location: place.location || '',
    price: place.price,
    coordinates: { lat: place.latitude, lng: place.longitude },
    heritage: regions[place.title] || null
  })));
}
