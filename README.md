# LiarsHandshake
A side project to create a web game where users can play a head to head social deduction game using their Destiny stats.

Useful Information:

* Currently working primarily on server backend using Python and Websockets
* Destiny API is communicated with through Python requests, the API key is stored on my local copy,
  so a pull of this repo will be non-functional unless you obtain your own key and assign it to the
  API_KEY constant
* Client is communicated with using Websockets and 16 character UUIDs
* Lobby IDs are generated with the [Wonder Words random word library](https://pypi.org/project/wonderwords/) then filtered
  for the small chance of producing inappropriate IDs using [profanity-filter](https://pypi.org/project/profanity-filter/)
* Database storage uses SQLite 3
  
