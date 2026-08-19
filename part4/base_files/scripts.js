// On the academy sandbox, the page is served from a proxy domain like
// "web-8000-142-110.cod-eu-west-3.hbtn.io" -- in that case "localhost"
// would wrongly point back at the student's own laptop, so we rewrite the
// port segment of that same hostname to reach the Flask backend instead.
// Outside the sandbox (plain localhost testing) nothing changes.
const API_BASE_URL = window.location.hostname.includes('.hbtn.io')
  ? `${window.location.protocol}//${window.location.hostname.replace(/^web-\d+-/, 'web-5000-')}/api/v1`
  : 'http://localhost:5000/api/v1';

document.addEventListener('DOMContentLoaded', () => {
  const isLoggedIn = getCookie('access_token') !== null;

  /* The "Add a review" button is visible in the HTML by default. Here we
     hide it again for signed-out visitors, so it only shows once the user
     has actually logged in (per the "only visible if logged in" spec). */
  const addReviewCta = document.getElementById('add-review-cta');
  if (addReviewCta) {
    addReviewCta.hidden = !isLoggedIn;
  }

  const loginLink = document.getElementById('login-link');
  if (loginLink && isLoggedIn) {
    loginLink.textContent = 'Log out';
    loginLink.href = '#';
    loginLink.addEventListener('click', (event) => {
      event.preventDefault();
      document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      window.location.href = 'index.html';
    });
  }

  const loginForm = document.getElementById('login-form');
  const loginError = document.getElementById('login-error');

  function showLoginError (message) {
    if (!loginError) return;
    loginError.textContent = message;
    loginError.hidden = false;
  }

  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;

      try {
        const response = await loginUser(email, password);
        const data = await response.json();

        if (response.ok) {
          document.cookie = `access_token=${data.access_token}; path=/`;
          window.location.href = 'index.html';
        } else {
          showLoginError(data.error || 'Login failed. Please try again.');
        }
      } catch (error) {
        showLoginError('Unable to reach the server. Please try again.');
      }
    });
  }

  const placesList = document.getElementById('places-list');
  if (placesList) {
    fetchPlaces(getCookie('access_token'));
  }

  const priceFilter = document.getElementById('price-filter');
  if (priceFilter) {
    priceFilter.addEventListener('change', (event) => {
      const maxPrice = event.target.value;

      document.querySelectorAll('#places-list .place-card').forEach((card) => {
        const price = Number(card.dataset.price);
        const show = maxPrice === 'all' || price <= Number(maxPrice);
        card.style.display = show ? '' : 'none';
      });
    });
  }

  /* Task 3: place.html only has #place-details when we're actually on
     that page, so this block is a no-op everywhere else. */
  if (document.getElementById('place-details')) {
    initPlacePage();
  }

  /* Task 4: same guard pattern, keyed off the review form's id. */
  if (document.getElementById('review-form')) {
    initReviewPage();
  }
});

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

async function loginUser (email, password) {
  return fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
}

async function fetchPlaces (token) {
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/places/`, { headers });
  if (response.ok) {
    displayPlaces(await response.json());
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
      card.appendChild(photo);
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

  /* Decorative-only: re-apply the redesign's tilt/scroll-reveal motion to
     the cards we just injected (they run once on DOMContentLoaded, before
     these cards exist). Safe no-ops if atlas.js isn't loaded. */
  if (window.__hbnbTilt) window.__hbnbTilt();
  if (window.__hbnbReveal) window.__hbnbReveal();
}

/* Decorative Saudi atlas map (index hero): a fixed illustrative scenario,
   independent of the real place catalog above. Not wired to the backend --
   see atlas.js for the rendering itself. */
if (document.getElementById('atlas-svg')) {
  fetch('data/places.json')
    .then((response) => response.json())
    .then((db) => {
      if (window.__hbnbMap) window.__hbnbMap(db.places);
    })
    .catch(() => {});
}

/* ---------- Task 3: place details, Task 4: add review ---------- */

function getPlaceIdFromURL () {
  return new URLSearchParams(window.location.search).get('id');
}

async function fetchPlace (id, token) {
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return fetch(`${API_BASE_URL}/places/${id}`, { headers });
}

async function fetchUser (id, token) {
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return fetch(`${API_BASE_URL}/users/${id}`, { headers });
}

async function submitReview (token, placeId, rating, text) {
  return fetch(`${API_BASE_URL}/reviews/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ place_id: placeId, rating: Number(rating), text })
  });
}

async function initPlacePage () {
  const placeId = getPlaceIdFromURL();
  if (!placeId) return;

  const token = getCookie('access_token');
  const response = await fetchPlace(placeId, token);
  if (!response.ok) return;

  const place = await response.json();
  renderPlaceDetails(place);
  renderReviews(place.reviews || [], token);

  const addReviewLink = document.querySelector('#add-review-cta a');
  if (addReviewLink) {
    addReviewLink.href = `add_review.html?id=${encodeURIComponent(placeId)}`;
  }
}

