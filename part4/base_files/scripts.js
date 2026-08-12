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
});

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}