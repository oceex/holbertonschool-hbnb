/*
  hbnb — front-end logic (no backend: everything below is mock data
  and a cookie-based demo "session" so the four pages behave like a
  real app would).
*/

/* ----------------------------------------------------------------
   Mock data
   ---------------------------------------------------------------- */
const PLACES = [
  {
    id: 1,
    name: 'Sunlit Loft in the Old Quarter',
    city: 'Riyadh, Saudi Arabia',
    host: 'Mariam A.',
    price: 45,
    description:
      'A bright, airy loft tucked above a quiet courtyard in the old quarter. Exposed stone walls, tall shuttered windows, and a rooftop terrace perfect for evening tea.',
    amenities: [
      { name: 'Wifi', icon: 'images/icon_wifi.png' },
      { name: '1 Bed', icon: 'images/icon_bed.png' },
      { name: 'Private bath', icon: 'images/icon_bath.png' },
    ],
    reviews: [
      { user: 'Ahmed K.', comment: 'Quiet, spotless, and the terrace view at sunset was unbeatable.', rating: 5 },
      { user: 'Lina S.', comment: 'Great location, a short walk from everything. Would stay again.', rating: 4 },
    ],
  },
  {
    id: 2,
    name: 'Desert-View Studio',
    city: 'AlUla, Saudi Arabia',
    host: 'Faisal N.',
    price: 25,
    description:
      'A compact studio with floor-to-ceiling windows facing the sandstone cliffs. Simple, comfortable, and five minutes from the old town trailhead.',
    amenities: [
      { name: 'Wifi', icon: 'images/icon_wifi.png' },
      { name: '1 Bed', icon: 'images/icon_bed.png' },
      { name: 'Shared bath', icon: 'images/icon_bath.png' },
    ],
    reviews: [
      { user: 'Grace O.', comment: 'Waking up to that view every morning was worth the trip alone.', rating: 5 },
    ],
  },
  {
    id: 3,
    name: 'Marina Apartment with Balcony',
    city: 'Jeddah, Saudi Arabia',
    host: 'Huda M.',
    price: 60,
    description:
      'Modern two-room apartment two blocks from the Corniche. Sea breeze on the balcony, a proper kitchen, and fast wifi for remote work days.',
    amenities: [
      { name: 'Wifi', icon: 'images/icon_wifi.png' },
      { name: '2 Beds', icon: 'images/icon_bed.png' },
      { name: 'Private bath', icon: 'images/icon_bath.png' },
    ],
    reviews: [
      { user: 'Omar T.', comment: 'Spacious, clean, and the host checked in without being intrusive.', rating: 5 },
      { user: 'Sara Y.', comment: 'Balcony views of the water were lovely, wifi was fast and stable.', rating: 4 },
      { user: 'Peter D.', comment: 'Good value. Street noise carried a bit at night.', rating: 3 },
    ],
  },
  {
    id: 4,
    name: 'Riad Courtyard Room',
    city: 'Marrakech, Morocco',
    host: 'Yasmine B.',
    price: 38,
    description:
      'A single room inside a family-run riad, opening onto an orange-tree courtyard. Breakfast included, and the medina is right outside the door.',
    amenities: [
      { name: 'Wifi', icon: 'images/icon_wifi.png' },
      { name: '1 Bed', icon: 'images/icon_bed.png' },
      { name: 'Shared bath', icon: 'images/icon_bath.png' },
    ],
    reviews: [
      { user: 'Noah F.', comment: 'Felt like staying with old friends. Breakfast was a highlight every day.', rating: 5 },
    ],
  },
  {
    id: 5,
    name: 'Bosphorus-Facing Flat',
    city: 'Istanbul, Türkiye',
    host: 'Deniz K.',
    price: 85,
    description:
      'A one-bedroom flat with a full water view, five minutes from the ferry terminal. Renovated kitchen, quiet building, easy access to both sides of the city.',
    amenities: [
      { name: 'Wifi', icon: 'images/icon_wifi.png' },
      { name: '1 Bed', icon: 'images/icon_bed.png' },
      { name: 'Private bath', icon: 'images/icon_bath.png' },
    ],
    reviews: [
      { user: 'Elif R.', comment: 'The ferry views from the living room are hard to beat.', rating: 5 },
      { user: 'Marco V.', comment: 'Comfortable stay, host was quick to respond to every question.', rating: 5 },
    ],
  },
  {
    id: 6,
    name: 'Downtown Design Suite',
    city: 'Dubai, UAE',
    host: 'Aisha R.',
    price: 120,
    description:
      'A sleek two-bedroom suite in a design district high-rise, with skyline views and a shared rooftop pool. Steps from galleries, cafes, and the metro.',
    amenities: [
      { name: 'Wifi', icon: 'images/icon_wifi.png' },
      { name: '2 Beds', icon: 'images/icon_bed.png' },
      { name: 'Private bath', icon: 'images/icon_bath.png' },
    ],
    reviews: [
      { user: 'Tariq H.', comment: 'Pool and skyline view made this feel like a proper getaway.', rating: 5 },
      { user: 'Nadia C.', comment: 'Beautifully designed space, though check-in took a while.', rating: 4 },
    ],
  },
];

