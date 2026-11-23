// Native playback stays available if this enhancement cannot load.
const film = document.querySelector('.film-media video');
const play = document.querySelector('.film-play');
if (film && play) {
  play.hidden = false;
  play.addEventListener('click', async () => {
    try { await film.play(); } catch { play.hidden = false; }
  });
  film.addEventListener('play', () => { play.hidden = true; });
  film.addEventListener('ended', () => { play.hidden = false; });
}