function renderPlaceDetails (place) {
  const eyebrow = document.querySelector('.place-main .eyebrow');
  if (eyebrow) eyebrow.textContent = place.location || '';

  const heading = document.querySelector('.place-main h1');
  if (heading) heading.textContent = place.title;

  const figureImg = document.querySelector('.place-figure img');
  if (figureImg && place.image_url) {
    figureImg.src = place.image_url;
    figureImg.alt = place.title;
  }

  const description = document.getElementById('place-description');
  if (description) description.textContent = place.description || '';

  const priceTag = document.querySelector('.price-tag');
  if (priceTag) priceTag.innerHTML = `SAR ${place.price} <small>/ night</small>`;

  if (place.owner) {
    const hostName = document.getElementById('host-name');
    const hostAvatar = document.querySelector('.host-avatar');
    if (hostName) hostName.textContent = `Hosted by ${place.owner.first_name}`;
    if (hostAvatar) hostAvatar.textContent = place.owner.first_name.charAt(0);
  }

  const amenitiesList = document.querySelector('.amenities-list');
  if (amenitiesList) {
    amenitiesList.innerHTML = '';
    (place.amenities || []).forEach((amenity) => {
      const item = document.createElement('li');
      item.textContent = amenity.name;
      amenitiesList.appendChild(item);
    });
  }

  const crumb = document.querySelector('.breadcrumb [aria-current="page"]');
  if (crumb) crumb.textContent = place.title;
}

function renderReviews (reviews, token) {
  const list = document.querySelector('.reviews-list');
  const summary = document.getElementById('reviews-summary');
  if (!list) return;

  list.innerHTML = '';

  if (summary) {
    summary.textContent = reviews.length
      ? `${reviews.length} guest${reviews.length === 1 ? '' : 's'} shared what stood out.`
      : 'No reviews yet -- be the first to share.';
  }

  reviews.forEach((review) => {
    const card = document.createElement('li');
    card.className = 'review-card';

    const head = document.createElement('div');
    head.className = 'review-head';

    const reviewer = document.createElement('span');
    reviewer.className = 'reviewer';
    reviewer.textContent = 'Guest';

    const rating = document.createElement('span');
    rating.className = 'rating';
    rating.textContent = `${'\u2605'.repeat(review.rating)}${'\u2606'.repeat(5 - review.rating)} ${review.rating}/5`;

    head.append(reviewer, rating);

    const text = document.createElement('p');
    text.textContent = review.text;

    card.append(head, text);
    list.appendChild(card);

    fetchUser(review.user_id, token).then((userResponse) => {
      if (!userResponse.ok) return;
      return userResponse.json();
    }).then((user) => {
      if (user) reviewer.textContent = `${user.first_name} ${user.last_name.charAt(0)}.`;
    });
  });
}

async function initReviewPage () {
  initStarPicker();
  const token = getCookie('access_token');
  const reviewForm = document.getElementById('review-form');
  const reviewError = document.getElementById('review-error');
  const reviewGate = document.getElementById('review-gate');

  if (!token) {
    window.location.href = 'index.html';
    return;
  }

  const placeId = getPlaceIdFromURL();
  if (!placeId) {
    if (reviewGate) {
      reviewGate.textContent = 'No place was specified. Go back and pick a place first.';
      reviewGate.hidden = false;
    }
    if ( reviewForm) reviewForm.hidden = true;
    return;
  }

  const placeResponse = await fetchPlace(placeId, token);
  if (placeResponse.ok) {
    const place = await placeResponse.json();

    const nameEl = document.getElementById('ctx-place-name');
    if (nameEl) nameEl.textContent = place.title;

    const locEl = document.getElementById('ctx-loc');
    if (locEl) locEl.textContent = place.location || '';

    const coverImg = document.getElementById('review-cover');
    if (coverImg && place.image_url) {
      coverImg.src = place.image_url;
      coverImg.alt = place.title;
    }

    document.querySelectorAll('#ctx-back, #header-place-link, #footer-place-link')
      .forEach((link) => { link.href = `place.html?id=${encodeURIComponent(placeId)}`; });
  }

  const commentField = document.getElementById('comment');
  const charCount = document.getElementById('character-count');
  if (commentField && charCount) {
    commentField.addEventListener('input', () => {
      charCount.textContent = `${commentField.value.length} / 1200`;
    });
  }

  if (reviewForm) {
    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (reviewError) reviewError.hidden = true;

      const ratingField = document.getElementById('rating');
      const rating = ratingField ? ratingField.value : '';
      const comment = commentField ? commentField.value.trim() : '';

      if (!rating || !comment) {
        if (reviewError) {
          reviewError.textContent = 'Choose a rating and write a comment first.';
          reviewError.hidden = false;
        }
        return;
      }

      try {
        const response = await submitReview(token, placeId, rating, comment);
        const data = await response.json();

        if (response.ok) {
          window.location.href = `place.html?id=${encodeURIComponent(placeId)}`;
        } else if (reviewError) {
          reviewError.textContent = data.message || data.error || 'Could not submit the review.';
          reviewError.hidden = false;
        }
      } catch (error) {
        if (reviewError) {
          reviewError.textContent = 'Unable to reach the server. Please try again.';
          reviewError.hidden = false;
        }
      }
    });
  }
}

function initStarPicker () {
  const picker = document.getElementById('star-picker');
  const ratingInput = document.getElementById('rating');
  if (!picker || !ratingInput) return;
  const buttons = Array.from(picker.querySelectorAll('.star-btn'));
  function paint (value) {
    buttons.forEach((btn) => {
      const active = Number(btn.dataset.value) <= value;
      btn.textContent = active ? '\u2605' : '\u2606';
    });
  }
  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      ratingInput.value = btn.dataset.value;
      paint(Number(btn.dataset.value));
    });
  });
  paint(0);
}
