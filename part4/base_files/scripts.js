const API_BASE_URL = 'http://localhost:5000/api/v1';

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