const PRICE_FILTER_OPTIONS = [10, 50, 100, 'All'];
const RATING_OPTIONS = [5, 4, 3, 2, 1];
const AUTH_COOKIE = 'hbnb_token';

/* ----------------------------------------------------------------
   Cookie helpers (stand in for a real session, since there is no
   backend in this project)
   ---------------------------------------------------------------- */
function setCookie(name, value, days) {
  const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function deleteCookie(name) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`;
}

function isAuthenticated() {
  return Boolean(getCookie(AUTH_COOKIE));
}

/* ----------------------------------------------------------------
   Shared header: swap Login for Logout once "logged in"
   ---------------------------------------------------------------- */
function initAuthLink() {
  const link = document.getElementById('login-link');
  if (!link) return;

  if (isAuthenticated()) {
    link.textContent = 'Logout';
    link.setAttribute('href', '#');
    link.addEventListener('click', (event) => {
      event.preventDefault();
      deleteCookie(AUTH_COOKIE);
      window.location.href = 'index.html';
    });
  } else {
    link.textContent = 'Login';
    link.setAttribute('href', 'login.html');
  }
}

/* ----------------------------------------------------------------
   Index page — list + price filter
   ---------------------------------------------------------------- */
function initIndexPage() {
  const list = document.getElementById('places-list');
  const filter = document.getElementById('price-filter');
  if (!list || !filter) return;

  PRICE_FILTER_OPTIONS.forEach((value) => {
    const option = document.createElement('option');
    option.value = value === 'All' ? 'all' : String(value);
    option.textContent = value === 'All' ? 'All' : `$${value}`;
    filter.appendChild(option);
  });
  filter.value = 'all';

  renderPlaces(list, PLACES);

  filter.addEventListener('change', () => {
    const max = filter.value;
    const filtered = max === 'all' ? PLACES : PLACES.filter((place) => place.price <= Number(max));
    renderPlaces(list, filtered);
  });
}

function renderPlaces(container, places) {
  container.innerHTML = '';

  if (!places.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-state';
    empty.textContent = 'No places match that price yet. Try a higher limit.';
    container.appendChild(empty);
    return;
  }

  places.forEach((place) => {
    const card = document.createElement('article');
    card.className = 'place-card';
    card.innerHTML = `
      <h3>${place.name}</h3>
      <p class="place-card-city">${place.city}</p>
      <p class="price-pill"><span>$${place.price}</span> / night</p>
      <a class="details-button" href="place.html?id=${place.id}">View Details</a>
    `;
    container.appendChild(card);
  });
}

/* ----------------------------------------------------------------
   Place details page
   ---------------------------------------------------------------- */
function getPlaceIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return Number(params.get('id')) || PLACES[0].id;
}

function initPlacePage() {
  const detailsSection = document.getElementById('place-details');
  if (!detailsSection) return;

  const place = PLACES.find((item) => item.id === getPlaceIdFromUrl()) || PLACES[0];

  renderPlaceDetails(detailsSection, place);
  renderReviews(place);
  renderAddReviewSection(place);
}

function renderPlaceDetails(section, place) {
  const amenitiesMarkup = place.amenities
    .map(
      (amenity) => `
        <li>
          <img src="${amenity.icon}" alt="" class="amenity-icon">
          <span>${amenity.name}</span>
        </li>`
    )
    .join('');

  section.innerHTML = `
    <h1>${place.name}</h1>
    <p class="place-location">${place.city}</p>
    <p class="place-card-city host-line">Hosted by ${place.host}</p>
    <p class="price-pill large"><span>$${place.price}</span> / night</p>
    <p class="place-description">${place.description}</p>
    <div class="place-info">
      <h2>What this place offers</h2>
      <ul class="amenities-list">
        ${amenitiesMarkup}
      </ul>
    </div>
  `;
}

function renderReviews(place) {
  const list = document.getElementById('reviews-list');
  if (!list) return;

  if (!place.reviews.length) {
    list.innerHTML = '<p class="empty-state">No reviews yet. Be the first to share your stay.</p>';
    return;
  }

  list.innerHTML = place.reviews
    .map(
      (review) => `
        <article class="review-card">
          <p class="review-comment">${review.comment}</p>
          <p class="review-meta"><span class="review-user">${review.user}</span> · <span class="review-rating">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</span></p>
        </article>`
    )
    .join('');
}

function renderAddReviewSection(place) {
  const section = document.getElementById('add-review');
  if (!section) return;

  if (!isAuthenticated()) {
    section.innerHTML = `
      <p class="login-prompt">Want to leave a review? <a href="login.html" class="login-button">Login</a> first.</p>
    `;
    return;
  }

  section.innerHTML = `
    <form class="add-review form" id="place-review-form">
      <h2>Add a Review</h2>
      <label for="place-review-text">Your Review</label>
      <textarea id="place-review-text" name="review" rows="4" placeholder="Share how your stay went..." required></textarea>

      <label for="place-review-rating">Rating</label>
      <select id="place-review-rating" name="rating" required></select>

      <button type="submit" class="primary-button">Submit</button>
      <p class="or-divider">or <a href="add_review.html?id=${place.id}">open the full-page form</a></p>
    </form>
  `;

  populateRatingOptions(document.getElementById('place-review-rating'));

  document.getElementById('place-review-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const textField = document.getElementById('place-review-text');
    const ratingField = document.getElementById('place-review-rating');

    place.reviews.unshift({
      user: 'You',
      comment: textField.value.trim(),
      rating: Number(ratingField.value),
    });

    renderReviews(place);
    event.target.reset();
  });
}

/* ----------------------------------------------------------------
   Login page
   ---------------------------------------------------------------- */
function initLoginPage() {
  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('login-error');

    if (!email || !password) {
      errorMessage.textContent = 'Enter both an email and a password to continue.';
      errorMessage.hidden = false;
      return;
    }

    // No backend here — a well-formed submission starts the demo session.
    setCookie(AUTH_COOKIE, email, 1);
    window.location.href = 'index.html';
  });
}

/* ----------------------------------------------------------------
   Standalone add-review page
   ---------------------------------------------------------------- */
function initAddReviewPage() {
  const form = document.getElementById('review-form');
  if (!form || document.getElementById('login-form')) return; // guard against index/login false-matches

  if (!isAuthenticated()) {
    window.location.href = 'login.html';
    return;
  }

  const place = PLACES.find((item) => item.id === getPlaceIdFromUrl()) || PLACES[0];
  document.getElementById('reviewing-place').textContent = `Reviewing: ${place.name}`;
  document.getElementById('place-id').value = String(place.id);

  populateRatingOptions(document.getElementById('rating'));

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const reviewText = document.getElementById('review').value.trim();
    const rating = Number(document.getElementById('rating').value);

    place.reviews.unshift({ user: 'You', comment: reviewText, rating });

    const confirmation = document.getElementById('review-confirmation');
    confirmation.textContent = 'Thanks — your review was added.';
    confirmation.hidden = false;
    form.reset();

    setTimeout(() => {
      window.location.href = `place.html?id=${place.id}`;
    }, 900);
  });
}

function populateRatingOptions(select) {
  if (!select) return;
  select.innerHTML = '';
  RATING_OPTIONS.forEach((value) => {
    const option = document.createElement('option');
    option.value = String(value);
    option.textContent = `${value} ${value === 1 ? 'star' : 'stars'}`;
    select.appendChild(option);
  });
}

/* ----------------------------------------------------------------
   Boot
   ---------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  initAuthLink();
  initIndexPage();
  initPlacePage();
  initLoginPage();
  initAddReviewPage();
});