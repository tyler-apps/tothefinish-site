// The finished film starts silently; sound always follows a visitor's action.
const film = document.querySelector('.film-media video');
const play = document.querySelector('.film-play');
const sound = document.querySelector('.film-sound');
if (film && play && sound) {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  film.muted = true;
  play.hidden = false;
  sound.hidden = false;
  const label = () => { sound.textContent = film.muted ? 'Watch with sound' : 'Sound off'; };
  const start = async () => {
    try { await film.play(); } catch { play.hidden = false; }
  };
  const listen = async () => {
    // A visitor hearing it for the first time gets the beginning of the story.
    if (film.muted || film.ended) film.currentTime = 0;
    film.muted = false;
    film.loop = false;
    label();
    await start();
  };
  play.addEventListener('click', listen);
  sound.addEventListener('click', () => {
    if (film.muted || film.ended) void listen();
    else { film.muted = true; label(); }
  });
  film.addEventListener('play', () => { play.hidden = true; });
  film.addEventListener('pause', () => { play.hidden = false; });
  film.addEventListener('ended', () => { play.hidden = false; });
  film.addEventListener('volumechange', () => { if (!film.muted) film.loop = false; label(); });
  reduced.addEventListener('change', () => {
    if (reduced.matches) { film.autoplay = false; film.loop = false; film.pause(); }
  });
  if (!reduced.matches) {
    film.autoplay = true;
    film.loop = true;
    void start();
  }
}
