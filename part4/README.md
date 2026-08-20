# HBnB — Part 4: Simple Web Client

A browser client for the HBnB API, written in HTML5, CSS3 and JavaScript ES6 with
no frameworks and no build step. The API from Part 3 is included here so the two
halves can be run together.

The client covers four pages: a list of places, a place's details, a login form,
and a form for adding a review.

## Layout

```
part4/
├── base_files/            # the web client
│   ├── index.html         # list of places, price filter, decorative atlas
│   ├── place.html         # one place: details, amenities, reviews
│   ├── login.html         # login form
│   ├── add_review.html    # review form, signed-in visitors only
│   ├── scripts.js         # all client behaviour
│   ├── atlas.js           # the SVG atlas and the motion effects
│   ├── styles.css         # every style rule
│   ├── data/regions.json  # decorative regional motifs for the atlas
│   ├── fonts/             # self-hosted fonts, so no external requests
│   └── images/
├── app/                   # the Flask API
│   ├── api/v1/            # endpoints: users, places, reviews, amenities, auth
│   ├── models/            # User, Place, Review, Amenity
│   ├── persistence/       # SQLAlchemy repository
│   └── services/          # HBnBFacade
├── sql/                   # schema, seed data and a raw CRUD demonstration
├── tests/                 # unit tests
├── config.py
└── run.py
```

## Running it

Two servers are needed: one for the API, one for the static files. The client
expects the API on port 5000.

```bash
pip install -r requirements.txt
python run.py
```

Then, in a second terminal:

```bash
cd base_files && python -m http.server 8000
```

Open <http://localhost:8000/index.html>.

A new database starts with one administrator account, `admin@hbnb.io` /
`admin1234`, because creating a user requires an administrator token and there
would otherwise be no way to sign in at all. The catalogue starts empty; places
and amenities are added through the API.

## How the client works

**Session.** Logging in posts to `/api/v1/auth/login` and stores the returned
JWT in a cookie. Every later request sends it as a `Bearer` token. Reading the
catalogue is public, so signed-out visitors still see every place and review.

**List of places.** `index.html` fetches `/api/v1/places/` and builds one card
per place. The price filter hides cards in the browser without another request,
and the atlas beside the list dims the same places the filter hides.

**Place details.** `place.html` reads the place id from the query string and
fetches that place, including its owner, amenities and reviews. The link to the
review form appears only when a visitor is signed in.

**Adding a review.** `add_review.html` redirects anyone without a token back to
the index, then posts the rating and comment to `/api/v1/reviews/`.

The API sets permissive CORS headers, since the client is served from a
different origin than the API.

## Design notes

Cards use the margin, padding, border and radius the project specifies; colours
and fonts were chosen freely. Fonts are stored in `base_files/fonts/`, so the
pages make no external requests. All four pages pass the W3C validator with no
errors, and every text colour meets the WCAG AA contrast ratio.

The atlas on the index page is decorative. It plots the real places from the
API, so a pin leads to that place's own page; only the regional colours and
motifs come from `data/regions.json`.

## Tests

```bash
python -m unittest discover -s tests
```

The suite builds its own application against an in-memory database, so running
it never touches `instance/development.db`.
