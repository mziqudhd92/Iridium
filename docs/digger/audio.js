// 8-bit Web Audio Sound Synthesizer for Digger Arcade
(function () {
  let audioCtx = null;
  let soundEnabled = false;

  function getAudioContext() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        audioCtx = new AudioContext();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playTone(freq, duration, type = 'square', gainVal = 0.08) {
    if (!soundEnabled) return;
    const ctx = getAudioContext();
    if (!ctx) return;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (_) {}
  }

  window.DiggerAudio = {
    toggle: function () {
      soundEnabled = !soundEnabled;
      if (soundEnabled) {
        getAudioContext();
        this.playGem();
      }
      return soundEnabled;
    },
    isEnabled: function () {
      return soundEnabled;
    },
    // Chomp sound (eating dirt)
    playChomp: function () {
      playTone(180, 0.06, 'triangle', 0.1);
      setTimeout(() => playTone(120, 0.07, 'square', 0.08), 50);
    },
    // Gem pickup sound (classic high chime)
    playGem: function () {
      playTone(523.25, 0.08, 'square', 0.07); // C5
      setTimeout(() => playTone(659.25, 0.08, 'square', 0.07), 70); // E5
      setTimeout(() => playTone(783.99, 0.12, 'square', 0.07), 140); // G5
      setTimeout(() => playTone(1046.5, 0.18, 'square', 0.09), 210); // C6
    },
    // Gold bag drop / break open
    playGold: function () {
      playTone(330, 0.09, 'sawtooth', 0.08);
      setTimeout(() => playTone(440, 0.09, 'square', 0.08), 80);
      setTimeout(() => playTone(660, 0.14, 'square', 0.1), 160);
    },
    // Button click / arcade blip
    playBlip: function () {
      playTone(880, 0.04, 'square', 0.06);
    },
    // Modal open / Sysop tty beep
    playTerminal: function () {
      playTone(440, 0.05, 'square', 0.06);
      setTimeout(() => playTone(880, 0.08, 'square', 0.06), 60);
    }
  };
})();
